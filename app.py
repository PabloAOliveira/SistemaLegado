import os
import io
import json
import base64
import sqlite3
import secrets
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from contextlib import closing
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
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
    {"nome": "Tech Team", "email": "tech.team@empresa.com", "cargo": "Equipe Tecnica"},
    {"nome": "Equipe Suporte", "email": "suporte@empresa.com", "cargo": "Suporte"},
    {"nome": "Time Produto", "email": "produto@empresa.com", "cargo": "Produto"},
)


# ---------------------------------------------------------------------------
# Plotly helpers
# ---------------------------------------------------------------------------
_PALETTE_PRIORITY = {
    'alta':  '#e05252',
    'media': '#e0a84d',
    'baixa': '#52a8e0',
    'sem prioridade': '#9e9e9e',
}

_PALETTE_STATUS = {
    'Aberto':       '#52a8e0',
    'Em Andamento': '#e0a84d',
    'Concluido':    '#5ac87a',
    'Cancelado':    '#e05252',
}

_PALETTE_BAR = [
    '#4f8ef7', '#a78bfa', '#34d399', '#f97316',
    '#fb7185', '#facc15', '#22d3ee', '#e879f9',
]

def _apply_dark_layout(fig, title):
    BG, FG, GRID = '#1e2330', '#c9d1d9', '#2d3448'
    fig.update_layout(
        title={'text': title, 'font': {'color': FG, 'size': 14, 'family': 'sans-serif'}, 'x': 0.5, 'xanchor': 'center'},
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font={'color': FG},
        margin=dict(t=50, b=20, l=10, r=10),
        xaxis=dict(showgrid=False, gridcolor=GRID, zeroline=False, automargin=True),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, automargin=True),
        autosize=True
    )
    return fig

def gerar_graficos():
    """Gera os 4 graficos usando Plotly e retorna JSON objects."""
    resultado = {}

    # 1. Chamados por Solicitante (barras horizontais)
    dados_sol = fetch_all("""
        SELECT solicitante, COUNT(*) as total
        FROM demandas
        WHERE solicitante IS NOT NULL AND solicitante != ''
        GROUP BY solicitante
        ORDER BY total ASC
        LIMIT 10
    """)
    if dados_sol:
        df = pd.DataFrame(dados_sol, columns=['Solicitante', 'Total'])
        fig = px.bar(df, x='Total', y='Solicitante', orientation='h', text='Total',
                     color='Solicitante', color_discrete_sequence=_PALETTE_BAR)
        fig.update_layout(showlegend=False, xaxis_title="Número de Chamados", yaxis_title="")
        fig.update_traces(textposition='outside')
        fig = _apply_dark_layout(fig, 'Chamados por Solicitante')
        resultado['por_solicitante'] = json.loads(fig.to_json())
    else:
        resultado['por_solicitante'] = None

    # 2. Por Prioridade (pizza)
    dados_prio = fetch_all("""
        SELECT COALESCE(NULLIF(prioridade,''), 'sem prioridade') as prio,
               COUNT(*) as total
        FROM demandas
        GROUP BY prio
        ORDER BY total DESC
    """)
    if dados_prio:
        df = pd.DataFrame(dados_prio, columns=['Prioridade', 'Total'])
        cores = [ _PALETTE_PRIORITY.get(p.lower(), '#9e9e9e') for p in df['Prioridade'] ]
        fig = px.pie(df, values='Total', names='Prioridade',
                     color_discrete_sequence=cores, hole=0.3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig = _apply_dark_layout(fig, 'Chamados por Prioridade')
        resultado['por_prioridade'] = json.loads(fig.to_json())
    else:
        resultado['por_prioridade'] = None

    # 3. Por Status (barras verticais)
    dados_status = fetch_all("""
        SELECT COALESCE(NULLIF(status,''), 'Aberto') as st,
               COUNT(*) as total
        FROM demandas
        GROUP BY st
        ORDER BY total DESC
    """)
    if dados_status:
        df = pd.DataFrame(dados_status, columns=['Status', 'Total'])
        cores = [ _PALETTE_STATUS.get(s, '#9e9e9e') for s in df['Status'] ]
        fig = px.bar(df, x='Status', y='Total', text='Total',
                     color='Status', color_discrete_sequence=cores)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Número de Chamados")
        fig.update_traces(textposition='outside')
        fig = _apply_dark_layout(fig, 'Chamados por Status')
        fig.update_layout(xaxis=dict(showgrid=False))
        resultado['por_status'] = json.loads(fig.to_json())
    else:
        resultado['por_status'] = None

    # 4. Evolucao Temporal (linha por mes)
    dados_temp = fetch_all("""
        SELECT substr(data_criacao, 1, 7) as mes, COUNT(*) as total
        FROM demandas
        WHERE data_criacao IS NOT NULL AND data_criacao != ''
        GROUP BY mes
        ORDER BY mes ASC
        LIMIT 24
    """)
    if dados_temp:
        df = pd.DataFrame(dados_temp, columns=['Mês', 'Total'])
        fig = px.line(df, x='Mês', y='Total', markers=True, text='Total')
        fig.update_traces(line=dict(color='#4f8ef7', width=3), 
                          marker=dict(size=8, color='#a78bfa'),
                          textposition="top center")
        fig.update_layout(xaxis_title="", yaxis_title="Número de Chamados")
        fig = _apply_dark_layout(fig, 'Evolução Temporal de Chamados')
        resultado['evolucao_temporal'] = json.loads(fig.to_json())
    else:
        resultado['evolucao_temporal'] = None

    return resultado



# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------
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
    return [{"id": row[0], "nome": row[1], "email": row[2], "cargo": row[3]} for row in rows]


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
        if name and name not in normalized_people:
            normalized_people.append(name)

    return normalized_people


def is_valid_person(name):
    return name in get_available_people()


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
    graficos = gerar_graficos()
    return render_template('solicitante.html',
                           requesters=requesters,
                           graficos=graficos)


@app.route('/solicitante/graficos', methods=['GET'])
def solicitante_graficos_api():
    """API para atualizacao dinamica dos graficos via fetch()."""
    return jsonify(gerar_graficos())


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
