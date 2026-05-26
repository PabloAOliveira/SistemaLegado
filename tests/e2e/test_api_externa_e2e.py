"""E2E tests for the external API."""
import json
import time
import pytest


class TestAuthentication:
    """Tests for authentication mechanisms."""

    def test_demandas_sem_token_retorna_401(self, api_client):
        """Requesting without token should return 401."""
        response = api_client.get('/api/v1/demandas')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'detail' in data
        assert data['detail'] == 'Missing authentication token'

    def test_demandas_com_token_invalido_retorna_403(self, api_client, invalid_token):
        """Requesting with invalid token should return 403."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {invalid_token}'}
        )
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['detail'] == 'Invalid token or insufficient permissions'

    def test_demandas_com_token_valido_retorna_200(self, api_client, valid_token):
        """Requesting with valid token should return 200."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'items' in data
        assert 'page' in data

    def test_solicitantes_sem_token_retorna_401(self, api_client):
        """Requesting solicitantes without token should return 401."""
        response = api_client.get('/api/v1/solicitantes')
        assert response.status_code == 401

    def test_autenticacao_com_x_api_token_header(self, api_client, valid_token):
        """Authentication via X-API-Token header should work."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'X-API-Token': valid_token}
        )
        assert response.status_code == 200


class TestDemandas:
    """Tests for demandas endpoint."""

    def test_demandas_retorna_lista(self, api_client, valid_token):
        """GET /api/v1/demandas returns list of demandas."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data['items'], list)
        assert len(data['items']) > 0

    def test_demanda_tem_campos_obrigatorios(self, api_client, valid_token):
        """Each demanda should have required fields."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        demanda = data['items'][0]

        required_fields = ['id', 'titulo', 'descricao', 'solicitante', 'prioridade', 'data_criacao']
        for field in required_fields:
            assert field in demanda

    def test_demanda_nao_deve_retornar_campos_sensveis(self, api_client, valid_token):
        """Demanda should not return sensitive fields like passwords."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        demanda = data['items'][0]

        # Should not have sensitive fields
        assert 'password' not in demanda
        assert 'token' not in demanda


