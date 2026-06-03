"""External read-only API for demandas and solicitantes.
This API is self-contained and can be run independently of the main app.
It requires a valid token stored in the `system_users` table with user_type = 'externo'.
"""
from flask import Flask, jsonify, request, make_response, render_template_string
from functools import wraps
from db import fetch_all
import config
import hashlib
import hmac
import math
import time
import uuid
import logging
from collections import deque
from threading import Lock
from werkzeug.exceptions import HTTPException
from werkzeug.serving import make_server, BaseWSGIServer
from services.logging import setup_logging, get_logger


# Disable Werkzeug server header globally for this process.
BaseWSGIServer.server_version = ''
BaseWSGIServer.sys_version = ''

class QuietWSGIServer(BaseWSGIServer):
    server_version = ''
    sys_version = ''

DEFAULT_NO_AUTH_MESSAGE = 'Missing authentication token'
DEFAULT_NO_PERMISSION_MESSAGE = 'Invalid token or insufficient permissions'

SCHEMA_ERROR = '#/components/schemas/Error'
RATE_LIMIT_RPS = 10
RATE_LIMIT_RPM = 600

_rate_limit_lock = Lock()
_rate_limit_state = {}
logger = get_logger(__name__)


def get_rate_limit_key(req):
    token = get_token_from_request(req)
    if token:
        return f"token:{token}"
    return f"ip:{req.remote_addr or 'unknown'}"


def rate_limit_response(retry_after_seconds):
    response = make_response(jsonify({'detail': 'Rate limit exceeded'}), 429)
    response.headers['Retry-After'] = str(int(retry_after_seconds))
    logger.warning(
        'Rate limit exceeded',
        extra={
            'request_id': getattr(request, 'request_id', 'N/A'),
            'remote_addr': request.remote_addr,
            'retry_after': int(retry_after_seconds)
        }
    )
    return response


def check_rate_limit(req):
    key = get_rate_limit_key(req)
    now = time.time()
    with _rate_limit_lock:
        state = _rate_limit_state.get(key)
        if state is None:
            state = {
                'per_second': deque(),
                'per_minute': deque(),
            }
            _rate_limit_state[key] = state

        per_second = state['per_second']
        per_minute = state['per_minute']

        while per_second and now - per_second[0] >= 1:
            per_second.popleft()
        while per_minute and now - per_minute[0] >= 60:
            per_minute.popleft()

        if len(per_second) >= RATE_LIMIT_RPS:
            retry_after = max(0.0, 1 - (now - per_second[0]))
            return rate_limit_response(retry_after)
        if len(per_minute) >= RATE_LIMIT_RPM:
            retry_after = max(0.0, 60 - (now - per_minute[0]))
            return rate_limit_response(retry_after)

        per_second.append(now)
        per_minute.append(now)
    return None


def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, X-API-Token, Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers.pop('Server', None)
    return response


def get_token_from_request(req):
    auth = req.headers.get('Authorization')
    if auth and auth.lower().startswith('bearer '):
        return auth.split(None, 1)[1].strip()
    return req.headers.get('X-API-Token')


def hash_token(token, salt_hex, iterations=100_000):
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac('sha256', token.encode('utf-8'), salt, iterations)
    return digest.hex()


def is_authorized_token(token):
    rows = fetch_all(
        "SELECT token, token_salt, user_type FROM system_users WHERE user_type = 'externo'"
    )
    for token_hash, token_salt, user_type in rows:
        if not token_hash or not token_salt:
            continue
        computed = hash_token(token, token_salt)
        if hmac.compare_digest(computed, token_hash):
            return True
    return False


def token_required(no_auth_message=DEFAULT_NO_AUTH_MESSAGE,
                  no_permission_message=DEFAULT_NO_PERMISSION_MESSAGE):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_from_request(request)
            request_id = getattr(request, 'request_id', 'N/A')
            
            if not token:
                logger.warning(
                    'Authentication failed: missing token',
                    extra={'request_id': request_id, 'remote_addr': request.remote_addr}
                )
                return make_response(jsonify({'detail': no_auth_message}), 401)
            
            if not is_authorized_token(token):
                logger.warning(
                    'Authentication failed: invalid token',
                    extra={'request_id': request_id, 'remote_addr': request.remote_addr}
                )
                return make_response(jsonify({'detail': no_permission_message}), 403)
            
            logger.info(
                'Authentication successful',
                extra={'request_id': request_id, 'path': request.path}
            )
            return f(*args, **kwargs)
        return decorated
    return decorator


