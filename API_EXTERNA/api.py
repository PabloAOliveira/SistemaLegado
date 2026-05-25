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


DEFAULT_NO_AUTH_MESSAGE = 'Missing authentication token'
DEFAULT_NO_PERMISSION_MESSAGE = 'Invalid token or insufficient permissions'

SCHEMA_ERROR = '#/components/schemas/Error'


def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, X-API-Token, Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
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
            if not token:
                return make_response(jsonify({'detail': no_auth_message}), 401)
            if not is_authorized_token(token):
                return make_response(jsonify({'detail': no_permission_message}), 403)
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


def build_openapi_spec(server_url, no_auth_message, no_permission_message):
    return {
        'openapi': '3.0.3',
        'info': {
            'title': 'SGDI External Read API',
            'version': '1.0.0',
            'description': (
                'API externa apenas leitura para demandas e solicitantes (sem email). '
                'Requer token previamente cadastrado na tabela system_users com user_type="externo". '
                'Os tokens são armazenados como hash com salt; envie o token apenas via header.'
            ),
            'contact': {'name': 'Team SGDI'}
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
                    'responses': {
                        '200': {
                            'description': 'Lista de demandas',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'array',
                                        'items': {'$ref': '#/components/schemas/Demanda'}
                                    },
                                    'examples': {
                                        'exemplo': {
                                            'value': [
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
                                            ]
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
                    'responses': {
                        '200': {
                            'description': 'Lista de solicitantes',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'array',
                                        'items': {'$ref': '#/components/schemas/Solicitante'}
                                    },
                                    'examples': {
                                        'exemplo': {
                                            'value': [
                                                {
                                                    'id': 1,
                                                    'nome': 'Joao Silva',
                                                    'cargo': 'Analista',
                                                    'data_criacao': '2024-01-15 09:00:00'
                                                }
                                            ]
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

    no_authentication_message = DEFAULT_NO_AUTH_MESSAGE
    no_permission_message = DEFAULT_NO_PERMISSION_MESSAGE

    app_api.after_request(add_cors_headers)

    @app_api.route('/api/v1/demandas', methods=['GET'])
    @token_required(no_authentication_message, no_permission_message)
    def api_demandas():
        rows = fetch_all(
            'SELECT id, titulo, descricao, solicitante, prioridade, data_criacao, '
            'status, responsavel, prazo, data_conclusao FROM demandas'
        )
        return jsonify([serialize_demanda(row) for row in rows])

    @app_api.route('/api/v1/solicitantes', methods=['GET'])
    @token_required(no_authentication_message, no_permission_message)
    def api_solicitantes():
        rows = fetch_all('SELECT id, nome, cargo, data_criacao FROM requesters')
        return jsonify([serialize_solicitante(row) for row in rows])

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


if __name__ == '__main__':
    app = create_api_app()
    app.run(host=config.FLASK_HOST, port=int(config.FLASK_PORT) + 1, debug=False)
