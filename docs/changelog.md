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


