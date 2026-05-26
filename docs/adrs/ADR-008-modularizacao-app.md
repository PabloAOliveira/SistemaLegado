# ADR-008: Modularização do `app.py` e separação de responsabilidades

## Data
25/05/2026

## Status
Aceito

## Contexto
O código original mantinha toda a lógica da aplicação web e, em seguida, foi necessário adicionar uma API externa independente. Para facilitar testes, deploys e evolução independente, foi necessário modularizar responsabilidades (aplicação web principal, utilitários de banco, API externa, serviços). Requisitos:
- Permitir que a API externa rode independentemente do app web
- Facilitar testes unitários e E2E isolando o ambiente (ferreiro das fixtures de banco)
- Evitar import cycles e dependências implícitas que quebra o teste ou o deploy

## Decisão
Adotar um layout modular onde cada responsabilidade tem seu próprio módulo/pacote:
- `app.py`: contém factory `create_app()` para a aplicação web principal (rotas web, templates, dashboards)
- `API_EXTERNA/`: pacote separado com `api.py` e `create_api_app()` para a API pública read-only
- `db.py`: funções genéricas de acesso ao SQLite (`get_db`, `fetch_all`, `fetch_one`, `execute_query`) usadas por ambos os apps
- `services/`: lógica de domínio (ex.: `demandas.py`, `requesters.py`, `dashboard.py`) para evitar lógica pesada nas rotas
- `config.py`: centralização de configuração por ambiente

Práticas adotadas:
- Aplicações expostas via factory (não singletons globais), facilitando criar clientes de teste (Flask test_client)
- Importações de baixo acoplamento (rotas importam serviços; serviços importam `db`; apps importam serviços)
- Evitar que `API_EXTERNA` importe `app.py` e vice-versa para impedir dependência circular e permitir execução independente

## Alternativas Consideradas
- Monolito único com flags de rota para habilitar/desabilitar API externa: simples inicialmente, mas frágil para deploy independente.
- Micro-serviços totalmente separados com repositório distinto: mais limpo, porém aumenta overhead operacional. Optamos por crate sub-pacote no mesmo repositório para facilitar manutenção e CI, mas permitir deploy separado.

## Consequências

### Positivas
- Testabilidade: fábricas permitem criar instâncias isoladas em `pytest` fixtures (ex.: `app_module.create_app()` e `API_EXTERNA.api.create_api_app()`)
- Menor acoplamento: alterações na API externa tendem a não afetar a app web
- Simplicidade operacional: mesmo repositório, mas processos separados se desejado

### Negativas
- Ainda há compartilhamento de código (db.py) que precisa ser mantido com cuidado — mudanças críticas podem afetar ambos
- Para escalabilidade cross-host, será necessário empacotar e separar deploys (Docker/CI) explicitamente

## Notas de Implementação
- `create_app()` e `create_api_app()` factories são usadas nas fixtures do `tests/conftest.py` para criar `test_client`s independentes.
- `config.FLASK_PORT` é a base; a API externa sobe em `FLASK_PORT + 1` quando executada via `run_api_server`.

Referências: `app.py`, `API_EXTERNA/api.py`, `tests/conftest.py`.

