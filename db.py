# db.py
import sqlite3

DB_PATH = "database.db"

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # dict-like rows
    return conn

def execute(sql: str, params=()):
    """Run INSERT/UPDATE/DELETE. Returns lastrowid (if any)."""
    with _connect() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid

def query(sql: str, params=()):
    """Run SELECT and return a list of dict rows."""
    with _connect() as conn:
        cur = conn.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]

def query_one(sql: str, params=()):
    """Run SELECT and return the first row as a dict (or None)."""
    rows = query(sql, params)
    return rows[0] if rows else None
