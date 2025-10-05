from datetime import datetime
from typing import Optional, Tuple

from werkzeug.security import generate_password_hash, check_password_hash

import db


def user_exists_email_or_username(email: str, username: str) -> bool:
    return db.query_one(
        "SELECT id FROM users WHERE email = ? OR username = ?",
        (email, username),
    ) is not None


def create_user(email: str, username: str, password_plain: str) -> int:
    pw_hash = generate_password_hash(password_plain)
    return db.execute(
        "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
        (email, username, pw_hash),
    )


def find_by_username(username: str):
    return db.query_one("SELECT * FROM users WHERE username = ?", (username,))


def get_profile(uid: int) -> dict:
    return db.query_one(
        "SELECT username, height_cm, weight_kg, age, sex, activity, goal, calorie_plan, "
        "low_carb_start, calories_target, protein_target_g, carbs_low_g, carbs_high_g "
        "FROM users WHERE id = ?",
        (uid,),
    ) or {}


def update_profile(
    uid: int,
    *,
    height_cm: Optional[int],
    weight_kg: Optional[float],
    age: Optional[int],
    sex: str,
    activity: str,
    goal: str,
    calorie_plan: str,
    low_carb_start: Optional[str],
    calories: Optional[int],
    protein_g: Optional[int],
    carbs_low_g: Optional[int],
    carbs_high_g: Optional[int],
):
    db.execute(
        """UPDATE users
           SET height_cm = ?, weight_kg = ?, age = ?,
               sex = ?, activity = ?, goal = ?, calorie_plan = ?,
               low_carb_start = ?,
               calories_target = ?, protein_target_g = ?, carbs_low_g = ?, carbs_high_g = ?
           WHERE id = ?""",
        (
            height_cm,
            weight_kg,
            age,
            sex,
            str(activity),
            goal,
            calorie_plan,
            low_carb_start,
            calories,
            protein_g,
            carbs_low_g,
            carbs_high_g,
            uid,
        ),
    )


def username_taken(username: str, exclude_uid: int) -> bool:
    return db.query_one(
        "SELECT id FROM users WHERE username = ? AND id != ?",
        (username, exclude_uid),
    ) is not None


def update_username(uid: int, new_username: str) -> None:
    db.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, uid))


def check_password(uid: int, plaintext: str) -> bool:
    row = db.query_one("SELECT password_hash FROM users WHERE id = ?", (uid,))
    return bool(row and check_password_hash(row["password_hash"], plaintext))


def set_password(uid: int, plaintext: str) -> None:
    pw_hash = generate_password_hash(plaintext)
    db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (pw_hash, uid))


def update_language(uid: int, lang: str) -> None:
    db.execute("UPDATE users SET language = ? WHERE id = ?", (lang, uid))


def delete_user(uid: int) -> None:
    db.execute("DELETE FROM users WHERE id = ?", (uid,))


def low_carb_cycle_info(uid: int):
    """Return (low_carb_start: Optional[date], carbs_low_g, carbs_high_g)."""
    row = db.query_one(
        "SELECT low_carb_start, carbs_low_g, carbs_high_g FROM users WHERE id=?",
        (uid,),
    ) or {}
    start_s = row.get("low_carb_start")
    start = None
    if start_s:
        try:
            start = datetime.strptime(start_s, "%Y-%m-%d").date()
        except Exception:
            start = None
    return start, row.get("carbs_low_g"), row.get("carbs_high_g")

