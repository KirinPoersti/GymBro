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
    # Carb cycle info used in both GET and POST re-renders
    is_lowcarb, is_highcarb, suggested_carbs = carb_cycle_for_date(uid, cur_date)

    if request.method == "POST":
        # Support legacy JSON posts
        data = request.get_json(silent=True)
        if data is not None:
            meals_payload = data.get("meals", []) or []
            try:
                save_meals(uid, d, meals_payload)
            except ValueError:
                return (jsonify({"ok": False, "error": "invalid_user"}), 401)
            return jsonify({"ok": True})

        # No-JS form submission: reconstruct meals from form fields
        meal_names = request.form.getlist("meal_name[]")
        meals_state = []
        for i, mn in enumerate(meal_names):
            items = []
            inames = request.form.getlist(f"item_name_{i}[]")
            iwe = request.form.getlist(f"item_weight_{i}[]")
            ip = request.form.getlist(f"item_protein_{i}[]")
            ic = request.form.getlist(f"item_carbs_{i}[]")
            ik = request.form.getlist(f"item_calories_{i}[]")
            max_len = max(len(inames), len(iwe), len(ip), len(ic), len(ik)) if any([inames, iwe, ip, ic, ik]) else 0
            for j in range(max_len):
                items.append({
                    "name": (inames[j] if j < len(inames) else ""),
                    "weight": (iwe[j] if j < len(iwe) else ""),
                    "protein": (ip[j] if j < len(ip) else ""),
                    "carbs": (ic[j] if j < len(ic) else ""),
                    "calories": (ik[j] if j < len(ik) else ""),
                })
            meals_state.append({"name": mn, "items": items})

        # Handle UI actions
        if "add_meal" in request.form:
            meals_state.append({"name": "", "items": []})
            return render_template("meals.html", d=d, meals=meals_state, is_lowcarb=is_lowcarb, is_highcarb=is_highcarb, suggested_carbs=suggested_carbs)
        if "remove_meal" in request.form:
            try:
                rm = int(request.form.get("remove_meal"))
            except Exception:
                rm = -1
            if 0 <= rm < len(meals_state):
                del meals_state[rm]
            if not meals_state:
                meals_state = [{"name": "", "items": []}]
            return render_template("meals.html", d=d, meals=meals_state, is_lowcarb=is_lowcarb, is_highcarb=is_highcarb, suggested_carbs=suggested_carbs)
        if "add_item" in request.form:
            try:
                mi = int(request.form.get("add_item"))
            except Exception:
                mi = -1
            if 0 <= mi < len(meals_state):
                meals_state[mi]["items"].append({"name": "", "weight": "", "protein": "", "carbs": "", "calories": ""})
            return render_template("meals.html", d=d, meals=meals_state, is_lowcarb=is_lowcarb, is_highcarb=is_highcarb, suggested_carbs=suggested_carbs)
        if "remove_item" in request.form:
            raw = request.form.get("remove_item", "")
            try:
                i_s, j_s = raw.split("-", 1)
                i, j = int(i_s), int(j_s)
            except Exception:
                i, j = -1, -1
            if 0 <= i < len(meals_state) and 0 <= j < len(meals_state[i]["items"]):
                del meals_state[i]["items"][j]
            return render_template("meals.html", d=d, meals=meals_state, is_lowcarb=is_lowcarb, is_highcarb=is_highcarb, suggested_carbs=suggested_carbs)

        # Save
        try:
            save_meals(uid, d, meals_state)
        except ValueError:
            abort(401)
        return redirect(url_for("meals_bp.meals_view", d=d), code=303)

    meals = fetch_meals(uid, d)

    return render_template(
        "meals.html",
        d=d,
        meals=meals,
        is_lowcarb=is_lowcarb,
        is_highcarb=is_highcarb,
        suggested_carbs=suggested_carbs,
    )

