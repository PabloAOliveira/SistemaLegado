from flask_migrate import upgrade
from sqlalchemy import text
from app import app
from models import db

SEED_DEMANDAS = [
    (1, 'Corrigir bug no login', 'Usuarios nao conseguem fazer login', 'Joao Silva', 'alta', '2024-01-15 10:30:00'),
    (2, 'Implementar relatorio de vendas', 'Precisamos de um relatorio mensal', 'Maria Santos', 'media', '2024-01-16 14:20:00'),
    (3, 'Melhorar performance', 'Sistema esta lento', 'Pedro Costa', 'baixa', '2024-01-17 09:15:00'),
    (99, 'Adicionar filtros', 'Usuarios querem filtrar demandas', 'Ana Lima', 'alta', '2024-01-18 11:00:00'),
]

SEED_COMENTARIOS = [
    (1, 1, 'Vou investigar esse bug', 'Tech Team', '2024-01-15 11:00:00'),
    (2, 1, 'Bug corrigido na branch develop', 'Desenvolvedor', '2024-01-15 16:30:00'),
    (3, 99, 'Este comentario esta orfao', 'Usuario', '2024-01-16 10:00:00'),
]

SEED_REQUESTERS = [
    ('Joao Silva', 'joao.silva@empresa.com', 'Analista', '2024-01-15 09:00:00'),
    ('Maria Santos', 'maria.santos@empresa.com', 'Coordenadora', '2024-01-15 09:05:00'),
    ('Tech Team', 'tech.team@empresa.com', 'Equipe Tecnica', '2024-01-15 09:10:00'),
    ('Equipe Suporte', 'suporte@empresa.com', 'Suporte', '2024-01-15 09:15:00'),
    ('Time Produto', 'produto@empresa.com', 'Produto', '2024-01-15 09:20:00'),
]

def run_migrations_and_seed() -> None:
    with app.app_context():
        print("Rodando migrações...")
        upgrade()

        # Ativa chaves estrangeiras no SQLite
        db.session.execute(text('PRAGMA foreign_keys = ON'))

        print("Limpando dados antigos...")
        db.session.execute(text('DELETE FROM comentarios'))
        db.session.execute(text('DELETE FROM demandas'))
        db.session.execute(text('DELETE FROM requesters'))

        print("Inserindo demandas iniciais...")
        for demanda in SEED_DEMANDAS:
            db.session.execute(
                text(
                    'INSERT INTO demandas '
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

        print("Inserindo comentários...")
        for comentario in SEED_COMENTARIOS:
            db.session.execute(
                text(
                    'INSERT INTO comentarios '
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

        print("Inserindo solicitantes...")
        for requester in SEED_REQUESTERS:
            db.session.execute(
                text(
                    'INSERT INTO requesters '
                    '(nome, email, cargo, data_criacao) '
                    'VALUES (:nome, :email, :cargo, :data_criacao)'
                ),
                {
                    'nome': requester[0],
                    'email': requester[1],
                    'cargo': requester[2],
                    'data_criacao': requester[3],
                },
            )

        db.session.commit()
        print("Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    run_migrations_and_seed()
