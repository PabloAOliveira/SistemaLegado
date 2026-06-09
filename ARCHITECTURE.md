# Arquitetura Modularizada - SGDI

Documento que descreve a estrutura modularizada da aplicação Flask de Gestão de Demandas.

## Estrutura de Diretórios

```
SistemaLegado/
├── app.py                      # Application factory (ponto de entrada)
├── config.py                   # Configurações centralizadas
├── db.py                       # Operações genéricas de banco de dados
├── models.py                   # Modelos SQLAlchemy (já existia)
├── routes.py                   # Definições de todas as rotas HTTP
│
├── services/                   # Pacote de serviços (lógica de negócio)
│   ├── __init__.py
│   ├── utils.py               # Funções utilitárias (normalização, parsing, etc.)
│   ├── requesters.py          # Serviços de solicitantes (CRUD + validação)
│   ├── demandas.py            # Serviços de demandas (CRUD + lógica)
│   ├── comentarios.py         # Serviços de comentários (CRUD)
│   ├── graphics.py            # Geração de gráficos Plotly
│   ├── dashboard.py           # Cálculo de métricas e KPIs
│   └── export.py              # Exportação em Excel e PDF
│
├── templates/                  # Arquivos Jinja2 (como era)
├── static/                     # Arquivos estáticos (CSS, JS, etc.)
├── migrations/                 # Migrações Alembic
├── tests/                      # Suite de testes
└── docs/                       # Documentação adicional
```

## Módulos e Responsabilidades

### 1. **config.py** - Configurações Centralizadas
Concentra todas as constantes e configurações:
- Variáveis de ambiente (Flask, Database, etc.)
- Constantes de negócio (DEFAULT_DEADLINE_DAYS, COMPANY_NAME)
- Dados padrão (DEFAULT_REQUESTERS)
- Paletas de cores para gráficos (PALETTE_*)

**Benefício:** Mudanças de configuração ficam localizadas em um único arquivo.

### 2. **db.py** - Acesso a Banco de Dados Genérico
Funções de baixo nível para comunicação com SQLite:
- `get_db()` - Abre conexão
- `fetch_all(query, params)` - Executa SELECT que retorna múltiplas linhas
- `fetch_one(query, params)` - Executa SELECT que retorna uma linha
- `execute_query(query, params)` - Executa INSERT/UPDATE/DELETE com commit
- `log_db_error(operation, error, **context)` - Log de erros

**Benefício:** Centraliza acesso a dados, facilitando testes e mudanças de banco de dados.

### 3. **services/utils.py** - Funções Utilitárias
Funções reutilizáveis de formatação e parsing:
- Formatação de datas: `date_now()`, `parse_datetime()`
- Normalização: `normalize_status()`, `normalize_priority()`
- Formatação de labels: `status_label()`, `format_priority_filter_label()`
- Cálculos: `calculate_deadline()`

**Benefício:** Evita duplicação de lógica de transformação de dados.

### 4. **services/requesters.py** - Gestão de Solicitantes
CRUD e lógica de solicitantes:
- `get_requesters()` - Lista todos
- `get_requester_by_id(id)` - Busca um
- `create_requester()` - Cria novo
- `update_requester()` - Atualiza
- `delete_requester()` - Deleta
- `is_valid_person()` - Validação

**Benefício:** Centraliza todas as operações relacionadas a solicitantes.

### 5. **services/demandas.py** - Gestão de Demandas
CRUD e lógica de demandas:
- `get_demandas(prioridade, solicitante, data_inicio, data_fim)` - Lista com filtros múltiplos
- `get_demanda(id)` - Busca uma
- `create_demanda()` - Cria nova
- `update_demanda()` - Atualiza
- `delete_demanda()` - Deleta
- `ensure_demandas_dashboard_columns()` - Garante schema atualizado

**Benefício:** Lógica de demandas isolada com suporte a filtros múltiplos e combinados.

### 6. **services/comentarios.py** - Gestão de Comentários
CRUD de comentários:
- `get_comentarios(demanda_id)` - Lista comentários
- `create_comentario()` - Cria novo

