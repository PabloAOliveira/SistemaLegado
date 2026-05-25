"""Serviços relacionados a geração de gráficos."""
import json
import pandas as pd
import plotly.express as px
from config import PALETTE_PRIORITY, PALETTE_STATUS, PALETTE_BAR
from db import fetch_all
from services.demandas import ensure_demandas_dashboard_columns


_DARK_LAYOUT_CONFIG = {
    'BG': '#1e2330',
    'FG': '#c9d1d9',
    'GRID': '#2d3448',
}


def _apply_dark_layout(fig, title):
    """Aplica tema escuro ao gráfico Plotly."""
    config = _DARK_LAYOUT_CONFIG
    fig.update_layout(
        title={
            'text': title,
            'font': {'color': config['FG'], 'size': 14, 'family': 'sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        paper_bgcolor=config['BG'],
        plot_bgcolor=config['BG'],
        font={'color': config['FG']},
        margin={'t': 50, 'b': 20, 'l': 10, 'r': 10},
        xaxis={'showgrid': False, 'gridcolor': config['GRID'], 'zeroline': False, 'automargin': True},
        yaxis={'showgrid': True, 'gridcolor': config['GRID'], 'zeroline': False, 'automargin': True},
        autosize=True
    )
    return fig


def gerar_graficos():
    """Gera os 4 gráficos usando Plotly e retorna JSON objects."""
    ensure_demandas_dashboard_columns()
    resultado = {}

    # 1. Chamados por Solicitante (barras horizontais)
    dados_sol = fetch_all("""
        SELECT solicitante, COUNT(*) as total
        FROM demandas
        WHERE solicitante IS NOT NULL AND solicitante != ''
        GROUP BY solicitante
        ORDER BY total
        LIMIT 10
    """)
    if dados_sol:
        df = pd.DataFrame(dados_sol, columns=['Solicitante', 'Total'])
        fig = px.bar(
            df, x='Total', y='Solicitante', orientation='h', text='Total',
            color='Solicitante', color_discrete_sequence=PALETTE_BAR
        )
        fig.update_layout(showlegend=False, xaxis_title="Número de Chamados", yaxis_title="")
        fig.update_traces(textposition='outside')
        fig = _apply_dark_layout(fig, 'Chamados por Solicitante')
        resultado['por_solicitante'] = json.loads(fig.to_json())
    else:
        resultado['por_solicitante'] = None

    # 2. Por Prioridade (pizza)
    dados_prio = fetch_all("""
        SELECT COALESCE(NULLIF(prioridade,''), 'sem prioridade') as prio,
               COUNT(*) as total
        FROM demandas
        GROUP BY prio
        ORDER BY total DESC
    """)
    if dados_prio:
        df = pd.DataFrame(dados_prio, columns=['Prioridade', 'Total'])
        cores = [PALETTE_PRIORITY.get(p.lower(), '#9e9e9e') for p in df['Prioridade']]
        fig = px.pie(df, values='Total', names='Prioridade',
                     color_discrete_sequence=cores, hole=0.3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig = _apply_dark_layout(fig, 'Chamados por Prioridade')
        resultado['por_prioridade'] = json.loads(fig.to_json())
    else:
        resultado['por_prioridade'] = None

    # 3. Por Status (barras verticais)
    dados_status = fetch_all("""
        SELECT COALESCE(NULLIF(status,''), 'Aberto') as st,
               COUNT(*) as total
        FROM demandas
        GROUP BY st
        ORDER BY total DESC
    """)
    if dados_status:
        df = pd.DataFrame(dados_status, columns=['Status', 'Total'])
        cores = [PALETTE_STATUS.get(s, '#9e9e9e') for s in df['Status']]
        fig = px.bar(df, x='Status', y='Total', text='Total',
                     color='Status', color_discrete_sequence=cores)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Número de Chamados")
        fig.update_traces(textposition='outside')
        fig = _apply_dark_layout(fig, 'Chamados por Status')
        fig.update_layout(xaxis={'showgrid': False})
        resultado['por_status'] = json.loads(fig.to_json())
    else:
        resultado['por_status'] = None

    # 4. Evolução Temporal (linha por mês)
    dados_temp = fetch_all("""
        SELECT substr(data_criacao, 1, 7) as mes, COUNT(*) as total
        FROM demandas
        WHERE data_criacao IS NOT NULL AND data_criacao != ''
        GROUP BY mes
        ORDER BY mes
        LIMIT 24
    """)
    if dados_temp:
        df = pd.DataFrame(dados_temp, columns=['Mês', 'Total'])
        fig = px.line(df, x='Mês', y='Total', markers=True, text='Total')
        fig.update_traces(
            line={'color': '#4f8ef7', 'width': 3},
            marker={'size': 8, 'color': '#a78bfa'},
            textposition="top center"
        )
        fig.update_layout(xaxis_title="", yaxis_title="Número de Chamados")
        fig = _apply_dark_layout(fig, 'Evolução Temporal de Chamados')
        resultado['evolucao_temporal'] = json.loads(fig.to_json())
    else:
        resultado['evolucao_temporal'] = None

    return resultado

