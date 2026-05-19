import os
import sqlite3
import secrets
import datetime
from contextlib import closing
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import db

app = Flask(__name__)
load_dotenv()
flask_secret_key = os.getenv("FLASK_SECRET_KEY")

if not flask_secret_key:
    # Enforce explicit configuration in production
    if os.getenv("FLASK_ENV") == "production":
        raise RuntimeError(
            "FLASK_SECRET_KEY environment variable must be set in production."
        )
    # For non-production environments, generate a strong random key
    flask_secret_key = secrets.token_hex(32)

app.secret_key = flask_secret_key
DATABASE_PATH = os.getenv('DATABASE_PATH', 'demandas.db')

database_path_abs = os.path.abspath(DATABASE_PATH)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path_abs}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

DEFAULT_REQUESTERS = (
    {"nome": "Joao Silva", "email": "joao.silva@empresa.com", "cargo": "Analista"},
    {"nome": "Maria Santos", "email": "maria.santos@empresa.com", "cargo": "Coordenadora"},
)

EXCLUDED_REQUESTER_NAMES = frozenset({
    "Tech Team",
    "Equipe Suporte",
    "Time Produto",
})


def get_db():
    return closing(sqlite3.connect(DATABASE_PATH))


def fetch_all(query, params=()):
    with get_db() as conn:
        cursor = conn.cursor()
        return cursor.execute(query, params).fetchall()


def fetch_one(query, params=()):
    with get_db() as conn:
        cursor = conn.cursor()
        return cursor.execute(query, params).fetchone()


