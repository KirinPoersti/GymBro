from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, jsonify

from services.auth import login_required
from services.meals import save_meals, fetch_meals, carb_cycle_for_date


bp = Blueprint("meals_bp", __name__)


@bp.route("/day/<d>/meals", methods=["GET", "POST"], endpoint="meals_view")
@login_required
def meals_view(d: str):
    try:
        y, m, dd = map(int, d.split("-"))
        cur_date = date(y, m, dd)
    except Exception:
        abort(404)

    uid = session["user_id"]

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        meals_payload = data.get("meals", []) or []
        save_meals(uid, d, meals_payload)
        return jsonify({"ok": True})

    meals = fetch_meals(uid, d)
    is_lowcarb, is_highcarb, suggested_carbs = carb_cycle_for_date(uid, cur_date)

    return render_template(
        "meals.html",
        d=d,
        meals=meals,
        is_lowcarb=is_lowcarb,
        is_highcarb=is_highcarb,
        suggested_carbs=suggested_carbs,
    )

