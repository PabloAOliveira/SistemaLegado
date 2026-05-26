"""add system_users table for external API tokens

Revision ID: 20260519_01
Revises: 20260512_01
Create Date: 2026-05-19 00:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260519_01'
down_revision = '20260512_01'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Create table if it doesn't exist (safe for sqlite)
    if 'system_users' not in inspector.get_table_names():
        op.create_table(
            'system_users',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('username', sa.Text(), nullable=False),
            sa.Column('token', sa.Text(), nullable=False, unique=True),
            sa.Column('user_type', sa.Text(), nullable=False),
            sa.Column('data_criacao', sa.Text(), nullable=False),
            sqlite_autoincrement=True,
        )

    # Seed a sample external user token (won't fail if already present)
    op.execute(
        """
        INSERT OR IGNORE INTO system_users (username, token, user_type, data_criacao)
        VALUES ('external_user', 'external-token-123', 'externo', datetime('now'))
        """
    )


def downgrade():
    op.drop_table('system_users')

