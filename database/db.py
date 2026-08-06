import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys, '_MEIPASS'):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# cria a pasta database se não existir
DB_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "joias.db")

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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tipos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo        TEXT NOT NULL UNIQUE
    )
""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS material (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    material    TEXT NOT NULL UNIQUE   
    )
""")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configs (
            id INTEGER PRIMARY KEY,
            chave_pix TEXT NOT NULL,
            nome TEXT NOT NULL,
            cidade TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()