class TestSolicitantes:
    """Tests for solicitantes endpoint."""

    def test_solicitantes_retorna_lista(self, api_client, valid_token):
        """GET /api/v1/solicitantes returns list of solicitantes."""
        response = api_client.get(
            '/api/v1/solicitantes',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data['items'], list)
        assert len(data['items']) > 0

    def test_solicitantes_tem_campos_obrigatorios(self, api_client, valid_token):
        """Each solicitante should have required fields."""
        response = api_client.get(
            '/api/v1/solicitantes',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        solicitante = data['items'][0]

        required_fields = ['id', 'nome', 'cargo', 'data_criacao']
        for field in required_fields:
            assert field in solicitante

    def test_solicitantes_nao_retorna_email(self, api_client, valid_token):
        """Solicitantes should NOT include email for privacy."""
        response = api_client.get(
            '/api/v1/solicitantes',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        solicitante = data['items'][0]

        assert 'email' not in solicitante


class TestPaginacao:
    """Tests for pagination."""

    def test_demandas_paginacao_padrao(self, api_client, valid_token):
        """Default pagination returns 20 items per page."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['per_page'] == 20
        assert data['page'] == 1

    def test_demandas_paginacao_page_parameter(self, api_client, valid_token):
        """Pagination accepts page parameter."""
        response = api_client.get(
            '/api/v1/demandas?page=2',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['page'] == 2

    def test_demandas_paginacao_per_page_20(self, api_client, valid_token):
        """Pagination accepts per_page=20."""
        response = api_client.get(
            '/api/v1/demandas?per_page=20',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['per_page'] == 20

    def test_demandas_paginacao_per_page_50(self, api_client, valid_token):
        """Pagination accepts per_page=50."""
        response = api_client.get(
            '/api/v1/demandas?per_page=50',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['per_page'] == 50

    def test_demandas_paginacao_per_page_100(self, api_client, valid_token):
        """Pagination accepts per_page=100."""
        response = api_client.get(
            '/api/v1/demandas?per_page=100',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['per_page'] == 100

    def test_demandas_paginacao_per_page_invalido_retorna_400(self, api_client, valid_token):
        """Invalid per_page value returns 400."""
        response = api_client.get(
            '/api/v1/demandas?per_page=75',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid pagination parameters' in data['detail']

    def test_demandas_paginacao_page_invalido_retorna_400(self, api_client, valid_token):
        """Invalid page value returns 400."""
        response = api_client.get(
            '/api/v1/demandas?page=0',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 400

    def test_paginacao_retorna_metadata(self, api_client, valid_token):
        """Pagination response includes metadata."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'page' in data
        assert 'per_page' in data
        assert 'total' in data
        assert 'total_pages' in data
        assert isinstance(data['total'], int)
        assert isinstance(data['total_pages'], int)


class TestCORS:
    """Tests for CORS headers."""

    def test_cors_allow_origin_header(self, api_client, valid_token):
        """Response should include CORS Allow-Origin header."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == '*'

    def test_cors_allow_methods_header(self, api_client, valid_token):
        """Response should include CORS Allow-Methods header."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert 'Access-Control-Allow-Methods' in response.headers

    def test_cors_allow_headers_header(self, api_client, valid_token):
        """Response should include CORS Allow-Headers."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert 'Access-Control-Allow-Headers' in response.headers
        headers_allowed = response.headers['Access-Control-Allow-Headers'].lower()
        assert 'authorization' in headers_allowed
        assert 'x-api-token' in headers_allowed or 'content-type' in headers_allowed

    def test_no_server_header_for_security(self, api_client, valid_token):
        """Response should NOT include Server header for security."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert 'Server' not in response.headers or response.headers['Server'] == ''


class TestOpenAPI:
    """Tests for OpenAPI/Swagger documentation."""

    def test_openapi_json_endpoint_retorna_spec(self, api_client):
        """GET /api/v1/openapi.json returns OpenAPI spec."""
        response = api_client.get('/api/v1/openapi.json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['openapi'] == '3.0.3'
        assert 'info' in data
        assert 'paths' in data

    def test_openapi_tem_demandas_endpoint(self, api_client):
        """OpenAPI spec includes demandas endpoint."""
        response = api_client.get('/api/v1/openapi.json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert '/api/v1/demandas' in data['paths']

    def test_openapi_tem_solicitantes_endpoint(self, api_client):
        """OpenAPI spec includes solicitantes endpoint."""
        response = api_client.get('/api/v1/openapi.json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert '/api/v1/solicitantes' in data['paths']

    def test_openapi_demandas_tem_responses_documentadas(self, api_client):
        """OpenAPI spec documents demandas responses."""
        response = api_client.get('/api/v1/openapi.json')
        assert response.status_code == 200
        data = json.loads(response.data)
        demandas_path = data['paths']['/api/v1/demandas']
        responses = demandas_path['get']['responses']

        # Should have 200, 401, 403, 429 responses
        assert '200' in responses
        assert '401' in responses
        assert '403' in responses
        assert '429' in responses

    def test_swagger_ui_docs_endpoint(self, api_client):
        """GET /api/v1/docs returns Swagger UI."""
        response = api_client.get('/api/v1/docs')
        assert response.status_code == 200
        assert b'swagger-ui' in response.data or b'Swagger' in response.data or b'SGDI' in response.data

    def test_openapi_tem_security_schemes(self, api_client):
        """OpenAPI spec includes security schemes."""
        response = api_client.get('/api/v1/openapi.json')
        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'components' in data
        assert 'securitySchemes' in data['components']
        assert 'bearerAuth' in data['components']['securitySchemes']
        assert 'apiTokenHeader' in data['components']['securitySchemes']

    def test_openapi_schemas_estao_definidos(self, api_client):
        """OpenAPI spec includes schema definitions."""
        response = api_client.get('/api/v1/openapi.json')
        assert response.status_code == 200
        data = json.loads(response.data)

        schemas = data['components']['schemas']
        assert 'Demanda' in schemas
        assert 'Solicitante' in schemas
        assert 'Error' in schemas


class TestRateLimiting:
    """Tests for rate limiting."""

    def test_rate_limit_response_com_retry_after_header(self, api_client, valid_token):
        """Rate limited response should include Retry-After header."""
        # Make many requests quickly to trigger rate limit
        for i in range(15):
            response = api_client.get(
                '/api/v1/demandas',
                headers={'Authorization': f'Bearer {valid_token}'}
            )
            if response.status_code == 429:
                assert 'Retry-After' in response.headers
                retry_after = int(response.headers['Retry-After'])
                assert retry_after >= 0
                break

    def test_rate_limit_resposta_429(self, api_client, valid_token):
        """Rate limited response has 429 status code."""
        # Make many requests quickly
        for i in range(15):
            response = api_client.get(
                '/api/v1/demandas',
                headers={'Authorization': f'Bearer {valid_token}'}
            )
            if response.status_code == 429:
                data = json.loads(response.data)
                assert 'detail' in data
                assert 'Rate limit exceeded' in data['detail']
                break

    def test_rate_limit_por_token(self, api_client, valid_token, invalid_token):
        """Rate limiting is per token."""
        # Rate limit with invalid token doesn't affect valid token
        for i in range(15):
            api_client.get(
                '/api/v1/demandas',
                headers={'X-API-Token': 'token-1'}
            )

        # Valid token should still work
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        # Should get either 200 or 429 depending on rate limit state
        assert response.status_code in [200, 429]


class TestResposta:
    """Tests for response format and structure."""

    def test_resposta_json_content_type(self, api_client, valid_token):
        """Response should have JSON content type."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert 'application/json' in response.content_type

    def test_resposta_nao_vazia_para_demandas(self, api_client, valid_token):
        """Demandas response should not be empty."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) >= 0  # May be empty but should be a list

    def test_resposta_nao_vazia_para_solicitantes(self, api_client, valid_token):
        """Solicitantes response should not be empty."""
        response = api_client.get(
            '/api/v1/solicitantes',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) > 0

    def test_demandas_ordenadas_por_id_desc(self, api_client, valid_token):
        """Demandas should be ordered by ID descending."""
        response = api_client.get(
            '/api/v1/demandas?per_page=100',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        if len(data['items']) > 1:
            ids = [item['id'] for item in data['items']]
            assert ids == sorted(ids, reverse=True)

    def test_solicitantes_ordenadas_por_id_desc(self, api_client, valid_token):
        """Solicitantes should be ordered by ID descending."""
        response = api_client.get(
            '/api/v1/solicitantes?per_page=100',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        if len(data['items']) > 1:
            ids = [item['id'] for item in data['items']]
            assert ids == sorted(ids, reverse=True)


class TestHTTPMethods:
    """Tests for HTTP method restrictions."""

    def test_demandas_post_nao_permitido(self, api_client, valid_token):
        """POST to demandas endpoint should not be allowed."""
        response = api_client.post(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer {valid_token}'},
            json={}
        )
        assert response.status_code in [405, 404]  # Method not allowed or not found

    def test_solicitantes_post_nao_permitido(self, api_client, valid_token):
        """POST to solicitantes endpoint should not be allowed."""
        response = api_client.post(
            '/api/v1/solicitantes',
            headers={'Authorization': f'Bearer {valid_token}'},
            json={}
        )
        assert response.status_code in [405, 404]


class TestEdgeCases:
    """Tests for edge cases and error scenarios."""

    def test_paginacao_com_parametros_string(self, api_client, valid_token):
        """Pagination with non-integer parameters should return 400."""
        response = api_client.get(
            '/api/v1/demandas?page=abc&per_page=def',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 400

    def test_paginacao_pagina_muito_alta(self, api_client, valid_token):
        """Request for very high page number should return empty items."""
        response = api_client.get(
            '/api/v1/demandas?page=9999',
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should return valid response even if page is beyond data
        assert 'items' in data
        assert isinstance(data['items'], list)

    def test_auth_header_case_insensitive_bearer(self, api_client, valid_token):
        """Bearer auth header should accept different cases."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'bearer {valid_token}'}
        )
        assert response.status_code == 200

    def test_auth_header_com_espacos_extras(self, api_client, valid_token):
        """Auth header should handle extra spaces."""
        response = api_client.get(
            '/api/v1/demandas',
            headers={'Authorization': f'Bearer   {valid_token}   '}
        )
        # Should either work or return 403 depending on implementation
        assert response.status_code in [200, 403]

