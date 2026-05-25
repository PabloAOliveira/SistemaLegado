# ADR-009: Estratégia de testes para a API Externa

## Data
25/05/2026

## Status
Aceito

## Contexto
A API Externa é um componente crítico que deve garantir comportamento previsível, segurança e compatibilidade com consumidores. É necessário uma estratégia de testes que valide autenticação, autorização, documentação e proteções (rate limiting), além de garantir que mudanças não rompam a privacidade (ex.: exposição de emails).

## Decisão
Adotar uma suíte de testes end-to-end (E2E) que:
- Executa a API via factory (Flask `test_client`) e utiliza um banco SQLite isolado por teste (fixtures com `tmp_path`)
- Usa monkeypatch para redirecionar `db.sqlite3.connect` para o DB temporário, garantindo que a mesma camada `db.py` seja usada tanto pela app principal quanto pela API externa
- Armazena na DB de teste um usuário `system_users` com `user_type='externo'` e o hash do token (PBKDF2) para simular autenticação real
- Cobre casos: autenticação (401/403/200), paginação, CORS, OpenAPI spec, rate limiting (429 + Retry-After), ordenação, e métodos HTTP proibidos
- Mantém testes idempotentes e rápidos (evitar dependências externas como Redis ou network)

Implementação prática observada:
- Arquivo `tests/e2e/test_api_externa_e2e.py` com 44 testes agrupados por responsabilidade (Autenticação, Demandas, Solicitantes, Paginação, CORS, OpenAPI, RateLimiting, Resposta, HTTPMethods, EdgeCases)
- `tests/conftest.py` ampliado com fixture `api_client` e fixtures `valid_token` e `invalid_token`
- Testes de rate limiting disparam requisições rápidas e verificam presença de `Retry-After` e 429

## Alternativas Consideradas
- Testes unitários muito isolados (mock de `db.fetch_all`): rápidos e determinísticos, mas não exercitam integração real entre camadas. Decidimos combinar E2E para cobertura de integração e manter alguns testes unitários em serviços separadamente.
- Usar um banco em memória compartilhado (SQLite :memory:): em-memory não funciona bem quando a conexão é criada em módulos diferentes; preferimos arquivo temporário por teste e monkeypatch para `connect`.
- Usar testcontainers / Docker para tests que precisam de Redis/DB separados: aumenta realismo, porém adiciona custo de execução na pipeline. Mantivemos testes rápidos e isolados sem dependências externas.

## Consequências

### Positivas
- Alta confiança: E2E garante que autenticação, rotas e serialização funcionam em conjunto.
- Rápido feedback local e CI: testes são rápidos (suíte atual < 6s localmente no ambiente de desenvolvimento).
- Reprodutibilidade: banco temporário por teste e monkeypatch torna testes determinísticos e isolados.

### Negativas
- Alguns cenários distribuídos (rate limiting entre múltiplas instâncias) não são cobertos — exigirão testes de integração/infra com Redis/cluster.
- A geração do hash do token no fixture deve espelhar a produção (mesmo algoritmo/iterações) — se o algoritmo mudar, fixtures devem ser atualizadas.

## Notas de Implementação
- Fixtures importantes: `db_path`, `api_client`, `valid_token`, `invalid_token` (em `tests/conftest.py`)
- Arquivo de testes principal: `tests/e2e/test_api_externa_e2e.py`
- Recomenda-se rodar a suíte de testes como parte do CI; para testes de carga/cluster usar ferramentas dedicadas (locust, k6) com infra de Redis para rate limiting global.

---

Referências: `tests/conftest.py`, `tests/e2e/test_api_externa_e2e.py`, `API_EXTERNA/api.py`.
