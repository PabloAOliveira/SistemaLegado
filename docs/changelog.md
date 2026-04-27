# Changelog

## 2026-03-28 - Higor Milani

Este documento resume as mudancas realizadas no projeto `SistemaLegado` durante a sessao.

### Backend (`app.py`)

- Refatoracao geral de acesso ao banco:
  - Criados helpers `get_db`, `fetch_all`, `fetch_one` e `execute_query`.
  - Fechamento de conexao padronizado via context manager.
- SQL hardcoded por f-string foi trocado por queries parametrizadas (`?`) para reduzir risco de SQL injection.
- Rotas atualizadas com tipos explicitos nos parametros:
  - `editar`: `/editar/<int:demanda_id>`
  - `deletar`: `/deletar/<int:demanda_id>`
  - `detalhes`: `/detalhes/<int:demanda_id>`
  - `adicionar_comentario`: `/adicionar_comentario/<int:demanda_id>`
- Verbos HTTP explicitos adicionados nas rotas GET:
  - `/`, `/buscar`, `/detalhes/<int:demanda_id>`
- Rota de exclusao alterada para verbo REST correto:
  - `DELETE /deletar/<int:demanda_id>`
- Tratamento de erros de banco melhorado:
  - Criado helper `log_db_error(...)`.
  - Logs com contexto por operacao (`nova_demanda`, `editar`, `deletar`, `adicionar_comentario`).
  - Mensagens de `flash` mantidas para UX.
- Configuracao por ambiente:
  - Adicionado `load_dotenv()`.
  - `FLASK_SECRET_KEY` carregada do ambiente com fallback seguro fora de producao.
  - `DATABASE_PATH` carregado por variavel de ambiente.
  - Bind padrao do servidor alterado de `0.0.0.0` para `127.0.0.1`.
  - `host`, `port` e `debug` agora controlados por:
    - `FLASK_HOST` (padrao `127.0.0.1`)
    - `FLASK_PORT` (padrao `5000`)
    - `FLASK_DEBUG` (`1/true/yes/on` habilita)

### Frontend (`templates/index.html`)

- Acao de exclusao adaptada para usar `fetch` com metodo `DELETE`.
- Link de deletar da tabela passou a chamar `deletarDemanda(id)` via JavaScript.

### Testes automatizados

- Suite E2E criada para cobrir as rotas principais da aplicacao.
- Arquivos de teste:
  - `tests/conftest.py`:
    - Fixture de banco SQLite isolado por teste.
    - Fixture de `client` Flask com monkeypatch de conexao.
  - `tests/e2e/test_routes_e2e.py`:
    - Cobertura de listagem, criacao, edicao, delecao, busca, detalhes e comentarios.
- Ajustes de robustez:
  - Consultas de validacao em teste agora usam context manager (`with sqlite3.connect(...)`).
  - Teste de delecao atualizado para `client.delete(...)`.

### Dependencias e ambientes

- `requirements.txt` reorganizado para runtime e atualizado com correcoes:
  - `Flask==3.1.3`
  - `Werkzeug==3.1.6`
  - `python-dotenv==1.0.1`
- Novos manifests por ambiente:
  - `requirements-test.txt` (herda de `requirements.txt` + `pytest==8.3.5`)
  - `requirements-dev.txt` (herda de `requirements-test.txt`)

### Git e configuracao de projeto

- `.gitignore` expandido com regras amplas para Python/IDE/ambiente (venv, caches, coverage, build artifacts etc).

### Validacoes executadas

- Reexecucao recorrente da suite E2E durante as alteracoes.
- Ultimo status validado: `9 passed` em `tests/e2e`.

### Auditoria de dependencias (`pip-audit`)

- Vulnerabilidades diretas de `Flask` e `Werkzeug` tratadas com upgrade.
- Permanecem alertas no ambiente para pacotes nao pinados diretamente no app:
  - `filelock`
  - `requests`
  - `pygments`
- `pip` do ambiente foi atualizado para `26.0.1`.

### Organizacao de documentacao

- Criada a pasta `docs/` para centralizar documentacao tecnica do projeto.
- Arquivo de changelog movido para `docs/changelog.md`.
- Arquivo de code review movido para `docs/Code-Review.md`.
- Novo guia de quality gate criado em `docs/quality-gate.md` com instrucoes para SonarQube e Qodana.

## 2026-03-29 - MariaChehade

Este bloco resume as mudancas introduzidas pela Maria no projeto.

### Backend (`app.py`)

- Adicionado o campo `prioridade` na entidade de demandas.
- Persistencia da prioridade incluida no fluxo de criacao/edicao no banco.
- Ordenacao por prioridade aplicada na listagem principal.

### Frontend (`templates/`)

- Formularios e telas atualizados para exibir/editar o campo `prioridade`.
- Tela principal ajustada para refletir a nova ordenacao por prioridade.

### Commits relacionados

- `b2c6eaa`: `feat(prioridade): add campo prioridade nas telas e banco e ordenando as prioridades na tela principal`
- `6467d51`: commit de teste inicial da autora no repositorio.

## 2026-04-03 - Higor Milani

### ADRs (Architecture Decision Records)

