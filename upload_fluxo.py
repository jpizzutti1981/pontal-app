import sqlite3

# --- CONFIGURAÇÃO ---
DATABASE = "indicadores.db"
TIPO     = "NOI"

# --- DADOS A INSERIR ---
# (data_referencia, mes, mes_nome, ano, realizado, meta, ano_anterior)
dados = [
    # 2024 (sem meta/ano_anterior)
    ("2024-01-01",  1, "janeiro",   2024, -147361.9917, None,      None),
    ("2024-02-01",  2, "fevereiro", 2024,  273585.1865, None,      None),
    ("2024-03-01",  3, "março",     2024,  -11873.35248, None,     None),
    ("2024-04-01",  4, "abril",     2024,    -333.4760705, None,  None),
    ("2024-05-01",  5, "maio",      2024, -504728.019,   None,      None),
    ("2024-06-01",  6, "junho",     2024, -443205.6304,  None,      None),
    ("2024-07-01",  7, "julho",     2024, -387018.9692,  None,      None),
    ("2024-08-01",  8, "agosto",    2024, -242733.6414,  None,      None),
    ("2024-09-01",  9, "setembro",  2024,  -25204.65,    None,      None),
    ("2024-10-01", 10, "outubro",   2024, -188626.8,     None,      None),
    ("2024-11-01", 11, "novembro",  2024, -329191.15,    None,      None),
    ("2024-12-01", 12, "dezembro",  2024,  -74751.0,     None,      None),

    # 2025 (até junho, com meta e ano_anterior)
    ("2025-01-01",  1, "janeiro",   2025, -519961.0,  -626111.0,  -147362.0),
    ("2025-02-01",  2, "fevereiro", 2025, -330202.0,  -254647.0,   273585.0),
    ("2025-03-01",  3, "março",     2025, -430385.0,  -351802.0,   -11873.0),
    ("2025-04-01",  4, "abril",     2025, -433752.0,  -255594.0,    -333000.0),
    ("2025-05-01",  5, "maio",      2025, -369126.0,   -44558.0,     22723.0),
    ("2025-06-01",  6, "junho",     2025, -275910.0,    14112.0,     14112.0),
]

def subir_noi():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Garante que a tabela existe
    c.execute("""
    CREATE TABLE IF NOT EXISTS indicadores (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo            TEXT    NOT NULL,
        ano             INTEGER,
        mes             INTEGER,
        mes_nome        TEXT,
        data_referencia TEXT,
        meta            REAL,
        realizado       REAL,
        ano_anterior    REAL
    )
    """)

    # Adiciona coluna mes_nome se faltar
    c.execute("PRAGMA table_info(indicadores)")
    if not any(col[1] == "mes_nome" for col in c.fetchall()):
        c.execute("ALTER TABLE indicadores ADD COLUMN mes_nome TEXT")

    # Remove registros antigos deste indicador
    anos = sorted({d[3] for d in dados})
    for ano in anos:
        c.execute(
            "DELETE FROM indicadores WHERE tipo = ? AND ano = ?",
            (TIPO, ano)
        )

    # Insere novos dados
    for dr, mes, nome, ano, real, meta, ant in dados:
        c.execute("""
            INSERT INTO indicadores
            (tipo, ano, mes, mes_nome, data_referencia, meta, realizado, ano_anterior)
            VALUES (?,    ?,   ?,     ?,         ?,               ?,    ?,         ?)
        """, (
            TIPO,
            ano,
            mes,
            nome,
            dr,
            float(meta) if meta is not None else None,
            float(real),
            float(ant)  if ant  is not None else None,
        ))

    conn.commit()
    conn.close()
    print(f"[OK] Subidos {len(dados)} registros de “{TIPO}”.")

if __name__ == "__main__":
    subir_noi()
