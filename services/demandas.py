"""Serviços relacionados a demandas."""
import sqlite3
from db import fetch_all, fetch_one, execute_query, log_db_error
from services.utils import date_now, calculate_deadline, normalize_status, normalize_priority


def ensure_demandas_dashboard_columns():
    """Garante que a tabela de demandas tem todas as colunas necessárias."""
    from config import DEFAULT_DEADLINE_DAYS

    columns = {row[1] for row in fetch_all("PRAGMA table_info(demandas)")}
    required_columns = {
        "status": "TEXT NOT NULL DEFAULT 'aberta'",
        "responsavel": "TEXT",
        "prazo": "TEXT",
        "data_conclusao": "TEXT",
    }

    for column_name, column_definition in required_columns.items():
        if column_name not in columns:
            execute_query(f"ALTER TABLE demandas ADD COLUMN {column_name} {column_definition}")

    execute_query(
        """
        UPDATE demandas
        SET responsavel = solicitante
        WHERE responsavel IS NULL OR TRIM(responsavel) = ''
        """
    )
    execute_query(
        f"""
        UPDATE demandas
        SET prazo = COALESCE(
            date(data_criacao, '+{DEFAULT_DEADLINE_DAYS} days'),
            date('now', '+{DEFAULT_DEADLINE_DAYS} days')
        )
        """
    )
    execute_query(
        """
        UPDATE demandas
        SET prioridade = 'baixa'
        WHERE prioridade IS NULL
           OR TRIM(prioridade) = ''
           OR LOWER(TRIM(prioridade)) NOT IN ('alta', 'media', 'média', 'baixa')
        """
    )


def get_demandas(prioridade_filtro='todas'):
    """Retorna lista de demandas com filtro de prioridade."""
    ensure_demandas_dashboard_columns()

    # Por padrão não exibimos demandas concluídas ou canceladas na listagem
    if prioridade_filtro == 'todas' or not prioridade_filtro:
        demandas = fetch_all("""
            SELECT *
            FROM demandas
            WHERE LOWER(status) NOT IN ('concluida', 'cancelada')
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
        prioridade_normalizada = normalize_priority(prioridade_filtro)
        demandas = fetch_all("""
            SELECT *
            FROM demandas
            WHERE LOWER(prioridade) = ?
              AND LOWER(status) NOT IN ('concluida', 'cancelada')
            ORDER BY data_criacao DESC
        """, (prioridade_normalizada,))

    return demandas


def get_demanda(demanda_id):
    """Busca uma demanda por ID."""
    ensure_demandas_dashboard_columns()
    return fetch_one('SELECT * FROM demandas WHERE id = ?', (demanda_id,))


def search_demandas(termo):
    """Busca demandas por termo (título, ID ou solicitante)."""
    ensure_demandas_dashboard_columns()
    like_term = f"%{termo}%"
    # Exclui demandas concluídas e canceladas também na busca quando exibida na listagem
    return fetch_all(
        '''SELECT * FROM demandas 
           WHERE (titulo LIKE ? 
           OR id LIKE ?
           OR solicitante LIKE ?)
             AND LOWER(status) NOT IN ('concluida', 'cancelada')
           ORDER BY data_criacao DESC''',
        (like_term, like_term, like_term),
    )


def create_demanda(titulo, descricao, solicitante, responsavel, prioridade, status):
    """Cria uma nova demanda."""
    ensure_demandas_dashboard_columns()
    data_criacao = str(date_now())
    prioridade = normalize_priority(prioridade)
    status = normalize_status(status)
    prazo = calculate_deadline(data_criacao)
    data_conclusao = date_now() if status == "concluida" else None

    try:
        execute_query(
            """
            INSERT INTO demandas
                (titulo, descricao, solicitante, prioridade, data_criacao, status, responsavel, prazo, data_conclusao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (titulo, descricao, solicitante, prioridade, data_criacao, status, responsavel, prazo, data_conclusao),
        )
        return True
    except sqlite3.Error as error:
        log_db_error("create_demanda", error, solicitante=solicitante)
        return False


def update_demanda(demanda_id, titulo, descricao, solicitante, responsavel, prioridade, status):
    """Atualiza uma demanda existente."""
    ensure_demandas_dashboard_columns()
    current_demanda = get_demanda(demanda_id)
    if not current_demanda:
        return False

    prioridade = normalize_priority(prioridade)
    status = normalize_status(status)
    prazo = calculate_deadline(current_demanda[5] if current_demanda else None)

    current_data_conclusao = current_demanda[9] if current_demanda and len(current_demanda) > 9 else None
    data_conclusao = current_data_conclusao
    if status == "concluida" and not data_conclusao:
        data_conclusao = date_now()
    elif status != "concluida":
        data_conclusao = None

    try:
        execute_query(
            """
            UPDATE demandas
            SET titulo = ?, descricao = ?, prioridade = ?, solicitante = ?,
                responsavel = ?, status = ?, prazo = ?, data_conclusao = ?
            WHERE id = ?
            """,
            (titulo, descricao, prioridade, solicitante, responsavel, status, prazo, data_conclusao, demanda_id),
        )
        return True
    except sqlite3.Error as error:
        log_db_error("update_demanda", error, demanda_id=demanda_id, solicitante=solicitante)
        return False


def delete_demanda(demanda_id):
    """Deleta uma demanda."""
    try:
        execute_query('DELETE FROM demandas WHERE id = ?', (demanda_id,))
        return True
    except sqlite3.Error as error:
        log_db_error("delete_demanda", error, demanda_id=demanda_id)
        return False

