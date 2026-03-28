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

---

**TODO:**
- Adicionar prioridades
- Melhorar busca
- Adicionar usuários

---

*Desenvolvido em 2026*