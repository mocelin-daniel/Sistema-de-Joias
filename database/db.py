import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "joias.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS joias (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        nome      TEXT NOT NULL,
        tipo      TEXT NOT NULL,
        material  TEXT NOT NULL,
        quantidade INTEGER NOT NULL DEFAULT 0,
        valor     REAL NOT NULL,
        descricao TEXT
    )
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        nome      TEXT NOT NULL,
        cpf       TEXT NOT NULL UNIQUE,
        numero  TEXT NOT NULL,
        email     TEXT NOT NULL,
        endereco  TEXT NOT NULL
    )
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id       INTEGER NOT NULL,
        joia_id          INTEGER NOT NULL,
        valor_joia       REAL NOT NULL,
        quantidade INTEGER NOT NULL DEFAULT 0,
        valor_total     REAL NOT NULL,
        data_venda TEXT DEFAULT (datetime('now', 'localtime')),
        pagamento TEXT, -- futuramente criar opção "debito, credito, pix, dinheiro,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (joia_id) REFERENCES joias(id)
    )
""")
    
    conn.commit()
    conn.close()