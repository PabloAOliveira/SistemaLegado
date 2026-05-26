import sqlite3
import sys
import hashlib
import os
from pathlib import Path

import pytest

# Adiciona o diretório raiz ao PYTHONPATH para importar app.py
sys.path.insert(0, str(Path(__file__).parent.parent))

import app as app_module
import db as db_module
from API_EXTERNA.api import create_api_app


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
            data_criacao TEXT,
            status TEXT,
            responsavel TEXT,
            prazo TEXT,
            data_conclusao TEXT
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
        CREATE TABLE system_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            token TEXT NOT NULL,
            token_salt TEXT NOT NULL,
            user_type TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO demandas (id, titulo, descricao, solicitante, prioridade, data_criacao, status, responsavel, prazo, data_conclusao)
        VALUES (1, 'Corrigir bug no login', 'Usuários nao conseguem fazer login', 'Joao Silva', 'alta', '2024-01-15 10:30:00', 'aberta', 'Tech Team', '2024-01-22', NULL)
        """
    )
    cursor.execute(
        """
        INSERT INTO demandas (id, titulo, descricao, solicitante, prioridade, data_criacao, status, responsavel, prazo, data_conclusao)
        VALUES (2, 'Implementar relatório de vendas', 'Precisamos de um relatório mensal', 'Maria Santos', 'media', '2024-01-16 14:20:00', 'concluida', 'Tech Team', '2024-01-23', '2024-01-20 15:00:00')
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
          (3, 'Tech Team', 'tech.team@empresa.com', 'Equipe Tecnica', '2024-01-15 09:10:00'),
          (4, 'Equipe Suporte', 'suporte@empresa.com', 'Suporte', '2024-01-15 09:15:00'),
          (5, 'Time Produto', 'produto@empresa.com', 'Produto', '2024-01-15 09:20:00')
        """
    )

    # Create system_users with valid token for testing
    valid_token = "test-external-token-valid"
    salt_hex = os.urandom(32).hex()
    token_hash = hashlib.pbkdf2_hmac('sha256', valid_token.encode('utf-8'), bytes.fromhex(salt_hex), 100_000).hex()

    cursor.execute(
        """
        INSERT INTO system_users (id, username, token, token_salt, user_type, data_criacao)
        VALUES (1, 'external_api_client', ?, ?, 'externo', '2024-01-15 08:00:00')
        """,
        (token_hash, salt_hex)
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

    monkeypatch.setattr(db_module.sqlite3, "connect", connect_override)

    app = app_module.create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
    )

    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def api_client(db_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Provide a Flask test client for the external API."""
    original_connect = sqlite3.connect

    def connect_override(_database, *args, **kwargs):
        return original_connect(str(db_path), *args, **kwargs)

    monkeypatch.setattr(db_module.sqlite3, "connect", connect_override)

    api_app = create_api_app()
    api_app.config.update(TESTING=True)

    with api_app.test_client() as test_client:
        yield test_client


@pytest.fixture
def valid_token():
    """Provide a valid token for API testing."""
    return "test-external-token-valid"


@pytest.fixture
def invalid_token():
    """Provide an invalid token for API testing."""
    return "invalid-token-xyz"
