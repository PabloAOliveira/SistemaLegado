"""add requesters table

Revision ID: 20260422_01
Revises: 20260407_01
Create Date: 2026-04-22 00:00:00

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260422_01'
down_revision = '20260407_01'
branch_labels = None
depends_on = None


DEFAULT_REQUESTERS = (
    {"nome": "Joao Silva", "email": "joao.silva@empresa.com", "cargo": "Analista"},
    {"nome": "Maria Santos", "email": "maria.santos@empresa.com", "cargo": "Coordenadora"},
    {"nome": "Tech Team", "email": "tech.team@empresa.com", "cargo": "Equipe Tecnica"},
    {"nome": "Equipe Suporte", "email": "suporte@empresa.com", "cargo": "Suporte"},
    {"nome": "Time Produto", "email": "produto@empresa.com", "cargo": "Produto"},
)


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, 'requesters'):
        op.create_table(
            'requesters',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nome', sa.Text(), nullable=False),
            sa.Column('email', sa.Text(), nullable=False),
            sa.Column('cargo', sa.Text(), nullable=False),
            sa.Column('data_criacao', sa.Text(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email'),
            sqlite_autoincrement=True,
        )

    requesters_table = sa.table(
        'requesters',
        sa.column('nome', sa.Text()),
        sa.column('email', sa.Text()),
        sa.column('cargo', sa.Text()),
        sa.column('data_criacao', sa.Text()),
    )

    for requester in DEFAULT_REQUESTERS:
        op.execute(
            requesters_table.insert().prefix_with("OR IGNORE").values(
                nome=requester["nome"],
                email=requester["email"],
                cargo=requester["cargo"],
                data_criacao='2026-04-22 00:00:00',
            )
        )


def downgrade():
    op.drop_table('requesters')
