"""Utility to manage API tokens in system_users table.
Usage:
    python manage_tokens.py create --username NAME [--token TOKEN] [--user_type externo]
    python manage_tokens.py list
"""
import sqlite3
import argparse
import secrets
import sys
from pathlib import Path
import hashlib

# Ensure project root is on sys.path so we can import config
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import DATABASE_PATH


def connect_db():
    return sqlite3.connect(DATABASE_PATH)


def ensure_column(cur, table, column, column_type):
    cur.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cur.fetchall()}
    if column not in columns:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def hash_token(token, salt_hex, iterations=100_000):
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac('sha256', token.encode('utf-8'), salt, iterations)
    return digest.hex()


def migrate_plain_tokens(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, token, token_salt FROM system_users")
    rows = cur.fetchall()
    for row_id, token_value, token_salt in rows:
        if not token_value or token_salt:
            continue
        salt_hex = secrets.token_bytes(16).hex()
        token_hash = hash_token(token_value, salt_hex)
        cur.execute(
            "UPDATE system_users SET token = ?, token_salt = ? WHERE id = ?",
            (token_hash, salt_hex, row_id)
        )
    conn.commit()


def ensure_table():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS system_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            user_type TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    ensure_column(cur, 'system_users', 'token_salt', 'TEXT')
    conn.commit()
    migrate_plain_tokens(conn)
    conn.close()


def create_token(username, token=None, user_type='externo'):
    if token is None:
        token = secrets.token_urlsafe(32)
    salt_hex = secrets.token_bytes(16).hex()
    token_hash = hash_token(token, salt_hex)
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO system_users (username, token, token_salt, user_type, data_criacao) '
            'VALUES (?,?,?,?,?)',
            (username, token_hash, salt_hex, user_type, now)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print('Token already exists or constraint violation')
        conn.close()
        return None
    conn.close()
    return token


def list_tokens():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username, token, user_type, data_criacao FROM system_users')
    rows = cur.fetchall()
    conn.close()
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd')

    p_create = sub.add_parser('create')
    p_create.add_argument('--username', required=True)
    p_create.add_argument('--token', required=False)
    p_create.add_argument('--user_type', default='externo')

    p_list = sub.add_parser('list')

    args = parser.parse_args()
    ensure_table()
    if args.cmd == 'create':
        t = create_token(args.username, args.token, args.user_type)
        if t:
            print('Created token:', t)
        else:
            print('Failed to create token')
    elif args.cmd == 'list':
        for r in list_tokens():
            print(r)
    else:
        parser.print_help()
