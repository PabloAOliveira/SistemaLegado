"""hash system_users tokens with salt

Revision ID: 20260524_01
Revises: 20260519_01
Create Date: 2026-05-24 00:00:00

"""
from alembic import op
import sqlalchemy as sa
import hashlib
import secrets


# revision identifiers, used by Alembic.
revision = '20260524_01'
down_revision = '20260519_01'
branch_labels = None
depends_on = None


def _hash_token(token, salt_hex, iterations=100_000):
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac('sha256', token.encode('utf-8'), salt, iterations)
    return digest.hex()


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'system_users' not in inspector.get_table_names():
        op.create_table(
            'system_users',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('username', sa.Text(), nullable=False),
            sa.Column('token', sa.Text(), nullable=False, unique=True),
            sa.Column('token_salt', sa.Text(), nullable=True),
            sa.Column('user_type', sa.Text(), nullable=False),
            sa.Column('data_criacao', sa.Text(), nullable=False),
            sqlite_autoincrement=True,
        )
        return

    columns = {col['name'] for col in inspector.get_columns('system_users')}
    if 'token_salt' not in columns:
        op.add_column('system_users', sa.Column('token_salt', sa.Text(), nullable=True))

    connection = op.get_bind()
    rows = connection.execute(sa.text(
        'SELECT id, token, token_salt FROM system_users'
    )).fetchall()

    for row_id, token_value, token_salt in rows:
        if not token_value or token_salt:
            continue
        salt_hex = secrets.token_bytes(16).hex()
        token_hash = _hash_token(token_value, salt_hex)
        connection.execute(
            sa.text(
                'UPDATE system_users SET token = :token, token_salt = :salt WHERE id = :id'
            ),
            {'token': token_hash, 'salt': salt_hex, 'id': row_id}
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'system_users' not in inspector.get_table_names():
        return
    columns = {col['name'] for col in inspector.get_columns('system_users')}
    if 'token_salt' in columns:
        op.drop_column('system_users', 'token_salt')

