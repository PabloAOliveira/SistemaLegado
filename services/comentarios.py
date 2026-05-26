"""Serviços relacionados a comentários."""
import sqlite3
from db import fetch_all, execute_query, log_db_error
from services.utils import date_now


def get_comentarios(demanda_id):
    """Retorna todos os comentários de uma demanda."""
    return fetch_all('SELECT * FROM comentarios WHERE demanda_id = ?', (demanda_id,))


def create_comentario(demanda_id, comentario, autor):
    """Cria um novo comentário."""
    try:
        execute_query(
            'INSERT INTO comentarios (demanda_id, comentario, autor, data) VALUES (?, ?, ?, ?)',
            (demanda_id, comentario, autor, str(date_now())),
        )
        return True
    except sqlite3.Error as error:
        log_db_error("create_comentario", error, demanda_id=demanda_id, autor=autor)
        return False

