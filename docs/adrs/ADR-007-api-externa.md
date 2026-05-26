# ADR-007: API Externa Read-Only separada do app principal

## Data
25/05/2026

## Status
Aceito

## Contexto
Necessitávamos oferecer acesso programático somente leitura a dados de demandas e solicitantes para consumidores externos (integrações B2B, dashboards, scripts automatizados). Requisitos importantes:
- Segurança: tokens para autenticação, evitar exposição de tokens em URLs, armazenar apenas hash dos tokens com salt
- Escopo restrito: apenas leitura, sem exposição de emails dos solicitantes
- Observabilidade e governança: documentação OpenAPI/Swagger, respostas padronizadas (401, 403, 429)
- Proteção contra abuso: rate limiting (10 req/s, 600 req/min)
- Deploy independente: deve poder rodar separadamente do app web principal (processo isolado, porta separada)
- Compatibilidade com frontends: CORS configurado e UI Swagger para onboarding

## Decisão
Criar um sub-módulo independente `API_EXTERNA/` que implementa uma API HTTP read-only com as seguintes características:
- Factory `create_api_app()` que retorna um Flask app independente e testável
- Endpoints protegidos: `/api/v1/demandas` e `/api/v1/solicitantes` (sem campo `email`)
- Autenticação por token enviada apenas via headers (Authorization: Bearer <token> ou X-API-Token)
- Tokens armazenados na tabela `system_users` com `user_type='externo'`; no banco são guardados `token` (hash PBKDF2-HMAC-SHA256) e `token_salt` (hex)
- Rate limiting em memória com sliding windows por token (ou por IP se não autenticado): 10 req/s e 600 req/min
- Documentação OpenAPI 3.0 + Swagger UI em `/api/v1/docs` e spec em `/api/v1/openapi.json`, incluindo respostas 401/403/429
- CORS restrito a headers necessários e métodos GET/OPTIONS
- Remoção do header `Server` do WSGI server (classe `QuietWSGIServer`) para não vazar versões
- A API roda em porta configurada (`config.FLASK_PORT + 1`) quando executada como processo próprio

## Alternativas Consideradas
- JWT (signed) em vez de tokens opacos: JWT facilitaria verificações sem consultar o banco, mas aumenta risco de vazamento de claims e exige mecanismo de revogação. Optamos por tokens opacos com hash+salt para permitir revogação simples e auditoria centralizada.
- Usar Redis/Cache central para rate limiting: mais robusto e escalável para múltiplas instâncias, porém adiciona dependência operacional. Começamos com implementação em memória (sliding window) para simplicidade e teste; migrável para Redis se necessário.
- Manter endpoints no mesmo processo do `app.py` (monolito): reduziria duplicação, mas mistura responsabilidades, aumenta blast radius em caso de falhas e dificulta deploy independente. Optamos por separar para permitir escalonamento e políticas de segurança distintas.
- Expor emails parcialmente (masked): por privacidade optamos por não retornar email algum pelo endpoint público.

## Consequências

### Positivas
- Isolamento claro entre API pública e app principal: facilita deploy independente e políticas de segurança diferentes.
- Tokens armazenados hashed + salt reduzem impacto de vazamento do banco de dados.
- Sliding window rate limiter protege contra bursts e abuso, fornece Retry-After ao cliente.
- OpenAPI/Swagger facilita integração por terceiros e permite botão "Authorize" no UI (com as devidas instruções para enviar token via header).

### Negativas (trade-offs)
- Rate limiter em memória não compartilha estado entre múltiplas instâncias; para cluster será necessária migração para Redis ou similar.
- Tokens opacos exigem consulta ao banco para autenticação, com custo de I/O; caches podem mitigar.
- A manutenção de duas bases de configuração e dois processos pode aumentar esforço operacional.
- Ao manter header `Access-Control-Allow-Origin: *`, deve-se avaliar políticas em produção; pode precisar restringir origens por política de segurança.

## Notas de Implementação
- Tabela `system_users` adicionada em migração (campo `token`, `token_salt`, `user_type`)
- Classe `QuietWSGIServer` herdando `BaseWSGIServer` para limpar `server_version` e `sys_version`
- Endpoints suportam paginação com `page` e `per_page` (20, 50, 100)
- Swagger inclui resposta 429 com header `Retry-After`


---

Referências: código em `API_EXTERNA/api.py`, migrações em `migrations/versions/`.
