"""Serviços relacionados a solicitantes (requesters)."""
import sqlite3
from config import DEFAULT_REQUESTERS
from db import fetch_all, fetch_one, execute_query, log_db_error
from services.utils import date_now


def ensure_requesters_table_seeded():
    """Garante que a tabela de solicitantes existe e está populada."""
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
    """Retorna lista de todos os solicitantes."""
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
    """Busca um solicitante por ID."""
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
    """Retorna lista de pessoas disponíveis (a partir de solicitantes)."""
    normalized_people = []
    for requester in get_requesters():
        name = str(requester.get("nome", "")).strip()
        if name and name not in normalized_people:
            normalized_people.append(name)
    return normalized_people


def is_valid_person(name):
    """Verifica se uma pessoa é válida (está na lista de solicitantes)."""
    return name in get_available_people()


def update_requester(requester_id, nome, email, cargo):
    """Atualiza dados de um solicitante."""
    try:
        execute_query(
            """
            UPDATE requesters
            SET nome = ?, email = ?, cargo = ?
            WHERE id = ?
            """,
            (nome, email, cargo, requester_id),
        )
        return True
    except sqlite3.IntegrityError:
        return False  # Email duplicado


def create_requester(nome, email, cargo):
    """Cria um novo solicitante."""
    try:
        execute_query(
            """
            INSERT INTO requesters (nome, email, cargo, data_criacao)
            VALUES (?, ?, ?, ?)
            """,
            (nome, email, cargo, str(date_now())),
        )
        return True
    except sqlite3.IntegrityError:
        return False  # Email duplicado


def delete_requester(requester_id):
    """Deleta um solicitante."""
    execute_query("DELETE FROM requesters WHERE id = ?", (requester_id,))