def execute_query(query, params=()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()


def log_db_error(operation, error, **context):
    context_str = ", ".join(f"{key}={value!r}" for key, value in context.items())
    app.logger.exception("Database error during %s (%s): %s", operation, context_str, error)


def date_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def remove_excluded_requesters():
    for name in EXCLUDED_REQUESTER_NAMES:
        execute_query("DELETE FROM requesters WHERE nome = ?", (name,))


def ensure_requesters_table_seeded():
    execute_query(
        """
        CREATE TABLE IF NOT EXISTS requesters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            cargo TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
        """
    )

    remove_excluded_requesters()

    row = fetch_one("SELECT COUNT(1) FROM requesters")
    count = row[0] if row else 0

    if count == 0:
        now = date_now()
        for requester in DEFAULT_REQUESTERS:
            execute_query(
                """
                INSERT INTO requesters (nome, email, cargo, data_criacao)
                VALUES (?, ?, ?, ?)
                """,
                (requester["nome"], requester["email"], requester["cargo"], now),
            )


def get_requesters():
    ensure_requesters_table_seeded()
    rows = fetch_all(
        """
        SELECT id, nome, email, cargo
        FROM requesters
        ORDER BY nome COLLATE NOCASE ASC
        """
    )
    return [
        {"id": row[0], "nome": row[1], "email": row[2], "cargo": row[3]}
        for row in rows
        if row[1] not in EXCLUDED_REQUESTER_NAMES
    ]


def get_requester_by_id(requester_id):
    ensure_requesters_table_seeded()
    row = fetch_one(
        """
        SELECT id, nome, email, cargo, data_criacao
        FROM requesters
        WHERE id = ?
        """,
        (requester_id,),
    )
    if not row:
        return None
    return {"id": row[0], "nome": row[1], "email": row[2], "cargo": row[3], "data_criacao": row[4]}


def get_available_people():
    # Placeholder for the future login integration that will hydrate this list.
    normalized_people = []

    for requester in get_requesters():
        name = str(requester.get("nome", "")).strip()
        if name and name not in EXCLUDED_REQUESTER_NAMES and name not in normalized_people:
            normalized_people.append(name)

    return normalized_people


def is_valid_person(name):
    return name in get_available_people()


def get_usuario_logado():
    usuario = str(session.get('usuario_atual', '')).strip()
    if usuario in EXCLUDED_REQUESTER_NAMES:
        session.pop('usuario_atual', None)
        return ''
    return usuario


def is_demanda_responsavel(demanda, usuario):
    solicitante = str(demanda[3] or '').strip()
    return bool(usuario) and usuario == solicitante


@app.context_processor
def inject_usuario_atual():
    return {
        'usuario_atual': get_usuario_logado(),
        'people': get_available_people(),
    }


@app.route('/definir-usuario', methods=['POST'])
def definir_usuario():
    usuario = request.form.get('usuario', '').strip()
    if usuario:
        if not is_valid_person(usuario):
            flash('Selecione um usuario valido!', 'error')
        else:
            session['usuario_atual'] = usuario
    else:
        session.pop('usuario_atual', None)

    return redirect(request.referrer or url_for('index'))


@app.route('/', methods=['GET'])
def index():
    prioridade_filtro = request.args.get('prioridade', 'todas').strip().lower()
    
    if prioridade_filtro == 'todas' or not prioridade_filtro:
        demandas = fetch_all("""
                             SELECT *
                             FROM demandas
                             ORDER BY CASE LOWER(prioridade)
                                          WHEN 'alta' THEN 1
                                          WHEN 'média' THEN 2
                                          WHEN 'media' THEN 2
                                          WHEN 'baixa' THEN 3
                                          ELSE 4
                                          END,
                                      data_criacao DESC
                             """)
    else:
        demandas = fetch_all("""
                             SELECT *
                             FROM demandas
                             WHERE LOWER(prioridade) = ?
                             ORDER BY data_criacao DESC
                             """, (prioridade_filtro,))
    
    return render_template('index.html', demandas=demandas, prioridade_filtro=prioridade_filtro)

@app.route('/nova_demanda', methods=['GET', 'POST'])
def nova_demanda():
    people = get_available_people()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        solicitante = request.form['solicitante'].strip()
        prioridade = request.form['prioridade']

        if not is_valid_person(solicitante):
            flash('Selecione um solicitante valido!', 'error')
            return render_template(
                'nova_demanda.html',
                people=people,
                form_data=request.form,
            )

        try:
            execute_query(
                "INSERT INTO demandas (titulo, descricao, solicitante, prioridade, data_criacao) VALUES (?, ?, ?, ?, ?)",
                (titulo, descricao, solicitante, prioridade, str(date_now())),
            )
        except sqlite3.Error as error:
            log_db_error("nova_demanda", error, solicitante=solicitante)
            flash('Erro ao salvar demanda!')
            return redirect(url_for('nova_demanda'))

        flash('Salvo!')
        return redirect(url_for('index'))

    return render_template('nova_demanda.html', people=people, form_data={})


@app.route('/editar/<int:demanda_id>', methods=['GET', 'POST'])
def editar(demanda_id):
    people = get_available_people()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        prioridade = request.form['prioridade']
        solicitante = request.form['solicitante'].strip()

        if not is_valid_person(solicitante):
            flash('Selecione um solicitante valido!', 'error')
            demanda = fetch_one('SELECT * FROM demandas WHERE id = ?', (demanda_id,))
            return render_template(
                'editar.html',
                demanda=demanda,
                people=people,
                form_data=request.form,
            )

        try:
            execute_query(
                "UPDATE demandas SET titulo = ?, descricao = ?, prioridade = ?, solicitante = ? WHERE id = ?",
                (titulo, descricao, prioridade, solicitante, demanda_id),
            )
        except sqlite3.Error as error:
            log_db_error("editar", error, demanda_id=demanda_id, solicitante=solicitante)
            flash('Erro ao atualizar demanda!')
            return redirect(url_for('editar', demanda_id=demanda_id))

        flash('Atualizado!')
        return redirect(url_for('index'))

    demanda = fetch_one('SELECT * FROM demandas WHERE id = ?', (demanda_id,))
    return render_template('editar.html', demanda=demanda, people=people, form_data={})


@app.route('/deletar/<int:demanda_id>', methods=['DELETE'])
def deletar(demanda_id):
    demanda = fetch_one('SELECT * FROM demandas WHERE id = ?', (demanda_id,))
    if not demanda:
        flash('Demanda nao encontrada!', 'error')
        return redirect(url_for('index'))

    usuario = get_usuario_logado()
    if not usuario:
        flash('Selecione quem voce e no menu antes de deletar uma demanda!', 'error')
        return redirect(url_for('index'))

    if not is_demanda_responsavel(demanda, usuario):
        flash('Apenas o responsavel da demanda pode deleta-la!', 'error')
        return redirect(url_for('index'))

    try:
        execute_query('DELETE FROM demandas WHERE id = ?', (demanda_id,))
    except sqlite3.Error as error:
        log_db_error("deletar", error, demanda_id=demanda_id)
        flash('Erro ao deletar demanda!')
        return redirect(url_for('index'))

    flash('Deletado!')
    return redirect(url_for('index'))


@app.route('/buscar', methods=['GET'])
def buscar():
    termo = request.args.get('q', '').strip()
    like_term = f"%{termo}%"

    resultados = fetch_all(
        '''SELECT * FROM demandas 
           WHERE titulo LIKE ? 
           OR id LIKE ?
           OR solicitante LIKE ?''',
        (like_term, like_term, like_term),
    )
    return render_template('index.html', demandas=resultados)


@app.route('/detalhes/<int:demanda_id>', methods=['GET'])
def detalhes(demanda_id):
    demanda = fetch_one('SELECT * FROM demandas WHERE id = ?', (demanda_id,))
    comentarios = fetch_all('SELECT * FROM comentarios WHERE demanda_id = ?', (demanda_id,))

    return render_template(
        'detalhes.html',
        demanda=demanda,
        comentarios=comentarios,
        people=get_available_people(),
        form_data={},
    )


@app.route('/solicitante', methods=['GET'])
def solicitante():
    requesters = get_requesters()
    
    # Count de chamados por solicitante
    dados = fetch_all("""
        SELECT solicitante, COUNT(*) as total
        FROM demandas
        GROUP BY solicitante
        ORDER BY total DESC
    """)
    
    # Formata para o gráfico
    categorias = [row[0] for row in dados]
    totais = [row[1] for row in dados]
    
    return render_template('solicitante.html', 
                         requesters=requesters,
                         categorias=categorias,
                         totais=totais)


@app.route('/sutita', methods=['GET'])
def sutita():
    return render_template('sutita.html')


@app.route('/solicitante/<int:requester_id>', methods=['GET'])
def detalhes_solicitante(requester_id):
    requester = get_requester_by_id(requester_id)
    if not requester:
        flash('Solicitante não encontrado!', 'error')
        return redirect(url_for('solicitante'))
    return render_template('detalhes_solicitante.html', requester=requester)


@app.route('/solicitante/editar/<int:requester_id>', methods=['GET', 'POST'])
def editar_solicitante(requester_id):
    requester = get_requester_by_id(requester_id)
    if not requester:
        flash('Solicitante não encontrado!', 'error')
        return redirect(url_for('solicitante'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        cargo = request.form.get('cargo', '').strip()

        if not nome or not email or not cargo:
            flash('Preencha nome, email e cargo para salvar!', 'error')
            return render_template('editar_solicitante.html', requester=requester, form_data=request.form)

        if len(nome) > 40 or len(email) > 40 or len(cargo) > 40:
            flash('Nome, email e cargo devem ter no máximo 40 caracteres.', 'error')
            return render_template('editar_solicitante.html', requester=requester, form_data=request.form)

        try:
            execute_query(
                """
                UPDATE requesters
                SET nome = ?, email = ?, cargo = ?
                WHERE id = ?
                """,
                (nome, email, cargo, requester_id),
            )
        except sqlite3.IntegrityError:
            flash('Já existe solicitante cadastrado com este email!', 'error')
            return render_template('editar_solicitante.html', requester=requester, form_data=request.form)
        except sqlite3.Error as error:
            log_db_error("editar_solicitante", error, requester_id=requester_id, email=email)
            flash('Erro ao editar solicitante!', 'error')
            return render_template('editar_solicitante.html', requester=requester, form_data=request.form)

        flash('Solicitante atualizado com sucesso!', 'success')
        return redirect(url_for('solicitante'))

    return render_template('editar_solicitante.html', requester=requester, form_data={})


@app.route('/solicitante/deletar/<int:requester_id>', methods=['DELETE'])
def deletar_solicitante(requester_id):
    requester = get_requester_by_id(requester_id)
    if not requester:
        return ('', 404)

    try:
        execute_query("DELETE FROM requesters WHERE id = ?", (requester_id,))
    except sqlite3.Error as error:
        log_db_error("deletar_solicitante", error, requester_id=requester_id)
        return ('', 500)

    return ('', 204)


@app.route('/solicitante/cadastrar', methods=['GET', 'POST'])
def cadastrar_solicitante():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        email = request.form['email'].strip()
        cargo = request.form['cargo'].strip()

        if not nome or not email or not cargo:
            flash('Preencha nome, email e cargo para cadastrar!', 'error')
            return render_template('cadastrar_solicitante.html', form_data=request.form)

        if len(nome) > 40 or len(email) > 40 or len(cargo) > 40:
            flash('Nome, email e cargo devem ter no máximo 40 caracteres.', 'error')
            return render_template('cadastrar_solicitante.html', form_data=request.form)

        try:
            execute_query(
                """
                INSERT INTO requesters (nome, email, cargo, data_criacao)
                VALUES (?, ?, ?, ?)
                """,
                (nome, email, cargo, str(date_now())),
            )
        except sqlite3.IntegrityError:
            flash('Ja existe solicitante cadastrado com este email!', 'error')
            return render_template('cadastrar_solicitante.html', form_data=request.form)
        except sqlite3.Error as error:
            log_db_error("cadastrar_solicitante", error, nome=nome, email=email)
            flash('Erro ao cadastrar solicitante!', 'error')
            return render_template('cadastrar_solicitante.html', form_data=request.form)

        flash('Solicitante cadastrado com sucesso!', 'success')
        return redirect(url_for('solicitante'))

    return render_template('cadastrar_solicitante.html', form_data={})


@app.route('/adicionar_comentario/<int:demanda_id>', methods=['POST'])
def adicionar_comentario(demanda_id):
    comentario = request.form['comentario'].strip()
    autor = request.form['autor'].strip()

    if not is_valid_person(autor):
        flash('Selecione um autor valido para o comentario!', 'error')
        demanda = fetch_one('SELECT * FROM demandas WHERE id = ?', (demanda_id,))
        comentarios = fetch_all('SELECT * FROM comentarios WHERE demanda_id = ?', (demanda_id,))
        return render_template(
            'detalhes.html',
            demanda=demanda,
            comentarios=comentarios,
            people=get_available_people(),
            form_data=request.form,
        )

    if not comentario:
        flash('Escreva um comentario antes de enviar!', 'error')
        demanda = fetch_one('SELECT * FROM demandas WHERE id = ?', (demanda_id,))
        comentarios = fetch_all('SELECT * FROM comentarios WHERE demanda_id = ?', (demanda_id,))
        return render_template(
            'detalhes.html',
            demanda=demanda,
            comentarios=comentarios,
            people=get_available_people(),
            form_data=request.form,
        )

    try:
        execute_query(
            'INSERT INTO comentarios (demanda_id, comentario, autor, data) VALUES (?, ?, ?, ?)',
            (demanda_id, comentario, autor, str(date_now())),
        )
    except sqlite3.Error as error:
        log_db_error("adicionar_comentario", error, demanda_id=demanda_id, autor=autor)
        flash('Erro ao adicionar comentário!')

    return redirect(url_for('detalhes', demanda_id=demanda_id))


if __name__ == '__main__':
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").strip().lower() in ("1", "true", "yes", "on")
    app.run(debug=debug, host=host, port=port)
