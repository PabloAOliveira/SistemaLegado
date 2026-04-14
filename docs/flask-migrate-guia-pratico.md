# Guia pratico: Flask-Migrate no SGDI

Este guia mostra como evoluir o banco sem apagar `demandas.db`.

## 1) Pre-requisitos

- Ambiente virtual ativo
- Dependencias instaladas (`requirements.txt`)
- App Flask em `app.py`
- Models em `models.py`

## 2) Primeiro uso no projeto

No SGDI, a pasta `migrations/` ja existe. Entao, para preparar o banco local:

```powershell
python -m flask --app app db upgrade
python init_db.py
```

- `db upgrade` aplica migracoes pendentes
- `init_db.py` garante seed inicial de forma idempotente (`INSERT OR IGNORE`)

## 3) Fluxo diario para mudar schema

1. Edite `models.py` (ex.: tabela `Demanda`)
2. Gere uma migration
3. Revise o arquivo gerado em `migrations/versions/`
4. Aplique no banco com `upgrade`

```powershell
python -m flask --app app db migrate -m "descricao da mudanca"
python -m flask --app app db upgrade
```

## 4) Exemplo: adicionar coluna em demandas

### Passo A - alterar model

Em `models.py`, na classe `Demanda`, adicione a nova coluna.

Exemplo:

```python
nova_coluna = db.Column(db.Text, nullable=True)
```

### Passo B - gerar migration

```powershell
python -m flask --app app db migrate -m "add nova_coluna em demandas"
```

### Passo C - revisar migration

Confira se o arquivo em `migrations/versions/` tem `op.add_column('demandas', ...)`.

### Passo D - aplicar

```powershell
python -m flask --app app db upgrade
```

## 5) Comandos uteis

```powershell
python -m flask --app app db current
python -m flask --app app db history
python -m flask --app app db downgrade -1
```

## 6) Problemas comuns

- **"Can't locate revision"**: falta arquivo em `migrations/versions/` no seu branch.
- **Falha em banco legado**: rode `python -m flask --app app db upgrade` antes de iniciar app.
- **Mudanca nao detectada no migrate**: confirme que a alteracao foi feita em `models.py` (metadados do SQLAlchemy).
- **SQLite em caminho customizado**: ajuste `DATABASE_PATH` no ambiente antes de rodar comandos.

## 7) Ordem recomendada no dia a dia

```powershell
python -m flask --app app db upgrade
python app.py
```

Quando houver mudanca de schema, execute `migrate` + `upgrade` antes de subir a aplicacao.

