import sqlite3
from pathlib import Path

import pytest

import app as app_module


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """Create an isolated SQLite database for each test."""
    database_path = tmp_path / "demandas_test.db"

    conn = sqlite3.connect(str(database_path))
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE demandas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            descricao TEXT,
            solicitante TEXT,
            data_criacao TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE comentarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demanda_id INTEGER,
            comentario TEXT,
            autor TEXT,
            data TEXT
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO demandas (id, titulo, descricao, solicitante, data_criacao)
        VALUES (1, 'Corrigir bug no login', 'Usuários nao conseguem fazer login', 'Joao Silva', '2024-01-15 10:30:00')
        """
    )
    cursor.execute(
        """
        INSERT INTO demandas (id, titulo, descricao, solicitante, data_criacao)
        VALUES (2, 'Implementar relatório de vendas', 'Precisamos de um relatório mensal', 'Maria Santos', '2024-01-16 14:20:00')
        """
    )
    cursor.execute(
        """
        INSERT INTO comentarios (id, demanda_id, comentario, autor, data)
        VALUES (1, 1, 'Vou investigar esse bug', 'Tech Team', '2024-01-15 11:00:00')
        """
    )

    conn.commit()
    conn.close()

    return database_path


@pytest.fixture
def client(db_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Provide a Flask test client with SQLite connections redirected to a temp DB."""
    original_connect = sqlite3.connect

    def connect_override(_database, *args, **kwargs):
        return original_connect(str(db_path), *args, **kwargs)

    monkeypatch.setattr(app_module.sqlite3, "connect", connect_override)
    app_module.app.config.update(TESTING=True, SECRET_KEY="test-secret-key")

    with app_module.app.test_client() as test_client:
        yield test_client
