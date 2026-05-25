"""Configurações centralizadas da aplicação."""
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

# Flask
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
if not FLASK_SECRET_KEY:
    if os.getenv("FLASK_ENV") == "production":
        raise RuntimeError("FLASK_SECRET_KEY must be set in production.")
    FLASK_SECRET_KEY = secrets.token_hex(32)

FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").strip().lower() in ("1", "true", "yes", "on")

# Database
DATABASE_PATH = os.getenv('DATABASE_PATH', 'demandas.db')
DATABASE_PATH_ABS = os.path.abspath(DATABASE_PATH)
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH_ABS}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Business Logic
DEFAULT_DEADLINE_DAYS = 7
COMPANY_NAME = os.getenv("COMPANY_NAME", "SGDI - Sistema de Gestão de Demandas")

# Default Requesters
DEFAULT_REQUESTERS = (
    {"nome": "Joao Silva", "email": "joao.silva@empresa.com", "cargo": "Analista"},
    {"nome": "Maria Santos", "email": "maria.santos@empresa.com", "cargo": "Coordenadora"},
    {"nome": "Tech Team", "email": "tech.team@empresa.com", "cargo": "Equipe Tecnica"},
    {"nome": "Equipe Suporte", "email": "suporte@empresa.com", "cargo": "Suporte"},
    {"nome": "Time Produto", "email": "produto@empresa.com", "cargo": "Produto"},
)

# Plotly Palettes
PALETTE_PRIORITY = {
    'alta': '#e05252',
    'media': '#e0a84d',
    'baixa': '#52a8e0',
    'sem prioridade': '#9e9e9e',
}

PALETTE_STATUS = {
    'Aberto': '#52a8e0',
    'Em Andamento': '#e0a84d',
    'Concluido': '#5ac87a',
    'Cancelado': '#e05252',
}

PALETTE_BAR = [
    '#4f8ef7', '#a78bfa', '#34d399', '#f97316',
    '#fb7185', '#facc15', '#22d3ee', '#e879f9',
]

