import os
import sqlite3
import secrets
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for
from dotenv import load_dotenv

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


def get_db():
    return sqlite3.connect(DATABASE_PATH)


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


@app.route('/', methods=['GET'])
def index():
    demandas = fetch_all("SELECT * FROM demandas")
    return render_template('index.html', demandas=demandas)


@app.route('/nova_demanda', methods=['GET', 'POST'])
def nova_demanda():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        solicitante = request.form['solicitante']

        try:
            execute_query(
                "INSERT INTO demandas (titulo, descricao, solicitante, data_criacao) VALUES (?, ?, ?, ?)",
                (titulo, descricao, solicitante, str(datetime.now())),
            )
        except sqlite3.Error as error:
            log_db_error("nova_demanda", error, solicitante=solicitante)
            flash('Erro ao salvar demanda!')
            return redirect(url_for('nova_demanda'))

        flash('Salvo!')
        return redirect(url_for('index'))

    return render_template('nova_demanda.html')


@app.route('/editar/<int:demanda_id>', methods=['GET', 'POST'])
def editar(demanda_id):
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        solicitante = request.form['solicitante']

        try:
            execute_query(
                "UPDATE demandas SET titulo = ?, descricao = ?, solicitante = ? WHERE id = ?",
                (titulo, descricao, solicitante, demanda_id),
            )
        except sqlite3.Error as error:
            log_db_error("editar", error, demanda_id=demanda_id, solicitante=solicitante)
            flash('Erro ao atualizar demanda!')
            return redirect(url_for('editar', demanda_id=demanda_id))

        return redirect(url_for('index'))

    demanda = fetch_one('SELECT * FROM demandas WHERE id = ?', (demanda_id,))
    return render_template('editar.html', demanda=demanda)


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
        'SELECT * FROM demandas WHERE titulo LIKE ?',
        (like_term,),
    )
    return render_template('index.html', demandas=resultados)


@app.route('/detalhes/<int:demanda_id>', methods=['GET'])
def detalhes(demanda_id):
    demanda = fetch_one('SELECT * FROM demandas WHERE id = ?', (demanda_id,))
    comentarios = fetch_all('SELECT * FROM comentarios WHERE demanda_id = ?', (demanda_id,))

    return render_template('detalhes.html', demanda=demanda, comentarios=comentarios)


@app.route('/adicionar_comentario/<int:demanda_id>', methods=['POST'])
def adicionar_comentario(demanda_id):
    comentario = request.form['comentario']
    autor = request.form['autor']

    try:
        execute_query(
            'INSERT INTO comentarios (demanda_id, comentario, autor, data) VALUES (?, ?, ?, ?)',
            (demanda_id, comentario, autor, str(datetime.now())),
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
