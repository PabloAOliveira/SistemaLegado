"""Funções utilitárias gerais."""
import datetime
from config import DEFAULT_DEADLINE_DAYS


def date_now():
    """Retorna data/hora atual em formato padronizado."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_datetime(value):
    """Converte string para datetime."""
    if not value:
        return None
    for date_format in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(value, date_format)
        except ValueError:
            continue
    return None


def calculate_deadline(created_at):
    """Calcula prazo baseado na data de criação."""
    created_date = parse_datetime(created_at) or datetime.datetime.now()
    return (created_date + datetime.timedelta(days=DEFAULT_DEADLINE_DAYS)).strftime("%Y-%m-%d")


def normalize_status(value):
    """Normaliza o status para formato padrão."""
    status = (value or "aberta").strip().lower()
    if status in ("concluida", "concluída"):
        return "concluida"
    if status == "cancelada":
        return "cancelada"
    return "aberta"


def normalize_priority(value):
    """Normaliza a prioridade para formato padrão."""
    priority = (value or "").strip().lower()
    if priority == "alta":
        return "alta"
    if priority in ("media", "média"):
        return "media"
    return "baixa"


def status_label(status):
    """Retorna label formatado do status."""
    labels = {
        "aberta": "Aberta",
        "concluida": "Concluida",
        "cancelada": "Cancelada",
    }
    return labels.get(normalize_status(status), "Aberta")


def format_priority_filter_label(prioridade_filtro):
    """Formata o rótulo do filtro de prioridade para exibição."""
    if prioridade_filtro == 'todas' or not prioridade_filtro:
        return "Todas as prioridades"
    elif prioridade_filtro == 'alta':
        return "Prioridade Alta"
    elif prioridade_filtro in ('media', 'média'):
        return "Prioridade Média"
    elif prioridade_filtro == 'baixa':
        return "Prioridade Baixa"
    return prioridade_filtro


def parse_data_criacao(value):
    """Parse data de criação."""
    if not value:
        return None
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

