import json
from typing import List, Dict, Optional

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
        
        -- Likes: one per user per post
        CREATE TABLE IF NOT EXISTS meal_forum_likes (
          id         INTEGER PRIMARY KEY AUTOINCREMENT,
          post_id    INTEGER NOT NULL,
          user_id    INTEGER NOT NULL,
          created_at TEXT DEFAULT (datetime('now')),
          UNIQUE(post_id, user_id),
          FOREIGN KEY (post_id) REFERENCES meal_forum_posts(id) ON DELETE CASCADE,
          FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_mfl_post ON meal_forum_likes(post_id);
        """
    )
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
    if not db.query_one("SELECT id FROM users WHERE id=?", (user_id,)):
        raise ValueError("Invalid user for forum post")
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


def list_posts(limit: Optional[int] = None, current_user_id: Optional[int] = None):
    ensure_schema()
    lim = f" LIMIT {int(limit)}" if limit else ""
    rows = db.query(
        "SELECT p.*, u.username,"
        "       COALESCE((SELECT COUNT(1) FROM meal_forum_likes l WHERE l.post_id=p.id), 0) AS likes_count"
        "  FROM meal_forum_posts p JOIN users u ON u.id=p.user_id"
        " ORDER BY datetime(p.created_at) DESC" + lim
    )
    for r in rows:
        r["items"] = json.loads(r["items_json"]) if r.get("items_json") else []
        r["owned_by_me"] = (r.get("user_id") == current_user_id)
        if current_user_id is not None:
            r["liked_by_me"] = bool(
                db.query_one(
                    "SELECT 1 AS x FROM meal_forum_likes WHERE post_id=? AND user_id=?",
                    (r["id"], current_user_id),
                )
            )
    return rows


def get_post(pid: int):
    ensure_schema()
    r = db.query_one(
        "SELECT p.*, u.username,"
        "       COALESCE((SELECT COUNT(1) FROM meal_forum_likes l WHERE l.post_id=p.id), 0) AS likes_count"
        "  FROM meal_forum_posts p JOIN users u ON u.id=p.user_id WHERE p.id=?",
        (pid,),
    )
    if r:
        r["items"] = json.loads(r["items_json"]) if r.get("items_json") else []
    return r


def update_post(pid: int, title: str, items: List[Dict]) -> None:
    ensure_schema()
    t = (title or "").strip()[:80] or "Untitled plan"
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

    db.execute(
        """UPDATE meal_forum_posts
           SET title=?, items_json=?, calories_total=?, protein_total=?, carbs_total=?, weight_total=?
           WHERE id=?""",
        (t, json.dumps(norm_items), cal_t, p_t, c_t, w_t, pid),
    )


def search_posts_unsafe(term: str):
    ensure_schema()
    # CSB OWASP 2021 A03 - Injection (VULNERABLE DEMO):
    # User-controlled search text is formatted directly into SQL.
    sql = (
        "SELECT p.id, p.title, p.calories_total, u.username "
        "FROM meal_forum_posts p JOIN users u ON u.id=p.user_id "
        f"WHERE p.title LIKE '%{term}%' OR u.username LIKE '%{term}%' "
        "ORDER BY datetime(p.created_at) DESC"
    )
    rows = db.query(sql)
    # SECURE FIX:
    # like = f"%{term}%"
    # rows = db.query(
    #     "SELECT p.id, p.title, p.calories_total, u.username "
    #     "FROM meal_forum_posts p JOIN users u ON u.id=p.user_id "
    #     "WHERE p.title LIKE ? OR u.username LIKE ? "
    #     "ORDER BY datetime(p.created_at) DESC",
    #     (like, like),
    # )
    return rows


def like_post(pid: int, user_id: int) -> Dict:
    """Attempt to like a post. Idempotent: if already liked, returns unchanged count."""
    ensure_schema()
    try:
        db.execute(
            "INSERT OR IGNORE INTO meal_forum_likes(post_id, user_id) VALUES (?,?)",
            (pid, user_id),
        )
    except Exception:
        pass
    row = db.query_one(
        "SELECT COUNT(1) AS c FROM meal_forum_likes WHERE post_id=?",
        (pid,),
    )
    return {"likes_count": (row["c"] if row else 0)}
