import sqlite3
import datetime
from pathlib import Path
from contextlib import closing

import app as app_module


def get_db(db_path: Path):
    return closing(sqlite3.connect(str(db_path)))


def test_index_lista_demandas(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Lista de Demandas" in response.data
    assert b"Total de demandas" not in response.data
    assert b"Demandas criticas" not in response.data
    assert b"Corrigir bug no login" in response.data


def test_dashboard_exibe_kpis(client):
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Painel de KPIs" in response.data
    assert b"Total de demandas" in response.data
    assert b"Demandas criticas" in response.data
    assert b"media entre demandas concluidas" in response.data


def test_dashboard_tempo_medio_usa_media_das_concluidas():
    demandas = [
        (1, "Concluida 1", "", "Joao Silva", "alta", "2024-01-01 08:00:00", "concluida", "Tech Team", "2024-01-08", "2024-01-04 08:00:00"),
        (2, "Concluida 2", "", "Maria Santos", "media", "2024-01-10 08:00:00", "concluida", "Tech Team", "2024-01-17", "2024-01-13 08:00:00"),
        (3, "Aberta", "", "Maria Santos", "baixa", "2024-01-10 08:00:00", "aberta", "Maria Santos", "2024-01-17", None),
        (4, "Cancelada", "", "Maria Santos", "baixa", "2024-01-01 08:00:00", "cancelada", "Maria Santos", "2024-01-08", "2024-02-01 08:00:00"),
    ]

    dashboard = app_module.calculate_dashboard_metrics(demandas)

    assert dashboard["average_resolution_days"] == 3.0


def test_nova_demanda_get_exibe_formulario(client):
    response = client.get("/nova_demanda")

    assert response.status_code == 200
    assert b"Nova Demanda" in response.data
    assert b'<select name="solicitante"' in response.data
    assert b'name="prazo"' not in response.data


def test_header_contem_link_para_solicitante(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b'href="/solicitante"' in response.data
    assert b'href="/dashboard"' in response.data


def test_solicitante_get_exibe_pagina(client):
    response = client.get("/solicitante")

    assert response.status_code == 200
    assert b"Solicitante" in response.data
    assert b"Cadastrar" in response.data


def test_cadastrar_solicitante_get_exibe_formulario(client):
    response = client.get("/solicitante/cadastrar")

    assert response.status_code == 200
    assert b"Cadastrar Solicitante" in response.data
    assert b'name="nome"' in response.data
    assert b'name="email"' in response.data
    assert b'name="cargo"' in response.data


def test_cadastrar_solicitante_post_adiciona_nome_na_lista(client):
    response = client.post(
        "/solicitante/cadastrar",
        data={
            "nome": "Ana Lima",
            "email": "ana.lima@empresa.com",
            "cargo": "Gerente",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/solicitante")

    nova_demanda = client.get("/nova_demanda")
    assert b"Ana Lima" in nova_demanda.data


def test_cadastrar_solicitante_post_com_campo_vazio_retorna_erro(client):
    response = client.post(
        "/solicitante/cadastrar",
        data={
            "nome": "Ana Lima",
            "email": "",
            "cargo": "Gerente",
        },
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert b"Preencha nome, email e cargo para cadastrar!" in response.data


def test_nova_demanda_post_cria_registro_e_redireciona(client, db_path: Path):
    response = client.post(
        "/nova_demanda",
        data={
            "titulo": "Nova feature",
            "descricao": "Implementar upload de arquivos",
            "solicitante": "Time Produto",
            "responsavel": "Tech Team",
            "prioridade": "baixa",
            "status": "aberta",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        created = cursor.execute(
            "SELECT titulo, descricao, solicitante, prioridade, responsavel, status, prazo FROM demandas WHERE titulo = ?",
            ("Nova feature",),
        ).fetchone()

    expected_deadline = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    assert created == ("Nova feature", "Implementar upload de arquivos", "Time Produto", "baixa", "Tech Team", "aberta", expected_deadline)


def test_nova_demanda_post_prioridade_invalida_vira_baixa(client, db_path: Path):
    response = client.post(
        "/nova_demanda",
        data={
            "titulo": "Sem prioridade valida",
            "descricao": "Validar prioridade automatica",
            "solicitante": "Time Produto",
            "responsavel": "Tech Team",
            "prioridade": "",
            "status": "aberta",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        prioridade = cursor.execute(
            "SELECT prioridade FROM demandas WHERE titulo = ?",
            ("Sem prioridade valida",),
        ).fetchone()

    assert prioridade == ("baixa",)


def test_editar_get_exibe_demanda(client):
    response = client.get("/editar/1")

    assert response.status_code == 200
    assert b"Editar Demanda" in response.data
    assert b"Corrigir bug no login" in response.data
    assert b'<select id="solicitante"' in response.data
    assert b'name="prazo"' not in response.data


def test_editar_post_atualiza_demanda_e_redireciona(client, db_path: Path):
    response = client.post(
        "/editar/1",
        data={
            "titulo": "Login corrigido",
            "descricao": "Ajuste final do login",
            "solicitante": "Equipe Suporte",
            "responsavel": "Tech Team",
            "prioridade": "media",
            "status": "concluida",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        updated = cursor.execute(
            "SELECT titulo, descricao, solicitante, prioridade, responsavel, status, prazo, data_conclusao FROM demandas WHERE id = 1"
        ).fetchone()

    assert updated[:7] == ("Login corrigido", "Ajuste final do login", "Equipe Suporte", "media", "Tech Team", "concluida", "2024-01-22")
    assert updated[7] is not None


def test_editar_post_prioridade_invalida_vira_baixa(client, db_path: Path):
    response = client.post(
        "/editar/1",
        data={
            "titulo": "Login sem prioridade",
            "descricao": "Prioridade invalida deve virar baixa",
            "solicitante": "Equipe Suporte",
            "responsavel": "Tech Team",
            "prioridade": "urgente",
            "status": "aberta",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        prioridade = cursor.execute("SELECT prioridade FROM demandas WHERE id = 1").fetchone()

    assert prioridade == ("baixa",)


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
    assert b'<select name="autor"' in response.data


def test_adicionar_comentario_cria_registro_e_redireciona(client, db_path: Path):
    response = client.post(
        "/adicionar_comentario/1",
        data={"autor": "Tech Team", "comentario": "Fluxo validado em e2e"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/detalhes/1")

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        comment = cursor.execute(
            "SELECT autor, comentario FROM comentarios WHERE demanda_id = 1 AND autor = ? AND comentario = ?",
            ("Tech Team", "Fluxo validado em e2e"),
        ).fetchone()

    assert comment == ("Tech Team", "Fluxo validado em e2e")


def test_adicionar_comentario_vazio_retorna_erro_e_nao_grava(client, db_path: Path):
    response = client.post(
        "/adicionar_comentario/1",
        data={"autor": "Tech Team", "comentario": "   "},
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert b'Escreva um comentario antes de enviar!' in response.data

    with get_db(db_path) as conn:
        cursor = conn.cursor()
        comment = cursor.execute(
            "SELECT autor, comentario FROM comentarios WHERE demanda_id = 1 AND comentario = ?",
            ("   ",),
        ).fetchone()

    assert comment is None

