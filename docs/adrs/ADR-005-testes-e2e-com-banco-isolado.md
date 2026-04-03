# ADR-005: Testes E2E com banco SQLite isolado por fixture

## Data
03/04/2026

## Status
Aceito

## Contexto
O commit `1c2d596` e o changelog registram criacao da suite E2E com `tests/conftest.py` e `tests/e2e/test_routes_e2e.py`, usando banco isolado por teste e `client` Flask para validar rotas principais.

## Decisao
Manter testes E2E de rotas criticas com banco temporario isolado em fixture, sem depender de `demandas.db` real do desenvolvedor.

## Alternativas Consideradas
- Opcao 1: testar apenas manualmente via navegador.
- Opcao 2: usar somente testes unitarios de funcoes isoladas.

## Consequencias

### Positivas
- Pros: reduz regressao em fluxos fim a fim (CRUD, busca, comentarios).
- Pros: melhora confiabilidade para refatoracao.
- Pros: permite executar em CI de forma repetivel.

### Negativas (trade-offs)
- Custo: testes E2E podem ser mais lentos que unitarios.
- Custo: manutencao dos testes cresce com evolucao de rotas/templates.

