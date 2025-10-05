from datetime import date, datetime, timedelta
from typing import List, Dict

import db


def _parse_date(s: str, default: date) -> date:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return default


def reps_leaderboard(start_iso: str | None, end_iso: str | None) -> List[Dict]:
    today = date.today()
    default_start = today - timedelta(days=30)
    start_d = _parse_date(start_iso, default_start) if start_iso else default_start
    end_d = _parse_date(end_iso, today) if end_iso else today

    if end_d < start_d:
        start_d, end_d = end_d, start_d

    rows = db.query(
        """
        SELECT u.username AS username, COALESCE(SUM(s.reps), 0) AS total_reps
        FROM users u
        JOIN workouts w   ON w.user_id = u.id
        JOIN exercises e  ON e.workout_id = w.id
        JOIN sets s       ON s.exercise_id = e.id
        WHERE w.wdate BETWEEN ? AND ?
        GROUP BY u.id
        HAVING total_reps > 0
        ORDER BY total_reps DESC, username ASC
        """,
        (start_d.isoformat(), end_d.isoformat()),
    )
    return rows

