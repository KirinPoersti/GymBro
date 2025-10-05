from datetime import date as date_cls
from typing import List, Dict, Tuple

import db
from .users import low_carb_cycle_info


def _meal_items_schema() -> Tuple[bool, bool]:
    mi_cols = {c["name"] for c in db.query("PRAGMA table_info(meal_items)")}
    return ("name" in mi_cols), ("food" in mi_cols)


def save_meals(user_id: int, d: str, meals_payload: List[Dict]) -> None:
    day = db.query_one("SELECT id FROM meal_days WHERE user_id=? AND d=?", (user_id, d))
    if not day:
        db.execute("INSERT INTO meal_days (user_id, d) VALUES (?, ?)", (user_id, d))
        day = db.query_one("SELECT id FROM meal_days WHERE user_id=? AND d=?", (user_id, d))

    # clear old content for this day
    db.execute(
        "DELETE FROM meal_items WHERE meal_id IN (SELECT id FROM meals WHERE day_id=?)",
        (day["id"],),
    )
    db.execute("DELETE FROM meals WHERE day_id=?", (day["id"],))

    MI_HAS_NAME, MI_HAS_FOOD = _meal_items_schema()

    saved_meals = 0
    for i, meal in enumerate(meals_payload):
        meal_name = (meal.get("name") or "").strip()
        raw_items = meal.get("items", []) or []

        items_in = []
        for it in raw_items:
            nm = (it.get("name") or "").strip()
            p = _to_float_none(it.get("protein"))
            c = _to_float_none(it.get("carbs"))
            k = _to_int_none(it.get("calories"))
            if nm or p is not None or c is not None or k is not None:
                items_in.append({
                    "name": nm,
                    "protein": p or 0.0,
                    "carbs": c or 0.0,
                    "calories": k or 0,
                })

        if not meal_name and not items_in:
            continue

        db.execute(
            "INSERT INTO meals (day_id, name, ord) VALUES (?, ?, ?)",
            (day["id"], meal_name, i),
        )
        meal_id = db.query_one(
            "SELECT id FROM meals WHERE day_id=? AND ord=?",
            (day["id"], i),
        )["id"]
        saved_meals += 1

        for it in items_in:
            name_to_save = (it["name"] or "").strip()
            if MI_HAS_NAME:
                db.execute(
                    "INSERT INTO meal_items (meal_id, name, protein, carbs, calories) VALUES (?,?,?,?,?)",
                    (
                        meal_id,
                        name_to_save,
                        it["protein"],
                        it["carbs"],
                        it["calories"],
                    ),
                )
            elif MI_HAS_FOOD:
                if name_to_save == "":
                    name_to_save = "-"
                db.execute(
                    "INSERT INTO meal_items (meal_id, food, protein, carbs, calories) VALUES (?,?,?,?,?)",
                    (
                        meal_id,
                        name_to_save,
                        it["protein"],
                        it["carbs"],
                        it["calories"],
                    ),
                )
            else:
                db.execute(
                    "INSERT INTO meal_items (meal_id, protein, carbs, calories) VALUES (?,?,?,?)",
                    (
                        meal_id,
                        it["protein"],
                        it["carbs"],
                        it["calories"],
                    ),
                )

    if saved_meals == 0:
        db.execute("DELETE FROM meal_days WHERE id=?", (day["id"],))


def fetch_meals(user_id: int, d: str) -> List[Dict]:
    day = db.query_one("SELECT id FROM meal_days WHERE user_id=? AND d=?", (user_id, d))
    meals: List[Dict] = []
    if not day:
        return meals

    MI_HAS_NAME, MI_HAS_FOOD = _meal_items_schema()

    for mrow in db.query("SELECT id, name FROM meals WHERE day_id=? ORDER BY ord", (day["id"],)):
        if MI_HAS_NAME and MI_HAS_FOOD:
            q = (
                "SELECT COALESCE(name, food) AS name, protein, carbs, calories FROM meal_items WHERE meal_id=?"
            )
        elif MI_HAS_NAME:
            q = "SELECT name, protein, carbs, calories FROM meal_items WHERE meal_id=?"
        elif MI_HAS_FOOD:
            q = "SELECT food AS name, protein, carbs, calories FROM meal_items WHERE meal_id=?"
        else:
            q = "SELECT '' AS name, protein, carbs, calories FROM meal_items WHERE meal_id=?"
        items = db.query(q, (mrow["id"],))
        meals.append({"name": mrow["name"], "items": items})

    return meals


def carb_cycle_for_date(user_id: int, cur_date: date_cls):
    """Return (is_lowcarb, is_highcarb, suggested_carbs)."""
    start, low_g, high_g = low_carb_cycle_info(user_id)
    if not start:
        return False, False, None
    delta = (cur_date - start).days
    if delta < 0:
        return False, False, None
    r = delta % 5
    if 0 <= r <= 3:
        return True, False, low_g
    if r == 4:
        return False, True, high_g
    return False, False, None


def _to_float_none(x):
    if x in (None, ""):
        return None
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return None


def _to_int_none(x):
    f = _to_float_none(x)
    return int(f) if f is not None else None

