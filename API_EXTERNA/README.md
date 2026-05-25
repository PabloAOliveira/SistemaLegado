SGDI External Read API
======================

Esta pasta contém a API externa somente leitura para as entidades `demandas` e `solicitantes`.

Características principais:
- Endpoints:
  - GET /api/v1/demandas — lista todas as demandas (inclui status, responsavel, prazo, etc.)
  - GET /api/v1/solicitantes — lista solicitantes **sem** o campo `email`
  - GET /api/v1/openapi.json — OpenAPI 3.0 spec
  - GET /api/v1/docs — Swagger UI para a documentação

- Autenticação: baseado em token. O token deve estar presente na tabela `system_users` com `user_type = 'externo'`.
  O token é armazenado como **hash com salt** (não é possível recuperar o valor após criado).
  Envie o token **apenas via header** (`Authorization: Bearer` ou `X-API-Token`).

Como rodar a API externa (independente do app principal):

1. Garanta que o banco e as migrações estão aplicadas (a migração que adiciona `system_users` já foi criada):

```powershell
Push-Location "E:\HigorE\ATITUS\2026-1\Desafio da tecnologia\Repo\Sistema SGDI\SistemaLegado"
python -m flask --app app db upgrade
Pop-Location
```

2. Rodar a API externa (usa o mesmo arquivo de configuração / banco do app principal):

```powershell
python -c "from API_EXTERNA.api import create_api_app; app = create_api_app(); app.run(host='0.0.0.0', port=5001)"
```

3. Testar endpoints (exemplo com token de teste inserido pela migration):

```powershell
curl -H "Authorization: Bearer external-token-123" http://localhost:5001/api/v1/demandas
curl -H "Authorization: Bearer external-token-123" http://localhost:5001/api/v1/solicitantes
```

Gerenciamento de tokens
-----------------------

Um pequeno utilitário `manage_tokens.py` foi adicionado para criar/listar tokens.
Os tokens retornados no comando `create` não podem ser recuperados depois.

```powershell
# Criar um token
python API_EXTERNA/manage_tokens.py create --username "clientX" --token "optional-token-value"

# Listar tokens (exibe o hash armazenado)
python API_EXTERNA/manage_tokens.py list
```

Recomendações de segurança
-------------------------
- Em produção, use tokens fortes (UUID4 ou HMAC). Não mantenha tokens seed em migrações de produção.
- Sirva a API externa via HTTPS e aplique rate-limiting por token.
- Considere logs de auditoria para cada chamada.
