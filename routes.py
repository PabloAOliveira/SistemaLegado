"""Rotas da aplicação."""
from flask import render_template, request, redirect, url_for, flash, jsonify
from services.demandas import (
    get_demandas, get_demanda, search_demandas, create_demanda,
    update_demanda, delete_demanda, ensure_demandas_dashboard_columns
)
from services.requesters import (
    get_requesters, get_requester_by_id, get_available_people, is_valid_person,
    update_requester, create_requester, delete_requester
)
from services.comentarios import get_comentarios, create_comentario
from services.graphics import gerar_graficos
from services.dashboard import calculate_dashboard_metrics
from services.export import export_to_excel, export_to_pdf
from services.utils import normalize_priority, normalize_status


def register_routes(app):
    """Registra todas as rotas na aplicação."""

    @app.route('/', methods=['GET'])
    def index():
        ensure_demandas_dashboard_columns()
        prioridade_filtro = request.args.get('prioridade', 'todas').strip().lower()
        if prioridade_filtro not in ("todas", ""):
            prioridade_filtro = normalize_priority(prioridade_filtro)

        demandas = get_demandas(prioridade_filtro)
        return render_template('index.html', demandas=demandas, prioridade_filtro=prioridade_filtro)

    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        ensure_demandas_dashboard_columns()
        from db import fetch_all
        dashboard_metrics = calculate_dashboard_metrics(fetch_all("SELECT * FROM demandas"))
        return render_template('dashboard.html', dashboard=dashboard_metrics)

    @app.route('/nova_demanda', methods=['GET', 'POST'])
    def nova_demanda():
        ensure_demandas_dashboard_columns()
        people = get_available_people()

        if request.method == 'POST':
            titulo = request.form['titulo']
            descricao = request.form['descricao']
            solicitante = request.form['solicitante'].strip()
            responsavel = request.form.get('responsavel', '').strip()
            prioridade = request.form.get('prioridade')
            status = request.form.get('status')

            if not is_valid_person(solicitante) or not is_valid_person(responsavel):
                flash('Selecione solicitante e responsavel validos!', 'error')
                return render_template('nova_demanda.html', people=people, form_data=request.form)

            if create_demanda(titulo, descricao, solicitante, responsavel, prioridade, status):
                flash('Salvo!')
                return redirect(url_for('index'))
            else:
                flash('Erro ao salvar demanda!')
                return redirect(url_for('nova_demanda'))

        return render_template('nova_demanda.html', people=people, form_data={})

    @app.route('/editar/<int:demanda_id>', methods=['GET', 'POST'])
    def editar(demanda_id):
        ensure_demandas_dashboard_columns()
        people = get_available_people()

        if request.method == 'POST':
            titulo = request.form['titulo']
            descricao = request.form['descricao']
            solicitante = request.form['solicitante'].strip()
            responsavel = request.form.get('responsavel', '').strip()
            prioridade = request.form.get('prioridade')
            status = request.form.get('status')

            if not is_valid_person(solicitante) or not is_valid_person(responsavel):
                flash('Selecione solicitante e responsavel validos!', 'error')
                demanda = get_demanda(demanda_id)
                return render_template('editar.html', demanda=demanda, people=people, form_data=request.form)

            if update_demanda(demanda_id, titulo, descricao, solicitante, responsavel, prioridade, status):
                flash('Atualizado!')
                return redirect(url_for('index'))
            else:
                flash('Erro ao atualizar demanda!')
                return redirect(url_for('editar', demanda_id=demanda_id))

        demanda = get_demanda(demanda_id)
        return render_template('editar.html', demanda=demanda, people=people, form_data={})

    @app.route('/deletar/<int:demanda_id>', methods=['DELETE'])
    def deletar(demanda_id):
        if delete_demanda(demanda_id):
            flash('Deletado!')
        else:
            flash('Erro ao deletar demanda!')
        return redirect(url_for('index'))

    @app.route('/buscar', methods=['GET'])
    def buscar():
        ensure_demandas_dashboard_columns()
        termo = request.args.get('q', '').strip()
        resultados = search_demandas(termo)
        return render_template('index.html', demandas=resultados, prioridade_filtro='todas')

    @app.route('/detalhes/<int:demanda_id>', methods=['GET'])
    def detalhes(demanda_id):
        ensure_demandas_dashboard_columns()
        demanda = get_demanda(demanda_id)
        comentarios = get_comentarios(demanda_id)

        return render_template(
            'detalhes.html',
            demanda=demanda,
            comentarios=comentarios,
            people=get_available_people(),
            form_data={},
        )

    @app.route('/solicitante', methods=['GET'])
    def solicitante():
        requesters = get_requesters()
        graficos = gerar_graficos()
        return render_template('solicitante.html', requesters=requesters, graficos=graficos)

    @app.route('/solicitante/graficos', methods=['GET'])
    def solicitante_graficos_api():
        """API para atualização dinâmica dos gráficos via fetch()."""
        return jsonify(gerar_graficos())

    @app.route('/sutita', methods=['GET'])
    def sutita():
        return render_template('sutita.html')

    @app.route('/solicitante/<int:requester_id>', methods=['GET'])
    def detalhes_solicitante(requester_id):
        requester = get_requester_by_id(requester_id)
        if not requester:
            flash('Solicitante não encontrado!', 'error')
            return redirect(url_for('solicitante'))
        return render_template('detalhes_solicitante.html', requester=requester)

    @app.route('/solicitante/editar/<int:requester_id>', methods=['GET', 'POST'])
    def editar_solicitante(requester_id):
        requester = get_requester_by_id(requester_id)
        if not requester:
            flash('Solicitante não encontrado!', 'error')
            return redirect(url_for('solicitante'))

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip()
            cargo = request.form.get('cargo', '').strip()

            if not nome or not email or not cargo:
                flash('Preencha nome, email e cargo para salvar!', 'error')
                return render_template('editar_solicitante.html', requester=requester, form_data=request.form)

            if len(nome) > 40 or len(email) > 40 or len(cargo) > 40:
                flash('Nome, email e cargo devem ter no máximo 40 caracteres.', 'error')
                return render_template('editar_solicitante.html', requester=requester, form_data=request.form)

            if not update_requester(requester_id, nome, email, cargo):
                flash('Já existe solicitante cadastrado com este email!', 'error')
                return render_template('editar_solicitante.html', requester=requester, form_data=request.form)

            flash('Solicitante atualizado com sucesso!', 'success')
            return redirect(url_for('solicitante'))

        return render_template('editar_solicitante.html', requester=requester, form_data={})

    @app.route('/solicitante/deletar/<int:requester_id>', methods=['DELETE'])
    def deletar_solicitante(requester_id):
        requester = get_requester_by_id(requester_id)
        if not requester:
            return ('', 404)

        try:
            delete_requester(requester_id)
            return ('', 204)
        except Exception:
            return ('', 500)

    @app.route('/solicitante/cadastrar', methods=['GET', 'POST'])
    def cadastrar_solicitante():
        if request.method == 'POST':
            nome = request.form['nome'].strip()
            email = request.form['email'].strip()
            cargo = request.form['cargo'].strip()

            if not nome or not email or not cargo:
                flash('Preencha nome, email e cargo para cadastrar!', 'error')
                return render_template('cadastrar_solicitante.html', form_data=request.form)

            if len(nome) > 40 or len(email) > 40 or len(cargo) > 40:
                flash('Nome, email e cargo devem ter no máximo 40 caracteres.', 'error')
                return render_template('cadastrar_solicitante.html', form_data=request.form)

            if not create_requester(nome, email, cargo):
                flash('Ja existe solicitante cadastrado com este email!', 'error')
                return render_template('cadastrar_solicitante.html', form_data=request.form)

            flash('Solicitante cadastrado com sucesso!', 'success')
            return redirect(url_for('solicitante'))

        return render_template('cadastrar_solicitante.html', form_data={})

    @app.route('/adicionar_comentario/<int:demanda_id>', methods=['POST'])
    def adicionar_comentario(demanda_id):
        comentario = request.form['comentario'].strip()
        autor = request.form['autor'].strip()

        if not is_valid_person(autor):
            flash('Selecione um autor valido para o comentario!', 'error')
            demanda = get_demanda(demanda_id)
            comentarios = get_comentarios(demanda_id)
            return render_template(
                'detalhes.html',
                demanda=demanda,
                comentarios=comentarios,
                people=get_available_people(),
                form_data=request.form,
            )

        if not comentario:
            flash('Escreva um comentario antes de enviar!', 'error')
            demanda = get_demanda(demanda_id)
            comentarios = get_comentarios(demanda_id)
            return render_template(
                'detalhes.html',
                demanda=demanda,
                comentarios=comentarios,
                people=get_available_people(),
                form_data=request.form,
            )

        if create_comentario(demanda_id, comentario, autor):
            flash('Comentário adicionado!')
        else:
            flash('Erro ao adicionar comentário!')

        return redirect(url_for('detalhes', demanda_id=demanda_id))

    @app.route('/export/excel', methods=['POST'])
    def export_excel_route():
        """Exporta demandas em formato Excel."""
        prioridade_filtro = request.form.get('prioridade_filtro', 'todas').strip().lower()
        relatorio_tipo = request.form.get('relatorio_tipo', 'completo').strip().lower()
        return export_to_excel(prioridade_filtro, relatorio_tipo)

    @app.route('/export/pdf', methods=['POST'])
    def export_pdf_route():
        """Exporta demandas em formato PDF."""
        prioridade_filtro = request.form.get('prioridade_filtro', 'todas').strip().lower()
        relatorio_tipo = request.form.get('relatorio_tipo', 'completo').strip().lower()
        return export_to_pdf(prioridade_filtro, relatorio_tipo)

