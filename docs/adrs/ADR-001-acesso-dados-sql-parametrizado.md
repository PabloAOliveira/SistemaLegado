# ADR-001: Padronizar acesso a dados com helpers e SQL parametrizado

## Data
03/04/2026

## Status
Aceito

## Contexto
O historico (commit `6675f5c`) mostra refatoracao de acesso ao banco em `app.py` com criacao de `get_db`, `fetch_all`, `fetch_one` e `execute_query`. Antes, havia SQL com f-strings e abertura/fechamento de conexao espalhados, aumentando risco de SQL injection e inconsistencias de tratamento de erro.

## Decisao
Centralizar o acesso ao SQLite em helpers unicos e usar sempre queries parametrizadas (`?`) para entrada do usuario.

## Alternativas Consideradas
- Opcao 1: manter SQL inline em cada rota.
- Opcao 2: criar camada de repositorio completa com ORM.

## Consequencias

### Positivas
- Pros: reduz risco de SQL injection.
- Pros: padroniza conexao e tratamento de erro.
- Pros: melhora manutencao e legibilidade de `app.py`.

### Negativas (trade-offs)
- Custo: ainda existe acoplamento de SQL no backend Flask (sem ORM).
- Custo: exige disciplina para nao criar novos acessos fora dos helpers.

