# 📋 Relatório de Code Review — SGDI (Sistema de Gestão de Demandas Internas)

**Data:** 2025  
**Escopo:** Análise completa de código, segurança, arquitetura, banco de dados e design do sistema legado.

---

## Índice

1. [SQL Injection em todas as rotas](#1--sql-injection-em-todas-as-rotas)
2. [Secret Key hardcoded e fraca](#2--secret-key-hardcoded-e-fraca)
3. [Ausência de autenticação e autorização](#3--ausência-de-autenticação-e-autorização)
4. [Deleção via método GET sem confirmação](#4--deleção-via-método-get-sem-confirmação)
5. [Conexão com banco de dados sem gerenciamento adequado](#5--conexão-com-banco-de-dados-sem-gerenciamento-adequado)
6. [Banco de dados sem chaves primárias, auto-incremento e foreign keys](#6--banco-de-dados-sem-chaves-primárias-auto-incremento-e-foreign-keys)
7. [Dados órfãos no banco de dados](#7--dados-órfãos-no-banco-de-dados)
8. [Ausência de validação de entrada nos formulários](#8--ausência-de-validação-de-entrada-nos-formulários)
9. [XSS (Cross-Site Scripting) potencial](#9--xss-cross-site-scripting-potencial)
10. [Acesso a dados por índice numérico em vez de nome de coluna](#10--acesso-a-dados-por-índice-numérico-em-vez-de-nome-de-coluna)
11. [Função `get_db()` definida mas não utilizada](#11--função-get_db-definida-mas-não-utilizada)
12. [Função `calcular_prazo()` é placeholder sem uso](#12--função-calcular_prazo-é-placeholder-sem-uso)
13. [Aplicação rodando com `debug=True` e `host='0.0.0.0'`](#13--aplicação-rodando-com-debugtrue-e-host0000)
14. [URLs hardcoded nos templates](#14--urls-hardcoded-nos-templates)
15. [Ausência de proteção CSRF nos formulários](#15--ausência-de-proteção-csrf-nos-formulários)
16. [Código administrativo comentado](#16--código-administrativo-comentado)
17. [Estilo inline nos templates HTML](#17--estilo-inline-nos-templates-html)
18. [Footer fixo sobrepõe conteúdo da página](#18--footer-fixo-sobrepõe-conteúdo-da-página)
19. [Falta de responsividade e acessibilidade](#19--falta-de-responsividade-e-acessibilidade)
20. [Ausência de tratamento de erros](#20--ausência-de-tratamento-de-erros)

---

## 1 — SQL Injection em todas as rotas

### 🔴 Problema

Todas as queries SQL do sistema são construídas via **interpolação direta de strings (f-strings)** com dados fornecidos pelo usuário, sem qualquer sanitização ou parametrização.

### 📌 Por que é um problema

SQL Injection é a **vulnerabilidade #1** do OWASP Top 10. Um atacante pode manipular qualquer campo de formulário ou parâmetro de URL para executar comandos SQL arbitrários, como: apagar tabelas inteiras, extrair dados sensíveis, ou até controlar o servidor.

### 🔍 Evidências

**`app.py` — rota `/nova_demanda`:**
```python
cursor.execute(
    f"INSERT INTO demandas (titulo, descricao, solicitante, data_criacao) VALUES ('{titulo}', '{descricao}', '{solicitante}', '{datetime.now()}')")
```

**`app.py` — rota `/editar/<id>`:**
```python
cursor.execute(
    f"UPDATE demandas SET titulo='{titulo}', descricao='{descricao}', solicitante='{solicitante}' WHERE id={id}")
```

**`app.py` — rota `/buscar`:**
```python
resultados = cursor.execute(f"SELECT * FROM demandas WHERE titulo LIKE '%{termo}%'").fetchall()
```

**`app.py` — rota `/deletar/<id>`:**
```python
cursor.execute(f'DELETE FROM demandas WHERE id={id}')
```

**`app.py` — rota `/adicionar_comentario/<demanda_id>`:**
```python
cursor.execute(
    f"INSERT INTO comentarios (demanda_id, comentario, autor, data) VALUES ({demanda_id}, '{comentario}', '{autor}', '{datetime.now()}')")
```

> Um usuário malicioso poderia, por exemplo, inserir no campo "título" o valor: `'; DROP TABLE demandas; --` e destruir toda a tabela.

### ✅ Como resolver

Usar **queries parametrizadas** com placeholders `?` em todas as operações SQL:

```python
cursor.execute(
    "INSERT INTO demandas (titulo, descricao, solicitante, data_criacao) VALUES (?, ?, ?, ?)",
    (titulo, descricao, solicitante, datetime.now())
)
```

### 🏆 Benefício para o sistema

Elimina completamente a classe de ataque mais crítica em aplicações web. Garante a **integridade dos dados**, protege contra **vazamento de informações** e torna o sistema seguro para uso em produção.

---

## 2 — Secret Key hardcoded e fraca

### 🔴 Problema

A `secret_key` do Flask está definida diretamente no código-fonte com o valor `'123456'`.

### 📌 Por que é um problema

A `secret_key` é usada para assinar cookies de sessão e mensagens flash. Com um valor trivial como `'123456'`, qualquer pessoa pode forjar sessões, tornando inútil qualquer mecanismo de autenticação futuro.

### 🔍 Evidências

**`app.py`:**
```python
app.secret_key = '123456'
```

### ✅ Como resolver

Usar uma chave gerada de forma segura e carregada via variável de ambiente:

```python
import os
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32).hex())
```

### 🏆 Benefício para o sistema

Garante que sessões não possam ser forjadas, protege mensagens flash contra adulteração e prepara o sistema para implementação futura de autenticação.

---

## 3 — Ausência de autenticação e autorização

### 🔴 Problema

O sistema não possui nenhum mecanismo de login, autenticação ou controle de acesso. Qualquer pessoa que acesse a URL pode criar, editar, deletar demandas e comentários.

### 📌 Por que é um problema

Em um sistema de gestão, é fundamental saber **quem** realizou cada ação. Sem autenticação, não há rastreabilidade, não há controle de permissões e qualquer pessoa na rede pode manipular dados.

### 🔍 Evidências

- Nenhuma rota verifica se o usuário está autenticado.
- A rota `/deletar/<id>` pode ser acessada diretamente por URL.
- A rota de admin está comentada e sem implementação:

```python
# @app.route('/admin')
# def admin():
#     return 'Área administrativa'
```

- O campo "autor" de comentários é preenchido manualmente pelo usuário sem verificação:

```html
<input type="text" name="autor" size="30">
```

### ✅ Como resolver

Implementar sistema de autenticação com `Flask-Login` ou similar:

```python
from flask_login import LoginManager, login_required, current_user

@app.route('/nova_demanda', methods=['GET', 'POST'])
@login_required
def nova_demanda():
    ...
```

### 🏆 Benefício para o sistema

Garante **rastreabilidade** de ações, impede acesso não autorizado, permite controle de permissões por perfil (admin, usuário, etc.) e atende a requisitos básicos de segurança.

---

## 4 — Deleção via método GET sem confirmação

### 🔴 Problema

A rota de deleção usa o método **GET** e não exige nenhuma confirmação do usuário.

### 📌 Por que é um problema

Operações que alteram estado (como exclusão) nunca devem usar GET, pois:
- Navegadores podem pré-carregar links GET (prefetch).
- Crawlers e bots podem disparar deleções acidentais.
- Não há proteção contra cliques acidentais.

### 🔍 Evidências

**`app.py`:**
```python
@app.route('/deletar/<id>')
def deletar(id):
    ...
    cursor.execute(f'DELETE FROM demandas WHERE id={id}')
```

**`index.html`:**
```html
<a href="/deletar/{{ demanda[0] }}" style="color:red;">Deletar</a>
```

> Um simples acesso a `/deletar/1` no navegador remove o registro permanentemente sem qualquer aviso.

### ✅ Como resolver

Usar método **POST** (ou DELETE) com formulário de confirmação:

```python
@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    ...
```

```html
<form method="POST" action="/deletar/{{ demanda[0] }}" 
      onsubmit="return confirm('Tem certeza que deseja deletar?')">
    <button type="submit" style="color:red;">Deletar</button>
</form>
```

### 🏆 Benefício para o sistema

Previne deleções acidentais, segue as convenções HTTP corretamente e protege contra ataques automatizados via URLs.

---

## 5 — Conexão com banco de dados sem gerenciamento adequado

### 🔴 Problema

O sistema abre conexões SQLite manualmente em cada rota e **não garante o fechamento em caso de erro**. Além disso, existe uma função `get_db()` com `row_factory` que nunca é utilizada.

### 📌 Por que é um problema

Se ocorrer uma exceção antes do `conn.close()`, a conexão ficará aberta indefinidamente, causando **vazamento de recursos** e possíveis travamentos do banco.

### 🔍 Evidências

**`app.py` — padrão repetido em todas as rotas:**
```python
conn = sqlite3.connect('demandas.db')
cursor = conn.cursor()
# ... operações ...
conn.close()  # não é chamado se ocorrer exceção antes
```

A função `get_db()` existe mas nunca é chamada:
```python
def get_db():
    conn = sqlite3.connect('demandas.db')
    conn.row_factory = sqlite3.Row
    return conn
```

### ✅ Como resolver

Usar **context manager** (`with`) ou o padrão `g` do Flask:

```python
from flask import g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('demandas.db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### 🏆 Benefício para o sistema

Garante que conexões são **sempre fechadas**, mesmo em caso de erro. Centraliza o gerenciamento do banco, elimina código duplicado e habilita o uso de `row_factory` para acesso por nome de coluna.

---

## 6 — Banco de dados sem chaves primárias, auto-incremento e foreign keys

### 🔴 Problema

As tabelas no banco não possuem `PRIMARY KEY`, `AUTOINCREMENT` ou `FOREIGN KEY`. Os IDs são inseridos manualmente.

### 📌 Por que é um problema

- Sem `PRIMARY KEY`, nada impede IDs duplicados.
- Sem `AUTOINCREMENT`, o sistema depende de controle manual de IDs, propenso a colisões.
- Sem `FOREIGN KEY`, comentários podem referenciar demandas inexistentes.

### 🔍 Evidências

**`init_db.py`:**
```python
cursor.execute('''
CREATE TABLE IF NOT EXISTS demandas (
    id INTEGER,          -- sem PRIMARY KEY
    titulo TEXT,
    descricao TEXT,
    solicitante TEXT,
    data_criacao TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS comentarios (
    id INTEGER,          -- sem PRIMARY KEY
    demanda_id INTEGER,  -- sem FOREIGN KEY
    comentario TEXT,
    autor TEXT,
    data TEXT
)
''')
```

Os IDs são inseridos manualmente e há um salto de `3` para `5`:
```python
cursor.execute("INSERT INTO demandas VALUES (1, ...)")
cursor.execute("INSERT INTO demandas VALUES (2, ...)")
cursor.execute("INSERT INTO demandas VALUES (3, ...)")
cursor.execute("INSERT INTO demandas VALUES (5, ...)")  # ID 4 não existe
```

### ✅ Como resolver

```python
cursor.execute('''
CREATE TABLE IF NOT EXISTS demandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    solicitante TEXT NOT NULL,
    data_criacao TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS comentarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    demanda_id INTEGER NOT NULL,
    comentario TEXT NOT NULL,
    autor TEXT NOT NULL,
    data TEXT NOT NULL,
    FOREIGN KEY (demanda_id) REFERENCES demandas(id) ON DELETE CASCADE
)
''')
```

### 🏆 Benefício para o sistema

Garante **integridade referencial**, evita dados duplicados ou órfãos, automatiza a geração de IDs e reforça constraints de NOT NULL para campos obrigatórios.

---

## 7 — Dados órfãos no banco de dados

### 🔴 Problema

O script de inicialização insere propositalmente um comentário que referencia uma demanda inexistente (`demanda_id=99`).

### 📌 Por que é um problema

Dados órfãos causam inconsistência, dificultam relatórios, ocupam espaço desnecessário e indicam falta de integridade referencial.

### 🔍 Evidências

**`init_db.py`:**
```python
cursor.execute("INSERT INTO comentarios VALUES (3, 99, 'Este comentário está órfão', 'Usuário', '2024-01-16 10:00:00')")
```

> Não existe nenhuma demanda com `id=99`, tornando esse comentário inacessível e sem contexto.

### ✅ Como resolver

1. Remover o registro órfão do script de seed.
2. Implementar `FOREIGN KEY` com `ON DELETE CASCADE` (conforme item 6).
3. Adicionar script de limpeza de dados órfãos:

```python
cursor.execute("DELETE FROM comentarios WHERE demanda_id NOT IN (SELECT id FROM demandas)")
```

### 🏆 Benefício para o sistema

Mantém a **consistência dos dados**, evita erros em listagens e relatórios, e garante que todo comentário esteja vinculado a uma demanda válida.

---

## 8 — Ausência de validação de entrada nos formulários

### 🔴 Problema

Nenhum campo de formulário possui validação — nem no front-end (HTML) nem no back-end (Python). É possível submeter formulários completamente vazios.

### 📌 Por que é um problema

Permite a criação de demandas e comentários com campos vazios, gerando dados inúteis no banco e degradando a qualidade da informação.

### 🔍 Evidências

**`nova_demanda.html`:**
```html
<input type="text" name="titulo" size="50">          <!-- sem required -->
<textarea name="descricao" rows="5" cols="50"></textarea>  <!-- sem required -->
<input type="text" name="solicitante">                <!-- sem required -->
```

**`app.py` — rota `/nova_demanda`:**
```python
titulo = request.form['titulo']       # aceita string vazia
descricao = request.form['descricao'] # aceita string vazia
solicitante = request.form['solicitante'] # aceita string vazia
# nenhuma validação antes do INSERT
```

### ✅ Como resolver

**Front-end** — adicionar atributo `required`:
```html
<input type="text" name="titulo" size="50" required>
```

**Back-end** — validar no servidor:
```python
titulo = request.form.get('titulo', '').strip()
if not titulo:
    flash('O campo título é obrigatório.')
    return redirect(url_for('nova_demanda'))
```

### 🏆 Benefício para o sistema

Garante **qualidade dos dados**, evita registros vazios ou inválidos e fornece feedback claro ao usuário quando dados obrigatórios estão faltando.

---

## 9 — XSS (Cross-Site Scripting) potencial

### 🔴 Problema

Os templates utilizam `{{ }}` do Jinja2 (que por padrão faz escape de HTML), porém os dados são inseridos diretamente no banco via SQL Injection (sem sanitização), o que pode criar vetores de ataque combinados. Além disso, o uso de `style` inline e HTML sem sanitização nos campos pode ser explorado.

### 📌 Por que é um problema

Embora o Jinja2 escape por padrão, se em algum momento `|safe` for adicionado (ou o template engine for alterado), dados maliciosos armazenados no banco seriam renderizados como HTML/JavaScript, permitindo roubo de sessão, redirecionamento malicioso etc.

### 🔍 Evidências

**`detalhes.html`** — renderiza dados diretamente do banco:
```html
<h3>{{ demanda[1] }}</h3>
<p>{{ demanda[2] }}</p>
<p>{{ comentario[2] }}</p>
```

Combinado com a falta de sanitização no back-end, um atacante pode inserir:
```
<script>alert('XSS')</script>
```
que ficará armazenado no banco. Embora o Jinja2 escape, a defesa é frágil por depender de apenas uma camada.

### ✅ Como resolver

Implementar **sanitização em múltiplas camadas**:

1. Validar e sanitizar entrada no back-end:
```python
import bleach
titulo = bleach.clean(request.form['titulo'])
```

2. Manter o escape padrão do Jinja2 (nunca usar `|safe` com dados de usuário).

3. Adicionar headers de segurança:
```python
@app.after_request
def set_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

### 🏆 Benefício para o sistema

Implementa **defesa em profundidade** contra injeção de scripts maliciosos, protegendo os usuários e a integridade da interface.

---

## 10 — Acesso a dados por índice numérico em vez de nome de coluna

### 🔴 Problema

Todos os templates acessam os dados das demandas e comentários usando **índices numéricos** (`demanda[0]`, `demanda[1]`, etc.), o que é frágil e ilegível.

### 📌 Por que é um problema

Se a ordem das colunas na tabela for alterada, ou se uma nova coluna for adicionada, **todos os templates quebram silenciosamente**, exibindo dados errados sem gerar erro.

### 🔍 Evidências

**`index.html`:**
```html
<td>{{ demanda[0] }}</td>   <!-- ID? -->
<td>{{ demanda[1] }}</td>   <!-- Título? -->
<td>{{ demanda[3] }}</td>   <!-- Solicitante? -->
<td>{{ demanda[4] }}</td>   <!-- Data? -->
```

**`detalhes.html`:**
```html
<h3>{{ demanda[1] }}</h3>
<p>{{ demanda[2] }}</p>
<p><strong>Solicitante:</strong> {{ demanda[3] }}</p>
```

> Não há como saber, olhando o template, qual coluna cada índice representa.

### ✅ Como resolver

Usar `row_factory = sqlite3.Row` (já definido na função `get_db()` não utilizada) e acessar por nome:

```html
<td>{{ demanda['id'] }}</td>
<td>{{ demanda['titulo'] }}</td>
<td>{{ demanda['solicitante'] }}</td>
<td>{{ demanda['data_criacao'] }}</td>
```

### 🏆 Benefício para o sistema

Código mais **legível e manutenível**. Alterações na estrutura do banco não quebram os templates. Facilita a colaboração entre desenvolvedores.

---

## 11 — Função `get_db()` definida mas não utilizada

### 🟡 Problema

Existe uma função `get_db()` que configura `row_factory` para acesso por nome de coluna, mas ela nunca é chamada em nenhuma rota.

### 📌 Por que é um problema

É **código morto** que confunde desenvolvedores. Indica que houve uma tentativa de padronização que foi abandonada. Enquanto isso, cada rota cria sua própria conexão de forma inconsistente.

### 🔍 Evidências

**`app.py`:**
```python
def get_db():
    conn = sqlite3.connect('demandas.db')
    conn.row_factory = sqlite3.Row  # configuração útil, mas não usada
    return conn

@app.route('/')
def index():
    conn = sqlite3.connect('demandas.db')  # conexão manual duplicada
    cursor = conn.cursor()
    ...
```

### ✅ Como resolver

Adotar `get_db()` em todas as rotas e remover conexões manuais duplicadas:

```python
@app.route('/')
def index():
    conn = get_db()
    demandas = conn.execute('SELECT * FROM demandas').fetchall()
    ...
```

### 🏆 Benefício para o sistema

Elimina **duplicação de código**, centraliza a configuração do banco, e habilita o uso de `row_factory` para acesso por nome de coluna em todos os templates.

---

## 12 — Função `calcular_prazo()` é placeholder sem uso

### 🟡 Problema

A função `calcular_prazo()` sempre retorna a string fixa `"30 dias"` e nunca é chamada em nenhuma parte do sistema.

### 📌 Por que é um problema

É código morto que gera confusão. Pode levar um desenvolvedor a acreditar que existe cálculo de prazo funcional, quando na verdade não há.

### 🔍 Evidências

**`app.py`:**
```python
def calcular_prazo(data_inicio):
    return "30 dias"
```

Nenhuma rota ou template referencia essa função.

### ✅ Como resolver

Remover a função ou implementá-la de fato:

```python
from datetime import datetime, timedelta

def calcular_prazo(data_inicio, dias=30):
    inicio = datetime.strptime(data_inicio, '%Y-%m-%d %H:%M:%S')
    prazo = inicio + timedelta(days=dias)
    return prazo.strftime('%d/%m/%Y')
```

### 🏆 Benefício para o sistema

Remove código morto, melhora a clareza do código-fonte e, se implementada, adiciona funcionalidade útil de **controle de prazos**.

---

## 13 — Aplicação rodando com `debug=True` e `host='0.0.0.0'`

### 🔴 Problema

O servidor Flask está configurado para rodar em modo debug, aceitando conexões de qualquer endereço IP.

### 📌 Por que é um problema

- **`debug=True`** expõe o debugger interativo do Werkzeug, que permite execução remota de código Python arbitrário.
- **`host='0.0.0.0'`** aceita conexões de qualquer máquina na rede.
- A combinação dos dois é **extremamente perigosa**.

### 🔍 Evidências

**`app.py`:**
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

### ✅ Como resolver

Usar variáveis de ambiente para controlar o modo:

```python
import os

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='127.0.0.1')
```

Para produção, usar um servidor WSGI como **Gunicorn**:
```bash
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

### 🏆 Benefício para o sistema

Impede **execução remota de código** via debugger, restringe o acesso à rede local e prepara o sistema para um deploy seguro em produção.

---

## 14 — URLs hardcoded nos templates

### 🟡 Problema

Todos os templates usam URLs escritas diretamente como strings em vez de usar a função `url_for()` do Flask.

### 📌 Por que é um problema

Se uma rota for renomeada ou o prefixo da aplicação mudar, **todos os links nos templates quebram** e precisam ser atualizados manualmente.

### 🔍 Evidências

**`detalhes.html`:**
```html
<a href="/editar/{{ demanda[0] }}"><button>Editar</button></a>
<a href="/"><button>Voltar</button></a>
```

**`index.html`:**
```html
<a href="/detalhes/{{ demanda[0] }}">Ver</a>
<a href="/editar/{{ demanda[0] }}">Editar</a>
<a href="/deletar/{{ demanda[0] }}" style="color:red;">Deletar</a>
```

**`base.html`:**
```html
<a href="/">Início</a>
<a href="/nova_demanda">Nova Demanda</a>
<form action="/buscar" method="GET">
```

### ✅ Como resolver

Usar `url_for()` em todos os templates:

```html
<a href="{{ url_for('editar', id=demanda['id']) }}">Editar</a>
<a href="{{ url_for('index') }}">Voltar</a>
<a href="{{ url_for('detalhes', id=demanda['id']) }}">Ver</a>
```

### 🏆 Benefício para o sistema

URLs geradas dinamicamente, **imunes a mudanças de rotas**. Facilita refatoração, deploy com prefixos e manutenção geral.

---

## 15 — Ausência de proteção CSRF nos formulários

### 🔴 Problema

Nenhum formulário possui token CSRF (Cross-Site Request Forgery).

### 📌 Por que é um problema

Um atacante pode criar uma página maliciosa que submete formulários para o SGDI em nome de um usuário legítimo, sem que este saiba.

### 🔍 Evidências

**Todos os formulários** (`nova_demanda.html`, `editar.html`, `detalhes.html`) não contêm token CSRF:

```html
<form method="POST" action="/nova_demanda">
    <!-- nenhum campo hidden com token CSRF -->
    <input type="text" name="titulo" size="50">
    ...
</form>
```

### ✅ Como resolver

Usar `Flask-WTF` que adiciona proteção CSRF automaticamente:

```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

```html
<form method="POST" action="/nova_demanda">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    ...
</form>
```

### 🏆 Benefício para o sistema

Impede que sites externos executem ações no SGDI em nome de usuários legítimos, protegendo contra **ataques CSRF**.

---

## 16 — Código administrativo comentado

### 🟡 Problema

Existe uma rota `/admin` comentada no código sem implementação.

### 📌 Por que é um problema

Código comentado polui o código-fonte e pode ser habilitado acidentalmente. Indica funcionalidade planejada mas não implementada, gerando dúvidas sobre o escopo.

### 🔍 Evidências

**`app.py`:**
```python
# @app.route('/admin')
# def admin():
#     return 'Área administrativa'
```

### ✅ Como resolver

Remover o código comentado. Se a funcionalidade for necessária, criar uma issue/tarefa e implementar adequadamente com autenticação.

### 🏆 Benefício para o sistema

Código mais limpo, sem ambiguidade sobre funcionalidades e sem risco de exposição acidental de rotas não protegidas.

---

## 17 — Estilo inline nos templates HTML

### 🟡 Problema

Os templates utilizam atributos de estilo inline e atributos HTML deprecados como `bgcolor`, `border`, `cellpadding`.

### 📌 Por que é um problema

Dificulta a manutenção visual, gera inconsistência de design, viola a separação de responsabilidades (HTML vs CSS) e usa atributos HTML que estão **deprecados** desde o HTML5.

### 🔍 Evidências

**`index.html`:**
```html
<table border="1" cellpadding="10" cellspacing="0" width="100%">
    <tr bgcolor="#cccccc">
```

**`detalhes.html`:**
```html
<div style="border:1px solid #ccc; padding:15px; margin-bottom:20px;">
<div style="background:#f0f0f0; padding:10px; margin:10px 0;">
```

**`index.html`:**
```html
<a href="/deletar/{{ demanda[0] }}" style="color:red;">Deletar</a>
```

### ✅ Como resolver

Mover todos os estilos para o arquivo `style.css` com classes semânticas:

```css
.demanda-card { border: 1px solid #ccc; padding: 15px; margin-bottom: 20px; }
.comentario { background: #f0f0f0; padding: 10px; margin: 10px 0; }
.btn-deletar { color: red; }
```

```html
<div class="demanda-card">
```

### 🏆 Benefício para o sistema

**Separação de responsabilidades**, facilidade de manutenção visual, consistência de design e conformidade com padrões HTML5 modernos.

---

## 18 — Footer fixo sobrepõe conteúdo da página

### 🟡 Problema

O footer usa `position: fixed` na parte inferior, o que faz com que ele sobreponha conteúdo da página quando há rolagem.

### 📌 Por que é um problema

Se a lista de demandas for grande, as últimas linhas da tabela ficarão **escondidas atrás do footer**, impossibilitando a leitura.

### 🔍 Evidências

**`style.css`:**
```css
.footer {
    background-color: #333;
    color: white;
    text-align: center;
    padding: 10px;
    position: fixed;
    bottom: 0;
    width: 100%;
}
```

### ✅ Como resolver

Adicionar `padding-bottom` ao body/container ou usar layout flexbox:

```css
body {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

.container {
    flex: 1;
    /* ...outros estilos... */
}

.footer {
    /* remover position: fixed */
    background-color: #333;
    color: white;
    text-align: center;
    padding: 10px;
}
```

### 🏆 Benefício para o sistema

Todo o conteúdo fica **visível e acessível**, o footer se posiciona naturalmente após o conteúdo e a experiência do usuário melhora significativamente.

---

## 19 — Falta de responsividade e acessibilidade

### 🟡 Problema

O sistema não possui viewport meta tag, media queries ou qualquer consideração de acessibilidade (ARIA labels, contraste adequado, etc.).

### 📌 Por que é um problema

O sistema será inutilizável em dispositivos móveis e não atende padrões de acessibilidade (WCAG), podendo excluir usuários com deficiência.

### 🔍 Evidências

**`base.html`** — ausência de viewport:
```html
<head>
    <title>SGDI - Sistema de Gestão de Demandas</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <!-- sem <meta name="viewport"> -->
    <!-- sem <meta charset="utf-8"> -->
    <!-- sem <html lang="pt-BR"> -->
```

**`style.css`** — nenhuma media query para responsividade.

### ✅ Como resolver

```html
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGDI</title>
```

Adicionar media queries no CSS e labels com `for` nos formulários.

### 🏆 Benefício para o sistema

Sistema acessível em **qualquer dispositivo**, conformidade com padrões web modernos e inclusão de usuários com necessidades de acessibilidade.

---

## 20 — Ausência de tratamento de erros

### 🔴 Problema

O sistema não possui tratamento de erros. Se uma demanda não for encontrada, uma consulta falhar ou um campo obrigatório estiver ausente, o sistema retorna erro 500 genérico.

### 📌 Por que é um problema

Usuários veem mensagens de erro técnicas incompreensíveis. Em modo debug, stack traces expõem informações sensíveis do sistema. Erros não são registrados em log.

### 🔍 Evidências

**`app.py` — rota `/detalhes/<id>`:**
```python
demanda = cursor.execute(f'SELECT * FROM demandas WHERE id={id}').fetchone()
# se demanda for None, o template vai dar erro ao acessar demanda[0]
```

Nenhuma rota tem `try/except`. Nenhum handler de erro está registrado:
```python
# Não existe:
# @app.errorhandler(404)
# @app.errorhandler(500)
```

### ✅ Como resolver

```python
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.route('/detalhes/<int:id>')
def detalhes(id):
    conn = get_db()
    demanda = conn.execute('SELECT * FROM demandas WHERE id = ?', (id,)).fetchone()
    if demanda is None:
        abort(404)
    ...
```

### 🏆 Benefício para o sistema

Experiência do usuário **muito mais amigável** em cenários de erro, proteção contra exposição de informações internas, e facilidade de diagnóstico com logs adequados.

---

## 📊 Resumo de Severidade

| # | Problema | Severidade | Categoria |
|---|----------|-----------|-----------|
| 1 | SQL Injection | 🔴 Crítica | Segurança |
| 2 | Secret Key hardcoded | 🔴 Crítica | Segurança |
| 3 | Sem autenticação | 🔴 Crítica | Segurança |
| 4 | DELETE via GET | 🔴 Alta | Segurança / Design |
| 5 | Conexão DB sem gerenciamento | 🟠 Alta | Arquitetura |
| 6 | Sem PKs, FKs, auto-increment | 🟠 Alta | Banco de Dados |
| 7 | Dados órfãos | 🟠 Média | Banco de Dados |
| 8 | Sem validação de entrada | 🔴 Alta | Segurança / UX |
| 9 | XSS potencial | 🟠 Alta | Segurança |
| 10 | Acesso por índice numérico | 🟡 Média | Manutenibilidade |
| 11 | `get_db()` não utilizada | 🟡 Baixa | Código Morto |
| 12 | `calcular_prazo()` sem uso | 🟡 Baixa | Código Morto |
| 13 | Debug=True + host 0.0.0.0 | 🔴 Crítica | Segurança |
| 14 | URLs hardcoded | 🟡 Média | Manutenibilidade |
| 15 | Sem proteção CSRF | 🔴 Alta | Segurança |
| 16 | Código comentado | 🟡 Baixa | Código Morto |
| 17 | Estilo inline / HTML deprecado | 🟡 Baixa | Design |
| 18 | Footer fixo sobrepõe conteúdo | 🟡 Média | UX / Design |
| 19 | Sem responsividade | 🟡 Média | UX / Acessibilidade |
| 20 | Sem tratamento de erros | 🔴 Alta | Robustez |

---

## 🎯 Prioridade de Resolução Sugerida

1. **Imediata:** Itens 1, 2, 3, 13 (vulnerabilidades críticas de segurança)
2. **Curto prazo:** Itens 4, 5, 6, 8, 15, 20 (segurança e integridade)
3. **Médio prazo:** Itens 7, 9, 10, 11, 14, 19 (qualidade e manutenibilidade)
4. **Longo prazo:** Itens 12, 16, 17, 18 (melhorias e limpeza)