def serialize_demanda(row):
    return {
        'id': row[0],
        'titulo': row[1],
        'descricao': row[2],
        'solicitante': row[3],
        'prioridade': row[4],
        'data_criacao': row[5],
        'status': row[6] if len(row) > 6 else None,
        'responsavel': row[7] if len(row) > 7 else None,
        'prazo': row[8] if len(row) > 8 else None,
        'data_conclusao': row[9] if len(row) > 9 else None,
    }


def serialize_solicitante(row):
    return {
        'id': row[0],
        'nome': row[1],
        'cargo': row[2],
        'data_criacao': row[3],
    }


def get_pagination_params(req, default_per_page=20):
    page_raw = req.args.get('page', '1')
    per_page_raw = req.args.get('per_page', str(default_per_page))
    try:
        page = int(page_raw)
        per_page = int(per_page_raw)
    except ValueError:
        return None, None, make_response(jsonify({'detail': 'Invalid pagination parameters'}), 400)
    if page < 1 or per_page not in (20, 50, 100):
        return None, None, make_response(jsonify({'detail': 'Invalid pagination parameters'}), 400)
    return page, per_page, None


def _build_where_clause(conditions):
    """Helper to join conditions into a WHERE clause and return tuple(params).

    `conditions` is a list of tuples (expr, value) where expr is a SQL fragment
    like "titulo LIKE ?" and value is the parameter value.
    """
    if not conditions:
        return '', ()
    exprs = [c[0] for c in conditions]
    params = [c[1] for c in conditions]
    return 'WHERE ' + ' AND '.join(exprs), tuple(params)


def build_demandas_where_clause(req):
    conditions = []

    # Exact id filter
    id_raw = req.args.get('id')
    if id_raw:
        try:
            _id = int(id_raw)
            conditions.append(('id = ?', _id))
        except ValueError:
            pass

    # Text fields — use LIKE for partial matches
    for field in ('titulo', 'descricao', 'solicitante', 'prioridade', 'status', 'responsavel'):
        v = req.args.get(field)
        if v:
            conditions.append((f"{field} LIKE ?", f"%{v}%"))

    # Date ranges
    if req.args.get('data_criacao_from'):
        conditions.append(("data_criacao >= ?", req.args.get('data_criacao_from')))
    if req.args.get('data_criacao_to'):
        conditions.append(("data_criacao <= ?", req.args.get('data_criacao_to')))
    if req.args.get('data_conclusao_from'):
        conditions.append(("data_conclusao >= ?", req.args.get('data_conclusao_from')))
    if req.args.get('data_conclusao_to'):
        conditions.append(("data_conclusao <= ?", req.args.get('data_conclusao_to')))
    if req.args.get('prazo_from'):
        conditions.append(("prazo >= ?", req.args.get('prazo_from')))
    if req.args.get('prazo_to'):
        conditions.append(("prazo <= ?", req.args.get('prazo_to')))

    return _build_where_clause(conditions)


def build_requesters_where_clause(req):
    conditions = []
    id_raw = req.args.get('id')
    if id_raw:
        try:
            _id = int(id_raw)
            conditions.append(('id = ?', _id))
        except ValueError:
            pass

    # nome and cargo partial matches
    if req.args.get('nome'):
        conditions.append(("nome LIKE ?", f"%{req.args.get('nome')}%"))
    if req.args.get('cargo'):
        conditions.append(("cargo LIKE ?", f"%{req.args.get('cargo')}%"))

    # date ranges for data_criacao
    if req.args.get('data_criacao_from'):
        conditions.append(("data_criacao >= ?", req.args.get('data_criacao_from')))
    if req.args.get('data_criacao_to'):
        conditions.append(("data_criacao <= ?", req.args.get('data_criacao_to')))

    return _build_where_clause(conditions)


