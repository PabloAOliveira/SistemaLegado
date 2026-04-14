from flask_migrate import upgrade
from sqlalchemy import text

from app import app
from models import db


SEED_DEMANDAS = [
    (1, 'Corrigir bug no login', 'Usuarios nao conseguem fazer login', 'Joao Silva', '', '2024-01-15 10:30:00'),
    (2, 'Implementar relatorio de vendas', 'Precisamos de um relatorio mensal', 'Maria Santos', '', '2024-01-16 14:20:00'),
    (3, 'Melhorar performance', 'Sistema esta lento', 'Pedro Costa', '', '2024-01-17 09:15:00'),
    (99, 'Adicionar filtros', 'Usuarios querem filtrar demandas', 'Ana Lima', '', '2024-01-18 11:00:00'),
]

SEED_COMENTARIOS = [
    (1, 1, 'Vou investigar esse bug', 'Tech Team', '2024-01-15 11:00:00'),
    (2, 1, 'Bug corrigido na branch develop', 'Desenvolvedor', '2024-01-15 16:30:00'),
    (3, 99, 'Este comentario esta orfao', 'Usuario', '2024-01-16 10:00:00'),
]


def run_migrations_and_seed() -> None:
    with app.app_context():
        upgrade()

        db.session.execute(text('PRAGMA foreign_keys = ON'))

        for demanda in SEED_DEMANDAS:
            db.session.execute(
                text(
                    'INSERT OR IGNORE INTO demandas '
                    '(id, titulo, descricao, solicitante, prioridade, data_criacao) '
                    'VALUES (:id, :titulo, :descricao, :solicitante, :prioridade, :data_criacao)'
                ),
                {
                    'id': demanda[0],
                    'titulo': demanda[1],
                    'descricao': demanda[2],
                    'solicitante': demanda[3],
                    'prioridade': demanda[4],
                    'data_criacao': demanda[5],
                },
            )

        for comentario in SEED_COMENTARIOS:
            db.session.execute(
                text(
                    'INSERT OR IGNORE INTO comentarios '
                    '(id, demanda_id, comentario, autor, data) '
                    'VALUES (:id, :demanda_id, :comentario, :autor, :data)'
                ),
                {
                    'id': comentario[0],
                    'demanda_id': comentario[1],
                    'comentario': comentario[2],
                    'autor': comentario[3],
                    'data': comentario[4],
                },
            )

        db.session.commit()


if __name__ == '__main__':
    run_migrations_and_seed()
    print('Migracoes aplicadas e dados iniciais garantidos com sucesso!')
