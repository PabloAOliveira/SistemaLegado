"""
Aplicação Flask modularizada.

Estrutura de módulos:
- config.py: Configurações + constantes
- db.py: Funções genéricas de banco de dados
- services/: Serviços de negócio (graphics, dashboard, demandas, etc.)
- routes.py: Definições de rotas HTTP
- app.py: Application factory (este arquivo)
"""
from flask import Flask
from flask_migrate import Migrate
from models import db
import config
from routes import register_routes

# Expor calculate_dashboard_metrics para compatibilidade com testes existentes
from services.dashboard import calculate_dashboard_metrics


def create_app():
    """Factory function para criar e configurar a aplicação Flask."""
    app = Flask(__name__)

    # Configurações
    app.secret_key = config.FLASK_SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    # Inicializar extensões
    db.init_app(app)
    migrate = Migrate(app, db)

    # Registrar rotas
    register_routes(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=config.FLASK_DEBUG,
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
    )