- Criada a pasta `docs/adrs/` para registrar decisoes tecnicas de forma rastreavel.
- Criado indice em `docs/adrs/README.md` com a lista de ADRs do projeto.
- Formalizadas decisoes tecnicas importantes em documentos ADR:
  - `ADR-001`: acesso a dados com helpers e SQL parametrizado.
  - `ADR-002`: semantica HTTP/REST nas rotas.
  - `ADR-003`: configuracao por ambiente e segredo fora do codigo.
  - `ADR-004` (Proposto): migracoes de schema com Flask-Migrate.
  - `ADR-005`: estrategia de testes E2E com banco isolado.
  - `ADR-006`: separacao de dependencias por ambiente e quality gate.

### Rastreabilidade Git (contexto dos ADRs)

- `6675f5c`: refatoracao de banco, seguranca e configuracao por ambiente.
- `1c2d596`: criacao da suite de testes E2E.
- `7a45d54`: reorganizacao de dependencias por ambiente.
- `422f353`: documentacao tecnica e quality gate.
- `b2c6eaa`: adicao de `prioridade` (motivando ADR de migracoes).

## 2026-04-08 - Enzo Almeida

### Frontend (`templates/nova_demanda.html`)

- Validacao no formulario de criacao de demanda para impedir salvar sem preencher:
  - `titulo`, `descricao` e `solicitante` (campos marcados como `required`).
  - Bloqueio do submit quando o valor for apenas espacos (trim) com aviso via `alert` e foco no primeiro campo faltante.

### Dependencias

- `requirements.txt` atualizado.
- `requirements-test.txt` ajustado para `pytest==6.2.5`.
- Adicionado `requirements-freeze.txt`.

### Commits relacionados

- `f780d02`: `Valida titulo, descricao e solicitante no front-end`

## 2026-04-07 - Higor Milani

### Migracoes de banco (Flask-Migrate)

- Implementado `Flask-Migrate` + `Flask-SQLAlchemy` no bootstrap da aplicacao (`app.py`).
- Criado `models.py` com metadados das tabelas `demandas` e `comentarios` para versionamento de schema.
- Criada estrutura de migracao em `migrations/` com revisao base `20260407_01`.
- A revisao base ajusta bancos legados sem apagar dados:
  - garante coluna `prioridade` em `demandas`.
  - garante chave primaria `id` autoincremental.
- `init_db.py` foi alterado para:
  - aplicar `db upgrade` via Flask-Migrate.
  - popular seed de forma idempotente (`INSERT OR IGNORE`).

## 2026-04-14 - Enzo Almeida

### Solicitantes e comentarios

- Campo `Solicitante` das telas de nova demanda e edicao foi trocado de texto livre para dropdown.
- Campo de autor do comentario na tela de detalhes tambem passou a usar dropdown.
- Comentarios agora exigem texto obrigatorio no frontend e no backend antes do envio.

### Cadastro de solicitantes

- Pagina `Solicitante` deixou de ser placeholder e passou a listar os solicitantes disponiveis.
- Adicionada rota `/solicitante/cadastrar` com formulario para:
  - `nome`
  - `email`
  - `cargo`
- Os tres campos do cadastro sao obrigatorios.
- Novo cadastro alimenta a lista em memoria usada pelos dropdowns da aplicacao.

### Backend e testes

- `DEFAULT_PEOPLE` foi substituido por estrutura de solicitantes completos (`DEFAULT_REQUESTERS`).
- Criados helpers para expor nomes disponiveis e manter a lista de solicitantes carregada na aplicacao.
- Testes E2E e fixtures foram atualizados para cobrir dropdowns, validacao de comentario e cadastro de solicitante.

## 2026-04-27 - Enzo Almeida (RA: 1134927)

Este bloco resume as mudancas realizadas na area de Solicitantes e ajustes de UI/CSS.

### Frontend (`templates/`)

- Pagina `Solicitantes` (`templates/solicitante.html`) padronizada para seguir o layout da tela inicial:
  - Toolbar no topo com `Cadastrar` e `Voltar` alinhados a direita.
  - Tabela com o primeiro campo sendo `ID`.
  - Truncamento visual com reticencias (ellipsis) para campos longos.
  - Coluna `Acoes` com opcoes de `Ver`, `Editar` e `Deletar` (icones no padrao da tabela principal).
  - Scroll ajustado para ser do conteudo inteiro da pagina (grafico + tabela), e nao apenas na tabela.
- Tela de cadastro de solicitante (`templates/cadastrar_solicitante.html`) alinhada ao padrao visual:
  - Toolbar no topo com botao `Voltar`.
  - Campos `nome`, `email` e `cargo` com limite de `maxlength=40`.
- Criadas telas para operacoes de solicitantes:
  - `templates/detalhes_solicitante.html` (visualizacao).
  - `templates/editar_solicitante.html` (edicao).

### Backend (`app.py`)

- `get_requesters()` passou a retornar tambem o `id` do solicitante.
- Adicionado helper `get_requester_by_id(requester_id)`.
- Criadas rotas CRUD para solicitantes:
  - `GET /solicitante/<int:requester_id>` (detalhes).
  - `GET|POST /solicitante/editar/<int:requester_id>` (editar).
  - `DELETE /solicitante/deletar/<int:requester_id>` (deletar via fetch).
- Validacao de tamanho no backend para `nome`, `email` e `cargo` (maximo 40 caracteres) em cadastro e edicao.

### CSS / Navegacao (`static/style.css`, `templates/base.html`)

- CSS ajustado para aplicar o mesmo estilo global em `input[type="email"]` (antes ficava com estilo padrao do browser).
- Link/botao `Solicitante` no header padronizado com estilo de botao e ocultado quando o usuario esta em rotas `/solicitante...`.

