# ADR-006: Separar dependencias por ambiente e formalizar quality gate

## Data
03/04/2026

## Status
Aceito

## Contexto
Os commits `7a45d54`, `422f353` e `12befdf` mostram evolucao de `requirements*.txt`, upgrade de pacotes criticos e criacao de documentacao em `docs/quality-gate.md`. Era necessario reduzir risco de dependencia em runtime e padronizar criterio de qualidade.

## Decisao
Manter tres camadas de dependencias (`requirements.txt`, `requirements-test.txt`, `requirements-dev.txt`) e adotar quality gate documentado para merge.

## Alternativas Consideradas
- Opcao 1: manter um unico `requirements.txt` para tudo.
- Opcao 2: deixar criterio de qualidade informal por revisao ad hoc.

## Consequencias

### Positivas
- Pros: runtime mais enxuto e previsivel.
- Pros: ambiente de teste/dev reprodutivel.
- Pros: melhora governanca tecnica e rastreabilidade de decisoes.

### Negativas (trade-offs)
- Custo: necessidade de sincronizar multiplos arquivos de dependencia.
- Custo: quality gate pode aumentar tempo de entrega no curto prazo.

