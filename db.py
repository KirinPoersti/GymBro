import sqlite3
from contextlib import closing

DB_PATH = "database.db"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute(sql, params=()):
    with connect() as con, closing(con.cursor()) as cur:
        cur.execute(sql, params)
        con.commit()

def query_one(sql, params=()):
    with connect() as con, closing(con.cursor()) as cur:
        cur.execute(sql, params)
        return cur.fetchone()
