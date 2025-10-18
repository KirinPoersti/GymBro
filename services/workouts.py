from typing import List, Dict, Set

import db


def get_or_create_workout(user_id: int, wdate: str) -> dict:
    if not db.query_one("SELECT id FROM users WHERE id=?", (user_id,)):
        raise ValueError("Invalid user for workout creation")
    w = db.query_one(
        "SELECT * FROM workouts WHERE user_id=? AND wdate=?",
        (user_id, wdate),
    )
    if not w:
        db.execute(
            "INSERT INTO workouts (user_id, wdate) VALUES (?, ?)",
            (user_id, wdate),
        )
        w = db.query_one(
            "SELECT * FROM workouts WHERE user_id=? AND wdate=?",
            (user_id, wdate),
        )
    return w


def save_workout(user_id: int, wdate: str, exercises: List[Dict]) -> None:
    w = get_or_create_workout(user_id, wdate)

    db.execute(
        "DELETE FROM sets WHERE exercise_id IN (SELECT id FROM exercises WHERE workout_id=?)",
        (w["id"],),
    )
    db.execute("DELETE FROM exercises WHERE workout_id=?", (w["id"],))

    inserted = 0
    for idx, ex in enumerate(exercises):
        name = (ex.get("name") or "").strip()
        raw_sets = ex.get("sets", []) or []

        sets_in = []
        for s in raw_sets:
            reps_raw = s.get("reps")
            weight_raw = s.get("weight")
            has_reps = reps_raw not in (None, "")
            has_weight = weight_raw not in (None, "")
            if has_reps or has_weight:
                reps = int(reps_raw) if has_reps else None
                weight = (
                    float(str(weight_raw).replace(",", ".")) if has_weight else None
                )
                sets_in.append({"reps": reps, "weight": weight})

        if not name and not sets_in:
            continue

        db.execute(
            "INSERT INTO exercises (workout_id, name, ord) VALUES (?, ?, ?)",
            (w["id"], name or f"Exercise {idx+1}", idx),
        )
        ex_id = db.query_one(
            "SELECT id FROM exercises WHERE workout_id=? AND ord=?",
            (w["id"], idx),
        )["id"]

        inserted += 1

        for s_idx, s in enumerate(sets_in, start=1):
            db.execute(
                "INSERT INTO sets (exercise_id, set_no, reps, weight) VALUES (?, ?, ?, ?)",
                (ex_id, s_idx, s["reps"], s["weight"]),
            )

    if inserted == 0:
        db.execute("DELETE FROM workouts WHERE id=?", (w["id"],))


def fetch_workout_payload(user_id: int, wdate: str) -> List[Dict]:
    w = db.query_one("SELECT * FROM workouts WHERE user_id=? AND wdate=?", (user_id, wdate))
    payload: List[Dict] = []
    if not w:
        return payload
    ex_rows = db.query("SELECT * FROM exercises WHERE workout_id=? ORDER BY ord", (w["id"],))
    for e in ex_rows:
        sets_rows = db.query(
            "SELECT * FROM sets WHERE exercise_id=? ORDER BY set_no", (e["id"],)
        )
        payload.append(
            {
                "name": e.get("name") or "",
                "sets": [
                    {
                        "reps": (s.get("reps") if s.get("reps") is not None else ""),
                        "weight": (
                            s.get("weight") if s.get("weight") is not None else ""
                        ),
                    }
                    for s in sets_rows
                ],
            }
        )
    return payload


def workout_dates_for_range(user_id: int, start_iso: str, end_iso: str) -> Set[str]:
    rows = db.query(
        """
        SELECT DISTINCT w.wdate
        FROM workouts w
        JOIN exercises e ON e.workout_id = w.id
        JOIN sets s      ON s.exercise_id = e.id
        WHERE w.user_id = ? AND w.wdate BETWEEN ? AND ?
        """,
        (user_id, start_iso, end_iso),
    )
    return {r["wdate"] for r in rows}

