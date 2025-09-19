import os, sqlite3

# Configurable path (use env var or default to database.db)
DB_PATH = os.environ.get("GYMBRO_DB", "database.db")

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # dict-like rows
    # Ensure foreign keys are enforced
    conn.execute("PRAGMA foreign_keys = ON;")
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

def executescript(script: str):
    """Run multiple SQL statements (e.g. schema.sql)."""
    with _connect() as conn:
        conn.executescript(script)
        conn.commit()
