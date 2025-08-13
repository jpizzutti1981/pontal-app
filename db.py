import sqlite3

# Conecta ou cria o banco
conn = sqlite3.connect("indicadores.db")
cursor = conn.cursor()

# Tabela de usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('admin', 'user'))
);
""")

# Tabela de indicadores
cursor.execute("""
CREATE TABLE IF NOT EXISTS indicadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    data_referencia TEXT,
    meta REAL,
    realizado REAL,
    ano_anterior REAL
);
""")

# Usuários iniciais
cursor.execute("INSERT OR IGNORE INTO usuarios (nome, usuario, senha, tipo) VALUES ('Administrador', 'admin', '123', 'admin')")
cursor.execute("INSERT OR IGNORE INTO usuarios (nome, usuario, senha, tipo) VALUES ('Usuário Comum', 'user', '123', 'user')")

# Indicador inicial de Vendas
cursor.execute("""
INSERT INTO indicadores (tipo, ano, mes, data_referencia, meta, realizado, ano_anterior)
VALUES ('Vendas', 2025, 7, '2025-07-01', 220000, 210000, 195000)
""")

cursor.execute("""
INSERT INTO indicadores (tipo, ano, mes, data_referencia, meta, realizado, ano_anterior)
VALUES ('Vendas', 2025, 1, '2025-01-01', 200000, 190000, 170000)
""")

conn.commit()
conn.close()

print("Banco criado com sucesso!")