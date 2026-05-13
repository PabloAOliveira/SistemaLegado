"""add dashboard fields to demands

Revision ID: 20260512_01
Revises: 20260422_01
Create Date: 2026-05-12 00:00:00

"""

from alembic import op
import sqlalchemy as sa


revision = '20260512_01'
down_revision = '20260422_01'
branch_labels = None
depends_on = None


def _column_names(inspector, table_name: str) -> set:
    return {column['name'] for column in inspector.get_columns(table_name)}


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = _column_names(inspector, 'demandas')

    with op.batch_alter_table('demandas') as batch_op:
        if 'status' not in columns:
            batch_op.add_column(sa.Column('status', sa.Text(), nullable=False, server_default='aberta'))
        if 'responsavel' not in columns:
            batch_op.add_column(sa.Column('responsavel', sa.Text(), nullable=True))
        if 'prazo' not in columns:
            batch_op.add_column(sa.Column('prazo', sa.Text(), nullable=True))
        if 'data_conclusao' not in columns:
            batch_op.add_column(sa.Column('data_conclusao', sa.Text(), nullable=True))

    op.execute(
        """
        UPDATE demandas
        SET responsavel = solicitante
        WHERE responsavel IS NULL OR TRIM(responsavel) = ''
        """
    )
    op.execute(
        """
        UPDATE demandas
        SET prazo = COALESCE(date(data_criacao, '+7 days'), date('now', '+7 days'))
        """
    )
    op.execute(
        """
        UPDATE demandas
        SET prioridade = 'baixa'
        WHERE prioridade IS NULL
           OR TRIM(prioridade) = ''
           OR LOWER(TRIM(prioridade)) NOT IN ('alta', 'media', 'média', 'baixa')
        """
    )


def downgrade():
    with op.batch_alter_table('demandas') as batch_op:
        batch_op.drop_column('data_conclusao')
        batch_op.drop_column('prazo')
        batch_op.drop_column('responsavel')
        batch_op.drop_column('status')
