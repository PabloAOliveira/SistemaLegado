# Testes da API Externa - Documentação

## Visão Geral

Este arquivo documenta os testes end-to-end (E2E) criados para a API Externa (`API_EXTERNA/api.py`). A suite de testes cobre todos os aspectos críticos da API, incluindo autenticação, paginação, rate limiting, CORS e documentação OpenAPI.

## Estrutura dos Testes

### Arquivo Principal
- **`tests/e2e/test_api_externa_e2e.py`**: Suite completa com 44 testes organizados em 8 classes

### Fixtures Suportadas (em `tests/conftest.py`)
- `api_client`: Cliente Flask para testar a API externa
- `valid_token`: Token válido para autenticação ("test-external-token-valid")
- `invalid_token`: Token inválido para teste de rejeição
- `db_path`: Banco de dados isolado com tabelas pré-carregadas

## Testes por Categoria

### 1. TestAuthentication (5 testes)
Valida mecanismos de autenticação:
- `test_demandas_sem_token_retorna_401`: Sem token → 401
- `test_demandas_com_token_invalido_retorna_403`: Token inválido → 403
- `test_demandas_com_token_valido_retorna_200`: Token válido → 200
- `test_solicitantes_sem_token_retorna_401`: Sem token no outro endpoint
- `test_autenticacao_com_x_api_token_header`: Suporte a header `X-API-Token`

**Cobertura**: Autenticação Bearer, X-API-Token, rejeição de não-autenticados e token inválido

### 2. TestDemandas (3 testes)
Valida o endpoint `/api/v1/demandas`:
- `test_demandas_retorna_lista`: Retorna lista não vazia
- `test_demanda_tem_campos_obrigatorios`: Todos os campos necessários estão presentes
- `test_demanda_nao_deve_retornar_campos_sensveis`: Sem campos sensíveis como password

**Cobertura**: Estrutura de dados, segurança de campos

### 3. TestSolicitantes (3 testes)
Valida o endpoint `/api/v1/solicitantes`:
- `test_solicitantes_retorna_lista`: Retorna lista não vazia
- `test_solicitantes_tem_campos_obrigatorios`: Campos obrigatórios presentes
- `test_solicitantes_nao_retorna_email`: **Email não é exposto** (privacidade)

**Cobertura**: Privacidade de dados, campos esperados

### 4. TestPaginacao (8 testes)
Valida paginação (20, 50, 100 itens/página):
- `test_demandas_paginacao_padrao`: Padrão é 20 itens/página
- `test_demandas_paginacao_page_parameter`: Suporte a parâmetro `page`
- `test_demandas_paginacao_per_page_*`: Suporte a per_page=20, 50, 100
- `test_demandas_paginacao_per_page_invalido_retorna_400`: Valores inválidos → 400
- `test_demandas_paginacao_page_invalido_retorna_400`: Página inválida (0 ou negativa) → 400
- `test_paginacao_retorna_metadata`: Resposta inclui `page`, `per_page`, `total`, `total_pages`

**Cobertura**: Validação de parâmetros, metadados paginados

### 5. TestCORS (4 testes)
Valida headers CORS para integração frontend:
- `test_cors_allow_origin_header`: Header `Access-Control-Allow-Origin: *`
- `test_cors_allow_methods_header`: Header `Access-Control-Allow-Methods`
- `test_cors_allow_headers_header`: Header inclui Authorization e X-API-Token
- `test_no_server_header_for_security`: **Sem Server header** (segurança)

**Cobertura**: Compatibilidade CORS, ocultação de versão do servidor

### 6. TestOpenAPI (7 testes)
Valida documentação Swagger/OpenAPI 3.0:
- `test_openapi_json_endpoint_retorna_spec`: Endpoint `/api/v1/openapi.json` funciona
- `test_openapi_tem_demandas_endpoint`: Swagger documenta endpoint `/demandas`
- `test_openapi_tem_solicitantes_endpoint`: Swagger documenta endpoint `/solicitantes`
- `test_openapi_demandas_tem_responses_documentadas`: Respostas 200, 401, 403, 429 documentadas
- `test_swagger_ui_docs_endpoint`: UI Swagger em `/api/v1/docs` acessível
- `test_openapi_tem_security_schemes`: Security schemes (Bearer, API Token) definidos
- `test_openapi_schemas_estao_definidos`: Schemas Demanda, Solicitante, Error presentes

**Cobertura**: Documentação profissional, completude OpenAPI

### 7. TestRateLimiting (3 testes)
Valida rate limiting (10 req/seg, 600 req/min):
- `test_rate_limit_response_com_retry_after_header`: Header `Retry-After` presente em 429
- `test_rate_limit_resposta_429`: Rate limit dispara com status 429
- `test_rate_limit_por_token`: Rate limit é por token (isolado por usuário)

**Cobertura**: Proteção contra abuso, retentativas

