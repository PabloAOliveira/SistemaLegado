"""Serviços relacionados ao dashboard e cálculo de KPIs."""
import datetime
from services.utils import normalize_status, status_label, parse_datetime


def calculate_dashboard_metrics(demandas):
    """Calcula métricas de KPI para o dashboard."""
    total = len(demandas)
    today = datetime.datetime.now().date()

    counts = {
        "abertas": 0,
        "concluidas": 0,
        "atrasadas": 0,
    }
    critical_demands = []
    open_by_responsible = {}
    completed_resolution_days = []

    for demanda in demandas:
        status = normalize_status(demanda[6] if len(demanda) > 6 else None)
        responsavel = (demanda[7] if len(demanda) > 7 else None) or demanda[3] or "Sem responsavel"
        prazo = demanda[8] if len(demanda) > 8 else None
        data_conclusao = demanda[9] if len(demanda) > 9 else None

        is_finalized = status in ("concluida", "cancelada")
        is_late = False
        prazo_date = parse_datetime(prazo)
        if prazo_date and not is_finalized and prazo_date.date() < today:
            is_late = True

        if status == "concluida":
            counts["concluidas"] += 1
            started_at = parse_datetime(demanda[5])
            finished_at = parse_datetime(data_conclusao)
            if started_at and finished_at and finished_at >= started_at:
                completed_resolution_days.append((finished_at - started_at).total_seconds() / 86400)
        elif status == "aberta":
            counts["abertas"] += 1
            open_by_responsible[responsavel] = open_by_responsible.get(responsavel, 0) + 1

        if is_late:
            counts["atrasadas"] += 1

        if (demanda[4] or "").strip().lower() == "alta" and not is_finalized:
            critical_demands.append(
                {
                    "id": demanda[0],
                    "titulo": demanda[1],
                    "responsavel": responsavel,
                    "status": status_label(status),
                }
            )

    def percent(value):
        if total == 0:
            return 0
        return round((value / total) * 100)

    average_resolution_days = None
    if completed_resolution_days:
        average_resolution_days = round(sum(completed_resolution_days) / len(completed_resolution_days), 1)

    return {
        "total": total,
        "status_cards": [
            {"label": "Abertas", "count": counts["abertas"], "percent": percent(counts["abertas"])},
            {"label": "Concluidas", "count": counts["concluidas"], "percent": percent(counts["concluidas"])},
            {"label": "Atrasadas", "count": counts["atrasadas"], "percent": percent(counts["atrasadas"])},
        ],
        "critical_demands": critical_demands,
        "open_by_responsible": sorted(open_by_responsible.items(), key=lambda item: (-item[1], item[0].lower())),
        "average_resolution_days": average_resolution_days,
    }

