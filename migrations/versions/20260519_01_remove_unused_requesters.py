"""remove requesters without demands

Revision ID: 20260519_01
Revises: 20260422_01
Create Date: 2026-05-19 00:00:00

"""

from alembic import op


revision = '20260519_01'
down_revision = '20260422_01'
branch_labels = None
depends_on = None

def upgrade():
    op.execute(
        """
        DELETE FROM requesters
        WHERE nome IN ('Tech Team', 'Equipe Suporte', 'Time Produto')
        """
    )


def downgrade():
    op.execute(
        """
        INSERT INTO requesters (nome, email, cargo, data_criacao)
        VALUES
            ('Tech Team', 'tech.team@empresa.com', 'Equipe Tecnica', '2024-01-15 09:10:00'),
            ('Equipe Suporte', 'suporte@empresa.com', 'Suporte', '2024-01-15 09:15:00'),
            ('Time Produto', 'produto@empresa.com', 'Produto', '2024-01-15 09:20:00')
        """
    )
