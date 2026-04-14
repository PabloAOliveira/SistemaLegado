"""baseline schema com prioridade e ids autoincrementais

Revision ID: 20260407_01
Revises:
Create Date: 2026-04-07 00:00:00

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260407_01'
down_revision = '9f3a2d1c7b8e'
branch_labels = None
depends_on = None


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_names(inspector, table_name: str) -> set:
    return {column['name'] for column in inspector.get_columns(table_name)}


def _recreate_demandas_sqlite(has_prioridade: bool) -> None:
    prioridade_expr = 'prioridade' if has_prioridade else "''"

    op.execute('PRAGMA foreign_keys=OFF')
    op.execute('DROP TABLE IF EXISTS demandas_new')
    op.execute(
        """
        CREATE TABLE demandas_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            solicitante TEXT,
            prioridade TEXT,
            data_criacao TEXT
        )
        """
    )
    op.execute(
        f"""
        INSERT INTO demandas_new (id, titulo, descricao, solicitante, prioridade, data_criacao)
        SELECT id, titulo, descricao, solicitante, {prioridade_expr}, data_criacao
        FROM demandas
        """
    )
    op.execute('DROP TABLE demandas')
    op.execute('ALTER TABLE demandas_new RENAME TO demandas')
    op.execute('PRAGMA foreign_keys=ON')


def _recreate_comentarios_sqlite() -> None:
    op.execute('PRAGMA foreign_keys=OFF')
    op.execute('DROP TABLE IF EXISTS comentarios_new')
    op.execute(
        """
        CREATE TABLE comentarios_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demanda_id INTEGER NOT NULL,
            comentario TEXT,
            autor TEXT,
            data TEXT,
            FOREIGN KEY(demanda_id) REFERENCES demandas(id)
        )
        """
    )
    op.execute(
        """
        INSERT INTO comentarios_new (demanda_id, comentario, autor, data)
        SELECT c.demanda_id, c.comentario, c.autor, c.data
        FROM comentarios c
        WHERE EXISTS (
            SELECT 1
            FROM demandas d
            WHERE d.id = c.demanda_id
        )
        ORDER BY c.id
        """
    )
    op.execute('DROP TABLE comentarios')
    op.execute('ALTER TABLE comentarios_new RENAME TO comentarios')
    op.execute('PRAGMA foreign_keys=ON')


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, 'demandas'):
        op.create_table(
            'demandas',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('titulo', sa.Text(), nullable=False),
            sa.Column('descricao', sa.Text(), nullable=True),
            sa.Column('solicitante', sa.Text(), nullable=True),
            sa.Column('prioridade', sa.Text(), nullable=True, server_default=''),
            sa.Column('data_criacao', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sqlite_autoincrement=True,
        )
    else:
        demandas_columns = _column_names(inspector, 'demandas')
        if bind.dialect.name == 'sqlite':
            _recreate_demandas_sqlite(has_prioridade='prioridade' in demandas_columns)
        elif 'prioridade' not in demandas_columns:
            op.add_column('demandas', sa.Column('prioridade', sa.Text(), nullable=True, server_default=''))

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, 'comentarios'):
        op.create_table(
            'comentarios',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('demanda_id', sa.Integer(), nullable=False),
            sa.Column('comentario', sa.Text(), nullable=True),
            sa.Column('autor', sa.Text(), nullable=True),
            sa.Column('data', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['demanda_id'], ['demandas.id']),
            sa.PrimaryKeyConstraint('id'),
            sqlite_autoincrement=True,
        )
    elif bind.dialect.name == 'sqlite':
        _recreate_comentarios_sqlite()


def downgrade():
    bind = op.get_bind()

    if bind.dialect.name == 'sqlite':
        op.execute('PRAGMA foreign_keys=OFF')
        op.execute(
            """
            CREATE TABLE demandas_old (
                id INTEGER PRIMARY KEY,
                titulo TEXT NOT NULL,
                descricao TEXT,
                solicitante TEXT,
                data_criacao TEXT
            )
            """
        )
        op.execute(
            """
            INSERT INTO demandas_old (id, titulo, descricao, solicitante, data_criacao)
            SELECT id, titulo, descricao, solicitante, data_criacao
            FROM demandas
            """
        )
        op.execute('DROP TABLE demandas')
        op.execute('ALTER TABLE demandas_old RENAME TO demandas')
        op.execute('PRAGMA foreign_keys=ON')
    else:
        with op.batch_alter_table('demandas') as batch_op:
            batch_op.drop_column('prioridade')

