# SGDI - Sistema de Gestão de Demandas Internas

Sistema para gerenciar demandas internas da empresa.

## Como rodar

```bash
pip install -r requirements.txt
python init_db.py
python app.py
```

Acesse: http://localhost:5000

## Testes automatizados (E2E)

```bash
pip install -r requirements-test.txt
python -m pytest tests/e2e -v
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