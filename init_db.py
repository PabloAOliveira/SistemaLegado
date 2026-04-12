import sqlite3


conn = sqlite3.connect('demandas.db')
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS demandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    solicitante TEXT,
    prioridade TEXT,
    data_criacao TEXT
)
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS comentarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    demanda_id INTEGER,
    comentario TEXT,
    autor TEXT,
    data TEXT,
    FOREIGN KEY (demanda_id) REFERENCES demandas(id)
)
''')


cursor.execute("DELETE FROM comentarios")
cursor.execute("DELETE FROM demandas")

cursor.execute("INSERT INTO demandas VALUES (1, 'Corrigir bug no login', 'Usuários não conseguem fazer login', 'João Silva', 'alta', '2024-01-15 10:30:00')")
cursor.execute("INSERT INTO demandas VALUES (2, 'Implementar relatório de vendas', 'Precisamos de um relatório mensal', 'Maria Santos', 'media', '2024-01-16 14:20:00')")
cursor.execute("INSERT INTO demandas VALUES (3, 'Melhorar performance', 'Sistema está lento', 'Pedro Costa', 'baixa', '2024-01-17 09:15:00')")
cursor.execute("INSERT INTO demandas VALUES (99, 'Adicionar filtros', 'Usuários querem filtrar demandas', 'Ana Lima', 'alta', '2024-01-18 11:00:00')")

cursor.execute("INSERT INTO comentarios VALUES (1, 1, 'Vou investigar esse bug', 'Tech Team', '2024-01-15 11:00:00')")
cursor.execute("INSERT INTO comentarios VALUES (2, 1, 'Bug corrigido na branch develop', 'Desenvolvedor', '2024-01-15 16:30:00')")
cursor.execute("INSERT INTO comentarios VALUES (3, 99, 'Este comentário está órfão', 'Usuário', '2024-01-16 10:00:00')")

conn.commit()
conn.close()

print("Banco de dados criado com sucesso!")
