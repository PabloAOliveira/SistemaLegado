# ADR-003: Configuracao por ambiente e segredo fora do codigo

## Data
03/04/2026

## Status
Aceito

## Contexto
O commit `6675f5c` introduziu `python-dotenv`, leitura de `FLASK_SECRET_KEY`, `DATABASE_PATH`, `FLASK_HOST`, `FLASK_PORT` e `FLASK_DEBUG` em `app.py`. Antes, havia configuracao fixa no codigo e bind mais aberto.

## Decisao
Padronizar configuracao operacional via variaveis de ambiente com defaults seguros para desenvolvimento local.

## Alternativas Consideradas
- Opcao 1: manter configuracoes hardcoded no codigo.
- Opcao 2: usar apenas arquivo de configuracao versionado.

## Consequencias

### Positivas
- Pros: separa segredo e configuracao da base de codigo.
- Pros: facilita deploy em ambientes diferentes.
- Pros: reduz risco operacional por ajuste manual no codigo.

### Negativas (trade-offs)
- Custo: precisa disciplina para configurar `.env` em cada ambiente.
- Custo: pode causar erros de startup se variaveis obrigatorias faltarem.

