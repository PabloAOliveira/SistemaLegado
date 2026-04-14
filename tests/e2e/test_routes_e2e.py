import sqlite3
from pathlib import Path
from contextlib import closing

def get_db(db_path: Path):
    return closing(sqlite3.connect(str(db_path)))


def test_index_lista_demandas(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Lista de Demandas" in response.data
    assert b"Corrigir bug no login" in response.data


def test_nova_demanda_get_exibe_formulario(client):
    response = client.get("/nova_demanda")

    assert response.status_code == 200
    assert b"Nova Demanda" in response.data


def test_header_contem_link_para_solicitante(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b'href="/solicitante"' in response.data


def test_solicitante_get_exibe_pagina(client):
    response = client.get("/solicitante")

    assert response.status_code == 200
    assert b"Solicitante" in response.data


def test_nova_demanda_post_cria_registro_e_redireciona(client, db_path: Path):
    response = client.post(
        "/nova_demanda",
        data={
            "titulo": "Nova feature",
            "descricao": "Implementar upload de arquivos",
            "solicitante": "Time Produto",
            "prioridade": "baixa",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        created = cursor.execute(
            "SELECT titulo, descricao, solicitante, prioridade FROM demandas WHERE titulo = ?",
            ("Nova feature",),
        ).fetchone()

    assert created == ("Nova feature", "Implementar upload de arquivos", "Time Produto", "baixa")


def test_editar_get_exibe_demanda(client):
    response = client.get("/editar/1")

    assert response.status_code == 200
    assert b"Editar Demanda" in response.data
    assert b"Corrigir bug no login" in response.data


def test_editar_post_atualiza_demanda_e_redireciona(client, db_path: Path):
    response = client.post(
        "/editar/1",
        data={
            "titulo": "Login corrigido",
            "descricao": "Ajuste final do login",
            "solicitante": "Equipe Suporte",
            "prioridade": "media",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        updated = cursor.execute(
            "SELECT titulo, descricao, solicitante, prioridade FROM demandas WHERE id = 1"
        ).fetchone()

    assert updated == ("Login corrigido", "Ajuste final do login", "Equipe Suporte", "media")


def test_deletar_remove_demanda_e_redireciona(client, db_path: Path):
    response = client.delete("/deletar/2", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        deleted = cursor.execute("SELECT id FROM demandas WHERE id = 2").fetchone()

    assert deleted is None


def test_buscar_filtra_por_titulo(client):
    response = client.get("/buscar?q=login")

    assert response.status_code == 200
    assert b"Corrigir bug no login" in response.data
    assert b"Implementar relatorio de vendas" not in response.data


def test_index_filtra_por_prioridade(client):
    response = client.get("/?prioridade=alta")

    assert response.status_code == 200
    assert b"Corrigir bug no login" in response.data
    assert b"Implementar relat" not in response.data


def test_index_sem_filtro_mostra_todas_ordenadas(client):
    response = client.get("/")

    assert response.status_code == 200
    data = response.data.decode('utf-8')
    alta_pos = data.find("Corrigir bug no login")
    media_pos = data.find("Implementar relat")
    assert alta_pos < media_pos


def test_detalhes_exibe_demanda_e_comentarios(client):
    response = client.get("/detalhes/1")

    assert response.status_code == 200
    assert b"Detalhes da Demanda #1" in response.data
    assert b"Vou investigar esse bug" in response.data


def test_adicionar_comentario_cria_registro_e_redireciona(client, db_path: Path):
    response = client.post(
        "/adicionar_comentario/1",
        data={"autor": "QA", "comentario": "Fluxo validado em e2e"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/detalhes/1")

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        comment = cursor.execute(
            "SELECT autor, comentario FROM comentarios WHERE demanda_id = 1 AND autor = ?",
            ("QA",),
        ).fetchone()

    assert comment == ("QA", "Fluxo validado em e2e")

