# ADR-004: Evoluir schema com Flask-Migrate em vez de recriar banco

## Data
03/04/2026

## Status
Proposto

## Contexto
A adicao da coluna `prioridade` (commit `b2c6eaa`) gerou quebra para quem ja tinha `demandas.db` sem a coluna. Hoje, sem trilha de migracao versionada, a solucao vira apagar banco local, o que perde dados e dificulta colaboracao.

## Decisao
Adotar migracoes versionadas de schema com Flask-Migrate (Alembic), incluindo adicoes de coluna e ajustes de chave primaria/autoincrement quando necessarios.

## Alternativas Consideradas
- Opcao 1: manter `init_db.py` com `CREATE TABLE IF NOT EXISTS` sem versao de schema.
- Opcao 2: scripts SQL manuais por release.

## Consequencias

### Positivas
- Pros: atualiza bancos existentes sem perder dados.
- Pros: cria historico auditavel de mudancas de schema.
- Pros: reduz friccao para onboarding e CI.

### Negativas (trade-offs)
- Custo: aumenta complexidade inicial de setup.
- Custo: exige disciplina de gerar/revisar migracoes a cada mudanca de modelo.

