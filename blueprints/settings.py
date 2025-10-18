from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services.auth import login_required
from services import users as users_svc
from services.nutrition import compute_calories_and_macros, to_float
from services.dates import valid_iso_date


bp = Blueprint("settings_bp", __name__)


@bp.route("/profile", methods=["GET", "POST"], endpoint="profile")
@login_required
def profile():
    uid = session["user_id"]

    if request.method == "POST":
        current = users_svc.get_profile(uid)

        def keep_or_cast(field, caster, default_key=None):
            raw = request.form.get(field, "").strip()
            if raw == "":
                return current.get(default_key or field)
            try:
                raw = raw.replace(",", ".")
                return caster(raw)
            except (ValueError, TypeError):
                return current.get(default_key or field)

        h = keep_or_cast("height_cm", int)
        w = keep_or_cast("weight_kg", float)
        a = keep_or_cast("age", int)

        sex = request.form.get("sex") or current.get("sex") or "male"
        activity = request.form.get("activity") or current.get("activity") or "1.55"
        goal = request.form.get("goal") or current.get("goal") or "casual"
        calorie_plan = request.form.get("calorie_plan") or current.get("calorie_plan") or "maintain"

        raw_start = (request.form.get("low_carb_start") or "").strip()
        if raw_start and valid_iso_date(raw_start):
            low_carb_start = raw_start
        else:
            low_carb_start = current.get("low_carb_start")

        activity_f = to_float(activity, None)

        calories, protein_g, carbs_low_g, carbs_high_g = compute_calories_and_macros(
            weight_kg=w,
            height_cm=h,
            age=a,
            sex=sex,
            activity_factor=activity_f,
            goal=goal,
            calorie_plan=calorie_plan,
        )

        users_svc.update_profile(
            uid,
            height_cm=h,
            weight_kg=w,
            age=a,
            sex=sex,
            activity=activity,
            goal=goal,
            calorie_plan=calorie_plan,
            low_carb_start=low_carb_start,
            calories=calories,
            protein_g=protein_g,
            carbs_low_g=carbs_low_g,
            carbs_high_g=carbs_high_g,
        )

        flash("Profile updated.")
        return redirect(url_for("profile"))

    user = users_svc.get_profile(uid)
    return render_template("profile.html", user=user)


@bp.route("/settings", endpoint="settings")
@login_required
def settings():
    return render_template("settings.html")


@bp.route("/settings/username", methods=["GET", "POST"], endpoint="settings_username")
@login_required
def settings_username():
    uid = session["user_id"]

    if request.method == "POST":
        new_name = request.form["new_username"].strip()
        if not new_name:
            flash("Username cannot be empty.")
            return redirect(url_for("settings_username"))
        if users_svc.username_taken(new_name, uid):
            flash("Username already taken.")
            return redirect(url_for("settings_username"))
        users_svc.update_username(uid, new_name)
        session["username"] = new_name
        flash("Username updated.")
        return redirect(url_for("settings"))

    current = users_svc.get_profile(uid)
    return render_template("settings_username.html", current=current.get("username", ""))


@bp.route("/settings/password", methods=["GET", "POST"], endpoint="settings_password")
@login_required
def settings_password():
    uid = session["user_id"]

    if request.method == "POST":
        curr = request.form["current_password"]
        new = request.form["new_password"]
        conf = request.form["confirm_password"]
        if new != conf:
            flash("New passwords do not match.")
            return redirect(url_for("settings_password"))
        if not users_svc.check_password(uid, curr):
            flash("Current password is incorrect.")
            return redirect(url_for("settings_password"))
        users_svc.set_password(uid, new)
        flash("Password changed.")
        return redirect(url_for("settings"))

    return render_template("settings_password.html")

@bp.route("/settings/delete", methods=["POST"], endpoint="settings_delete")
@login_required
def settings_delete():
    uid = session["user_id"]
    users_svc.delete_user(uid)
    session.clear()
    flash("Account deleted.")
    return redirect(url_for("register"))