def build_paginated_response(items, page, per_page, total):
    total_pages = max(1, math.ceil(total / per_page)) if total else 1
    return {
        'items': items,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages
    }


def build_openapi_spec(server_url, no_auth_message, no_permission_message):
    return {
        'openapi': '3.0.3',
        'info': {
            'title': 'SGDI External Read API',
            'version': '1.0.0',
            'description': (
                'API externa apenas leitura para demandas e solicitantes. '
                'Requer token previamente cadastrado na tabela system_users com user_type="externo". '
                'Os tokens são envie o token apenas via header. '
                'Limite de requisições por usuário: 600 por minuto.'

            ),
            'contact': {'name': 'SUTITA'}
        },
        'servers': [
            {'url': server_url, 'description': 'External API server'},
        ],
        'tags': [
            {'name': 'demandas', 'description': 'Consulta de demandas (somente leitura).'},
            {'name': 'solicitantes', 'description': 'Consulta de solicitantes (somente leitura).'},
        ],
        'paths': {
            '/api/v1/demandas': {
                'get': {
                    'summary': 'Listar demandas',
                    'description': 'Retorna todas as demandas com campos de status e prazos quando existentes.',
                    'tags': ['demandas'],
                    'security': [
                        {'bearerAuth': []},
                        {'apiTokenHeader': []}
                    ],
                    'parameters': [
                        {'name': 'page', 'in': 'query', 'required': False, 'schema': {'type': 'integer', 'minimum': 1, 'default': 1}, 'description': 'Página atual (inicia em 1).'},
                        {'name': 'per_page', 'in': 'query', 'required': False, 'schema': {'type': 'integer', 'enum': [20, 50, 100], 'default': 20}, 'description': 'Quantidade de itens por página.'},
                        {'name': 'id', 'in': 'query', 'required': False, 'schema': {'type': 'integer'}, 'description': 'Filtrar por id exato'},
                        {'name': 'titulo', 'in': 'query', 'required': False, 'schema': {'type': 'string'}, 'description': 'Busca parcial no título'},
                        {'name': 'descricao', 'in': 'query', 'required': False, 'schema': {'type': 'string'}, 'description': 'Busca parcial na descrição'},
                        {'name': 'solicitante', 'in': 'query', 'required': False, 'schema': {'type': 'string'}, 'description': 'Busca parcial pelo nome do solicitante'},
                        {'name': 'prioridade', 'in': 'query', 'required': False, 'schema': {'type': 'string'}, 'description': 'Filtrar por prioridade (baixa, media, alta, critica)'},
                        {'name': 'status', 'in': 'query', 'required': False, 'schema': {'type': 'string'}, 'description': 'Filtrar por status (aberta, concluida, cancelada, etc.)'},
                        {'name': 'responsavel', 'in': 'query', 'required': False, 'schema': {'type': 'string'}, 'description': 'Busca parcial pelo responsável'},
                        {'name': 'data_criacao_from', 'in': 'query', 'required': False, 'schema': {'type': 'string', 'format': 'date-time'}, 'description': 'Data de criação mínima (inclusive) - formato YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS'},
                        {'name': 'data_criacao_to', 'in': 'query', 'required': False, 'schema': {'type': 'string', 'format': 'date-time'}, 'description': 'Data de criação máxima (inclusive)'},
                        {'name': 'data_conclusao_from', 'in': 'query', 'required': False, 'schema': {'type': 'string', 'format': 'date-time'}, 'description': 'Data de conclusão mínima (inclusive)'},
                        {'name': 'data_conclusao_to', 'in': 'query', 'required': False, 'schema': {'type': 'string', 'format': 'date-time'}, 'description': 'Data de conclusão máxima (inclusive)'},
                        {'name': 'prazo_from', 'in': 'query', 'required': False, 'schema': {'type': 'string', 'format': 'date'}, 'description': 'Prazo mínimo (inclusive)'},
                        {'name': 'prazo_to', 'in': 'query', 'required': False, 'schema': {'type': 'string', 'format': 'date'}, 'description': 'Prazo máximo (inclusive)'}
                    ],
                    'responses': {
                        '200': {
                            'description': 'Lista de demandas (paginada)',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/PaginatedDemandas'},
                                    'examples': {
                                        'exemplo': {
                                            'value': {
                                                'items': [
                                                    {
                                                        'id': 1,
                                                        'titulo': 'Corrigir bug no login',
                                                        'descricao': 'Usuários não conseguem fazer login',
                                                        'solicitante': 'Joao Silva',
                                                        'prioridade': 'alta',
                                                        'data_criacao': '2024-01-15 10:30:00',
                                                        'status': 'aberta',
                                                        'responsavel': 'Tech Team',
                                                        'prazo': '2024-01-22',
                                                        'data_conclusao': None
                                                    }
                                                ],
                                                'page': 1,
                                                'per_page': 20,
                                                'total': 1,
                                                'total_pages': 1
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        '401': {
                            'description': no_auth_message,
                            'content': {'application/json': {'schema': {'$ref': SCHEMA_ERROR}}}
                        },
                        '403': {
                            'description': no_permission_message,
                            'content': {'application/json': {'schema': {'$ref': SCHEMA_ERROR}}}
                        },
                        '429': {
                            'description': 'Rate limit exceeded',
                            'headers': {
                                'Retry-After': {
                                    'schema': {'type': 'integer'},
                                    'description': 'Segundos até a próxima requisição permitida.'
                                }
                            },
                            'content': {'application/json': {'schema': {'$ref': SCHEMA_ERROR}}}
                        },
                    }
                }
            },
            '/api/v1/solicitantes': {
                'get': {
                    'summary': 'Listar solicitantes (sem email)',
                    'description': 'Retorna solicitantes sem o campo de email por privacidade.',
                    'tags': ['solicitantes'],
                    'security': [
                        {'bearerAuth': []},
                        {'apiTokenHeader': []}
                    ],
                    'parameters': [
                        {'name': 'page', 'in': 'query', 'required': False, 'schema': {'type': 'integer', 'minimum': 1, 'default': 1}, 'description': 'Página atual (inicia em 1).'},
                        {'name': 'per_page', 'in': 'query', 'required': False, 'schema': {'type': 'integer', 'enum': [20, 50, 100], 'default': 20}, 'description': 'Quantidade de itens por página.'},
                        {'name': 'id', 'in': 'query', 'required': False, 'schema': {'type': 'integer'}, 'description': 'Filtrar por id exato'},
                        {'name': 'nome', 'in': 'query', 'required': False, 'schema': {'type': 'string'}, 'description': 'Busca parcial por nome'},
                        {'name': 'cargo', 'in': 'query', 'required': False, 'schema': {'type': 'string'}, 'description': 'Busca parcial por cargo'},
                        {'name': 'data_criacao_from', 'in': 'query', 'required': False, 'schema': {'type': 'string', 'format': 'date-time'}, 'description': 'Data de criação mínima (inclusive)'},
                        {'name': 'data_criacao_to', 'in': 'query', 'required': False, 'schema': {'type': 'string', 'format': 'date-time'}, 'description': 'Data de criação máxima (inclusive)'}
                    ],
                    'responses': {
                        '200': {
                            'description': 'Lista de solicitantes (paginada)',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/PaginatedSolicitantes'},
                                    'examples': {
                                        'exemplo': {
                                            'value': {
                                                'items': [
                                                    {
                                                        'id': 1,
                                                        'nome': 'Joao Silva',
                                                        'cargo': 'Analista',
                                                        'data_criacao': '2024-01-15 09:00:00'
                                                    }
                                                ],
                                                'page': 1,
                                                'per_page': 20,
                                                'total': 1,
                                                'total_pages': 1
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        '401': {
                            'description': no_auth_message,
                            'content': {'application/json': {'schema': {'$ref': SCHEMA_ERROR}}}
                        },
                        '403': {
                            'description': no_permission_message,
                            'content': {'application/json': {'schema': {'$ref': SCHEMA_ERROR}}}
                        },
                        '429': {
                            'description': 'Rate limit exceeded',
                            'headers': {
                                'Retry-After': {
                                    'schema': {'type': 'integer'},
                                    'description': 'Segundos até a próxima requisição permitida.'
                                }
                            },
                            'content': {'application/json': {'schema': {'$ref': SCHEMA_ERROR}}}
                        },
                    }
                }
            }
        },
        'components': {
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'Token'
                },
                'apiTokenHeader': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'X-API-Token'
                }
            },
            'schemas': {
                'Demanda': {
                    'type': 'object',
                    'required': ['id', 'titulo', 'descricao', 'solicitante', 'prioridade', 'data_criacao'],
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'titulo': {'type': 'string', 'example': 'Corrigir bug no login'},
                        'descricao': {'type': 'string', 'example': 'Usuários não conseguem fazer login'},
                        'solicitante': {'type': 'string', 'example': 'Joao Silva'},
                        'prioridade': {
                            'type': 'string',
                            'example': 'alta',
                            'description': 'Valores típicos: baixa, media, alta, critica.'
                        },
                        'data_criacao': {
                            'type': 'string',
                            'format': 'date-time',
                            'example': '2024-01-15 10:30:00'
                        },
                        'status': {'type': ['string', 'null'], 'example': 'aberta'},
                        'responsavel': {'type': ['string', 'null'], 'example': 'Tech Team'},
                        'prazo': {'type': ['string', 'null'], 'example': '2024-01-22'},
                        'data_conclusao': {'type': ['string', 'null'], 'example': None},
                    }
                },
                'Solicitante': {
                    'type': 'object',
                    'required': ['id', 'nome', 'cargo', 'data_criacao'],
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'nome': {'type': 'string', 'example': 'Joao Silva'},
                        'cargo': {'type': 'string', 'example': 'Analista'},
                        'data_criacao': {
                            'type': 'string',
                            'format': 'date-time',
                            'example': '2024-01-15 09:00:00'
                        },
                    }
                },
                'Error': {
                    'type': 'object',
                    'properties': {
                        'detail': {'type': 'string', 'example': 'Missing authentication token'}
                    }
                },
                'PaginatedDemandas': {
                    'type': 'object',
                    'properties': {
                        'items': {
                            'type': 'array',
                            'items': {'$ref': '#/components/schemas/Demanda'}
                        },
                        'page': {'type': 'integer', 'example': 1},
                        'per_page': {'type': 'integer', 'example': 20},
                        'total': {'type': 'integer', 'example': 120},
                        'total_pages': {'type': 'integer', 'example': 6}
                    }
                },
                'PaginatedSolicitantes': {
                    'type': 'object',
                    'properties': {
                        'items': {
                            'type': 'array',
                            'items': {'$ref': '#/components/schemas/Solicitante'}
                        },
                        'page': {'type': 'integer', 'example': 1},
                        'per_page': {'type': 'integer', 'example': 20},
                        'total': {'type': 'integer', 'example': 120},
                        'total_pages': {'type': 'integer', 'example': 6}
                    }
                }
            }
        }
    }


def build_swagger_html():
    return """
    <!doctype html>
    <html>
      <head>
        <title>SGDI External API Docs</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
          window.onload = () => {
            SwaggerUIBundle({
              url: '/api/v1/openapi.json',
              dom_id: '#swagger-ui',
              presets: [SwaggerUIBundle.presets.apis],
              layout: 'BaseLayout',
              persistAuthorization: true
            });
          };
        </script>
      </body>
    </html>
    """


def create_api_app():
    app_api = Flask(__name__)
    app_api.config['JSON_SORT_KEYS'] = False

    # Setup logging
    setup_logging(app_api, loki_enabled=True)
    app_logger = get_logger('sgdi.api')

    no_authentication_message = DEFAULT_NO_AUTH_MESSAGE
    no_permission_message = DEFAULT_NO_PERMISSION_MESSAGE

    app_api.after_request(add_cors_headers)

    @app_api.before_request
    def setup_request_context():
        """Setup request_id and logging context."""
        request.request_id = str(uuid.uuid4())
        app_logger.info(
            f'Incoming {request.method} {request.path}',
            extra={'request_id': request.request_id, 'remote_addr': request.remote_addr}
        )
        limited = check_rate_limit(request)
        if limited is not None:
            return limited
        return None

    @app_api.after_request
    def log_response(response):
        """Log response status."""
        request_id = getattr(request, 'request_id', 'N/A')
        app_logger.info(
            f'Response {response.status_code} {request.method} {request.path}',
            extra={'request_id': request_id, 'status_code': response.status_code}
        )
        return response

    @app_api.errorhandler(Exception)
    def handle_exception(error):
        """Log exceptions."""
        if isinstance(error, HTTPException):
            return error

        request_id = getattr(request, 'request_id', 'N/A')
        app_logger.error(
            f'Exception: {str(error)}',
            extra={'request_id': request_id, 'error_type': type(error).__name__},
            exc_info=True
        )
        return jsonify({'detail': 'Internal server error'}), 500

    @app_api.route('/api/v1/demandas', methods=['GET'])
    @token_required(no_authentication_message, no_permission_message)
    def api_demandas():
        request_id = getattr(request, 'request_id', 'N/A')
        try:
            page, per_page, error = get_pagination_params(request)
            if error:
                return error
            offset = (page - 1) * per_page
            where_clause, where_params = build_demandas_where_clause(request)
            total_q = 'SELECT COUNT(1) FROM demandas ' + where_clause
            total = fetch_all(total_q, where_params)[0][0]

            rows_q = (
                'SELECT id, titulo, descricao, solicitante, prioridade, data_criacao, '
                'status, responsavel, prazo, data_conclusao FROM demandas '
                + where_clause + ' ORDER BY id DESC LIMIT ? OFFSET ?'
            )
            params = list(where_params) + [per_page, offset]
            rows = fetch_all(rows_q, tuple(params))
            items = [serialize_demanda(row) for row in rows]
            
            result = build_paginated_response(items, page, per_page, total)
            app_logger.info(
                f'Demandas retrieved: {total} total, page {page}',
                extra={'request_id': request_id, 'total': total, 'page': page}
            )
            return jsonify(result)
        except Exception as e:
            app_logger.error(
                f'Error in api_demandas: {str(e)}',
                extra={'request_id': request_id},
                exc_info=True
            )
            raise

    @app_api.route('/api/v1/solicitantes', methods=['GET'])
    @token_required(no_authentication_message, no_permission_message)
    def api_solicitantes():
        request_id = getattr(request, 'request_id', 'N/A')
        try:
            page, per_page, error = get_pagination_params(request)
            if error:
                return error
            offset = (page - 1) * per_page
            where_clause, where_params = build_requesters_where_clause(request)
            total_q = 'SELECT COUNT(1) FROM requesters ' + where_clause
            total = fetch_all(total_q, where_params)[0][0]

            rows_q = (
                'SELECT id, nome, cargo, data_criacao FROM requesters '
                + where_clause + ' ORDER BY id DESC LIMIT ? OFFSET ?'
            )
            params = list(where_params) + [per_page, offset]
            rows = fetch_all(rows_q, tuple(params))
            items = [serialize_solicitante(row) for row in rows]
            
            result = build_paginated_response(items, page, per_page, total)
            app_logger.info(
                f'Solicitantes retrieved: {total} total, page {page}',
                extra={'request_id': request_id, 'total': total, 'page': page}
            )
            return jsonify(result)
        except Exception as e:
            app_logger.error(
                f'Error in api_solicitantes: {str(e)}',
                extra={'request_id': request_id},
                exc_info=True
            )
            raise

    @app_api.route('/api/v1/openapi.json', methods=['GET'])
    def openapi_spec():
        server_url = request.host_url.rstrip('/')
        spec = build_openapi_spec(
            server_url,
            no_authentication_message,
            no_permission_message
        )
        return jsonify(spec)

    @app_api.route('/api/v1/docs', methods=['GET'])
    def docs():
        return render_template_string(build_swagger_html())

    return app_api


def run_api_server(app):
    server = make_server(config.FLASK_HOST, int(config.FLASK_PORT) + 1, app, QuietWSGIServer)
    server.serve_forever()


if __name__ == '__main__':
    app = create_api_app()
    run_api_server(app)
