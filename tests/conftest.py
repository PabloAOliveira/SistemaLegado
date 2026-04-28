import sqlite3
import sys
from pathlib import Path

import pytest

# Adiciona o diretório raiz ao PYTHONPATH para importar app.py
sys.path.insert(0, str(Path(__file__).parent.parent))

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
            prioridade TEXT,
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
        CREATE TABLE requesters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            cargo TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO demandas (id, titulo, descricao, solicitante, prioridade, data_criacao)
        VALUES (1, 'Corrigir bug no login', 'Usuários nao conseguem fazer login', 'Joao Silva', 'alta', '2024-01-15 10:30:00')
        """
    )
    cursor.execute(
        """
        INSERT INTO demandas (id, titulo, descricao, solicitante, prioridade, data_criacao)
        VALUES (2, 'Implementar relatório de vendas', 'Precisamos de um relatório mensal', 'Maria Santos', 'media', '2024-01-16 14:20:00')
        """
    )
    cursor.execute(
        """
        INSERT INTO comentarios (id, demanda_id, comentario, autor, data)
        VALUES (1, 1, 'Vou investigar esse bug', 'Tech Team', '2024-01-15 11:00:00')
        """
    )
    cursor.execute(
        """
        INSERT INTO requesters (id, nome, email, cargo, data_criacao)
        VALUES
          (1, 'Joao Silva', 'joao.silva@empresa.com', 'Analista', '2024-01-15 09:00:00'),
          (2, 'Maria Santos', 'maria.santos@empresa.com', 'Coordenadora', '2024-01-15 09:05:00'),
          (3, 'Tech Team', 'tech.team@empresa.com', 'Equipe Tecnica', '2024-01-15 09:10:00')
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
    app_module.app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
    )

    with app_module.app.test_client() as test_client:
        yield test_client
