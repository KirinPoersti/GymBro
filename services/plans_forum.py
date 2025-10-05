import json
from typing import List, Dict

import db


def ensure_schema() -> None:
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS meal_forum_posts (
          id              INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id         INTEGER NOT NULL,
          title           TEXT NOT NULL,
          items_json      TEXT NOT NULL,
          calories_total  INTEGER,
          protein_total   REAL,
          carbs_total     REAL,
          weight_total    REAL,
          created_at      TEXT DEFAULT (datetime('now')),
          FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_mfp_created ON meal_forum_posts(created_at DESC);
        """
    )
    # Backfill weight_total if the table already existed
    cols = {c["name"] for c in db.query("PRAGMA table_info(meal_forum_posts)")}
    if "weight_total" not in cols:
        db.execute("ALTER TABLE meal_forum_posts ADD COLUMN weight_total REAL")


def _num(x, tp=float):
    if x in (None, ""): return 0 if tp is int else 0.0
    try:
        v = float(str(x).replace(",", "."))
        return int(v) if tp is int else float(v)
    except Exception:
        return 0 if tp is int else 0.0


def create_post(user_id: int, title: str, items: List[Dict]) -> int:
    ensure_schema()
    t = (title or "").strip()[:80]
    if not t:
        t = "Untitled plan"

    norm_items = []
    cal_t = 0
    p_t = 0.0
    c_t = 0.0
    w_t = 0.0
    for it in items or []:
        nm = (it.get("name") or "").strip()
        w = _num(it.get("weight"), float)
        p = _num(it.get("protein"), float)
        c = _num(it.get("carbs"), float)
        k = _num(it.get("calories"), int)
        if nm or w or p or c or k:
            norm_items.append({"name": nm, "weight": w, "protein": p, "carbs": c, "calories": k})
            w_t += w
            cal_t += k
            p_t += p
            c_t += c

    post_id = db.execute(
        "INSERT INTO meal_forum_posts (user_id, title, items_json, calories_total, protein_total, carbs_total, weight_total)"
        " VALUES (?,?,?,?,?,?,?)",
        (user_id, t, json.dumps(norm_items), cal_t, p_t, c_t, w_t),
    )
    return post_id


def list_posts(limit: int | None = None):
    ensure_schema()
    lim = f" LIMIT {int(limit)}" if limit else ""
    rows = db.query(
        "SELECT p.*, u.username FROM meal_forum_posts p JOIN users u ON u.id=p.user_id"
        " ORDER BY datetime(p.created_at) DESC" + lim
    )
    for r in rows:
        r["items"] = json.loads(r["items_json"]) if r.get("items_json") else []
    return rows


def get_post(pid: int):
    ensure_schema()
    r = db.query_one(
        "SELECT p.*, u.username FROM meal_forum_posts p JOIN users u ON u.id=p.user_id WHERE p.id=?",
        (pid,),
    )
    if r:
        r["items"] = json.loads(r["items_json"]) if r.get("items_json") else []
    return r
