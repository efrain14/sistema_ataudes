import sqlite3
from config import DB_PATH

def get_connection():
    """Retorna una conexión SQLite con row_factory activado."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn