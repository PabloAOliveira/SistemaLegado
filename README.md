# SGDI - Sistema de Gestão de Demandas Internas

Sistema para gerenciar demandas internas da empresa.

## Como rodar

```bash
pip install -r requirements.txt
python -m flask --app app db upgrade
python init_db.py
python app.py
```

Acesse: http://localhost:5000

## Migracoes de banco (Flask-Migrate)

Guia completo de uso: `docs/flask-migrate-guia-pratico.md`

```bash
python -m flask --app app db upgrade
```

Exemplo para adicionar nova coluna na tabela `demandas`:

```bash
# 1) Atualize o model em models.py
python -m flask --app app db migrate -m "add nova_coluna em demandas"
python -m flask --app app db upgrade
```

## Testes automatizados (E2E)

```bash
pip install -r requirements-test.txt
python -m pytest tests/e2e -v
python -m pytest --cov=. --cov-report=xml --cov-report=term-missing
```

## Funcionalidades

- Criar demandas
- Editar demandas
- Deletar demandas
- Visualizar detalhes
- Comentários
- Classificação por prioridade (alta, média, baixa)
- Filtros por prioridade
- Ordenação automática por prioridade

---

**TODO:**
- Melhorar busca
- Adicionar usuários

---

.\.venv\Scripts\python.exe app.py

*Desenvolvido em 2026*