**Benefício:** Operações de comentários isoladas e reutilizáveis.

### 7. **services/graphics.py** - Geração de Gráficos
Cria visualizações Plotly:
- `gerar_graficos()` - Gera 4 gráficos (Solicitante, Prioridade, Status, Evolução Temporal)
- `_apply_dark_layout()` - Aplica tema visual

**Benefício:** Lógica de visualização separada da lógica de rotas.

### 8. **services/dashboard.py** - Métricas e KPIs
Cálculo de indicadores para o dashboard:
- `calculate_dashboard_metrics(demandas)` - Calcula total, abertas, concluídas, atrasadas, críticas, etc.

**Benefício:** Lógica de métricas reutilizável em testes e APIs.

### 9. **services/export.py** - Exportação de Dados
Geração de relatórios:
- `export_to_excel()` - Exporta em XLSX com gráficos
- `export_to_pdf()` - Exporta em PDF com formatação
- Funções auxiliares: `build_demandas_data()`, `calculate_kpis()`, `filter_overdue_demands()`, etc.

**Benefício:** Lógica de exportação complexa centralizada e testável.

### 10. **routes.py** - Rotas HTTP
Define todas as rotas da aplicação:
- `register_routes(app)` - Função que registra rotas no Flask
- Agrupa rotas por domínio (index, demandas, solicitantes, exportação, etc.)
- Cada rota delegapara services apropriados

**Benefício:** Separação clara entre HTTP e lógica de negócio.

### 11. **app.py** - Application Factory
Ponto de entrada da aplicação:
- `create_app()` - Factory function que cria a app Flask
- Inicializa extensões (SQLAlchemy, Migrate)
- Registra rotas
- Expõe `calculate_dashboard_metrics` para compatibilidade com testes

**Benefício:** Padrão Flask moderno, facilita testes e múltiplas instâncias.

## Fluxo de Requisição

```
Cliente HTTP
   ↓
routes.py (rota HTTP)
   ↓
services/* (lógica de negócio)
   ↓
db.py (acesso a dados)
   ↓
SQLite (persistência)
```

## Benefícios da Modularização

✅ **Separação de Responsabilidades** - Cada módulo tem uma função clara
✅ **Reutilização** - Serviços podem ser usados em rotas, testes e APIs
✅ **Testabilidade** - Serviços podem ser testados isoladamente
✅ **Manutenibilidade** - Mudanças localizadas em módulos específicos
✅ **Escalabilidade** - Fácil adicionar novos serviços ou rotas
✅ **Legibilidade** - Código mais organizado e compreensível

## Como Adicionar uma Nova Funcionalidade

1. **Se é lógica de dados**: criar função em `services/novo_servico.py`
2. **Se é transformação**: adicionar em `services/utils.py`
3. **Se é rota HTTP**: adicionar em `routes.py` (chamando services)
4. **Se precisa de config**: adicionar em `config.py`

Exemplo:
```python
# 1. Lógica em services/demandas.py
def get_demandas_por_status(status):
    return fetch_all("SELECT * FROM demandas WHERE status = ?", (status,))

# 2. Rota em routes.py
@app.route('/demandas/<status>')
def demandas_status(status):
    demandas = get_demandas_por_status(status)
    return render_template('demandas.html', demandas=demandas)
```

## Compatibilidade com Testes

O arquivo `conftest.py` foi atualizado para:
- Importar `db` módulo para monkeypatch
- Usar `app.create_app()` para criar instâncias de teste
- Manter compatibilidade com testes existentes

Todos os testes passam: **21/21 ✅**

## Arquivos Antigos

O arquivo `app_old.py` contém o código original monolítico (1343 linhas) para referência.

## Próximos Passos

💡 Para evoluir ainda mais:
1. Criar `services/auth.py` para autenticação/autorização
2. Criar `api.py` para endpoints REST JSON
3. Adicionar `services/notifications.py` para emails/alertas
4. Criar `tests/unit/` para testes unitários de services

