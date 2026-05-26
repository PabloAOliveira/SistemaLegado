"""Operações genéricas de banco de dados."""
import sqlite3
from contextlib import closing
from config import DATABASE_PATH
from flask import current_app


def get_db():
    """Retorna uma conexão com o banco de dados."""
    return closing(sqlite3.connect(DATABASE_PATH))


def fetch_all(query, params=()):
    """Executa uma query e retorna todos os resultados."""
    with get_db() as conn:
        cursor = conn.cursor()
        return cursor.execute(query, params).fetchall()


def fetch_one(query, params=()):
    """Executa uma query e retorna um resultado."""
    with get_db() as conn:
        cursor = conn.cursor()
        return cursor.execute(query, params).fetchone()


def execute_query(query, params=()):
    """Executa uma query com commit automático."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()


def log_db_error(operation, error, **context):
    """Loga erros de banco de dados."""
    context_str = ", ".join(f"{key}={value!r}" for key, value in context.items())
    current_app.logger.exception("Database error during %s (%s): %s", operation, context_str, error)