### 8. TestResposta (5 testes)
Valida formato e estrutura de respostas:
- `test_resposta_json_content_type`: Content-Type é `application/json`
- `test_resposta_nao_vazia_para_demandas`: Resposta de demandas é válida
- `test_resposta_nao_vazia_para_solicitantes`: Resposta de solicitantes com dados
- `test_demandas_ordenadas_por_id_desc`: Demandas ordenadas ID descendente
- `test_solicitantes_ordenadas_por_id_desc`: Solicitantes ordenadas ID descendente

**Cobertura**: Formato JSON, ordenação, completude

### 9. TestHTTPMethods (2 testes)
Valida restrição de métodos HTTP:
- `test_demandas_post_nao_permitido`: POST não permitido em demandas
- `test_solicitantes_post_nao_permitido`: POST não permitido em solicitantes

**Cobertura**: API read-only (GET apenas)

### 10. TestEdgeCases (4 testes)
Valida casos extremos:
- `test_paginacao_com_parametros_string`: Parâmetros string → 400
- `test_paginacao_pagina_muito_alta`: Página muito alta → resposta valid
- `test_auth_header_case_insensitive_bearer`: "bearer" (minúsculo) funciona
- `test_auth_header_com_espacos_extras`: Espaços extras são tratados

**Cobertura**: Robustez, tolerância

## Rodando os Testes

### Todos os testes da API Externa
```bash
pytest tests/e2e/test_api_externa_e2e.py -v
```

### Testes de uma categoria específica
```bash
pytest tests/e2e/test_api_externa_e2e.py::TestAuthentication -v
pytest tests/e2e/test_api_externa_e2e.py::TestPaginacao -v
pytest tests/e2e/test_api_externa_e2e.py::TestRateLimiting -v
```

### Teste específico
```bash
pytest tests/e2e/test_api_externa_e2e.py::TestAuthentication::test_demandas_com_token_valido_retorna_200 -v
```

### Com cobertura de código
```bash
pytest tests/e2e/test_api_externa_e2e.py --cov=API_EXTERNA --cov-report=html
```

## Fixtures Utilizadas

### `api_client`
Cliente Flask **isolado** para testar a API externa. Usa banco de dados temporário (`tmp_path`) para não afetar dados reais.

```python
@pytest.fixture
def api_client(db_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Redireciona conexões SQLite para banco isolado
    # Cria instância da API externa
    # Retorna cliente test_client
```

### `valid_token` e `invalid_token`
Tokens para testes de autenticação:
- **valid_token**: `"test-external-token-valid"` (armazenado com hash no banco de testes)
- **invalid_token**: `"invalid-token-xyz"` (nunca é aceito)

### `db_path`
Banco SQLite isolado com:
- Tabela `demandas`: 2 demandas de exemplo
- Tabela `requesters`: 5 solicitantes de exemplo
- Tabela `system_users`: Usuário externo com token válido
- Tabela `comentarios`: 1 comentário de exemplo

## Dados de Teste

### Demandas
| ID | Título | Status | Responsável |
|----|--------|--------|-------------|
| 1 | Corrigir bug no login | aberta | Tech Team |
| 2 | Implementar relatório de vendas | concluida | Tech Team |

### Solicitantes (sem email na API)
| ID | Nome | Cargo |
|----|------|-------|
| 1 | Joao Silva | Analista |
| 2 | Maria Santos | Coordenadora |
| 3 | Tech Team | Equipe Tecnica |
| 4 | Equipe Suporte | Suporte |
| 5 | Time Produto | Produto |

### Usuário Externo
- **username**: external_api_client
- **user_type**: externo
- **token**: test-external-token-valid (hash PBKDF2 com salt)

## Resultados

✅ **44 testes passando** em ~5.2 segundos

Cobertura:
- **Autenticação**: 5 testes
- **Endpoints**: 6 testes
- **Paginação**: 8 testes
- **CORS**: 4 testes
- **OpenAPI**: 7 testes
- **Rate Limiting**: 3 testes
- **Respostas**: 5 testes
- **HTTP Methods**: 2 testes
- **Edge Cases**: 4 testes

## Notas Importantes

### Segurança
1. ✅ Tokens enviados apenas via headers (não em URL)
2. ✅ Tokens armazenados com hash PBKDF2 + salt
3. ✅ Email de solicitantes não exposto
4. ✅ Sem header `Server` (versão do Werkzeug)
5. ✅ Rate limiting por token para proteção contra DDoS

### Performance
- Rate limit: **10 req/segundo + 600 req/minuto**
- Implementado com sliding window em memória (O(1) amortizado)
- Thread-safe com Lock

### Compatibilidade
- OpenAPI 3.0.3 (Swagger profissional)
- CORS para clientes web
- Paginação sem limite (20, 50, 100)

## Próximos Passos (Opcional)

1. **Testes de Carga**: Testar rate limiting com ferramentas como `locust`
2. **Testes de Segurança**: Token brute force, SQL injection
3. **Testes de Performance**: Paginação com 100k+ registros
4. **Testes de Integração**: Com frontend real

## Referências

- [conftest.py](../conftest.py) - Fixtures compartilhadas
- [API_EXTERNA/api.py](../../API_EXTERNA/api.py) - Implementação da API
- [API_EXTERNA/README.md](../../API_EXTERNA/README.md) - Guia de uso

