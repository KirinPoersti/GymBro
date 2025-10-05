from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, jsonify

from services.auth import login_required
from services.dates import month_grid
from services.workouts import workout_dates_for_range
from services.users import low_carb_cycle_info
from services.leaderboard import reps_leaderboard


bp = Blueprint("dashboard_bp", __name__)


@bp.route("/", endpoint="home")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@bp.route("/day/<d>", endpoint="day_view")
@login_required
def day_view(d: str):
    try:
        y, m, dd = map(int, d.split("-"))
        _ = date(y, m, dd)
    except Exception:
        abort(404)
    return render_template("day.html", d=d)


@bp.route("/dashboard", endpoint="dashboard")
@login_required
def dashboard():
    today = date.today()
    y = int(request.args.get("y", today.year))
    m = int(request.args.get("m", today.month))

    grid = month_grid(y, m)

    if m == 1:
        prev_y, prev_m = y - 1, 12
    else:
        prev_y, prev_m = y, m - 1
    if m == 12:
        next_y, next_m = y + 1, 1
    else:
        next_y, next_m = y, m + 1

    start_iso, end_iso = grid[0].isoformat(), grid[-1].isoformat()
    workout_dates = workout_dates_for_range(session["user_id"], start_iso, end_iso)

    start, _, _ = low_carb_cycle_info(session["user_id"])
    lowcarb_dates, highcarb_dates = set(), set()
    if start:
        for d in grid:
            delta = (d - start).days
            if delta >= 0:
                r = delta % 5
                if 0 <= r <= 3:
                    lowcarb_dates.add(d.isoformat())
                elif r == 4:
                    highcarb_dates.add(d.isoformat())

    return render_template(
        "dashboard.html",
        grid=grid,
        year=y,
        month=m,
        prev_y=prev_y,
        prev_m=prev_m,
        next_y=next_y,
        next_m=next_m,
        today=today,
        workout_dates=workout_dates,
        lowcarb_dates=lowcarb_dates,
        highcarb_dates=highcarb_dates,
    )


@bp.get("/api/leaderboard/reps", endpoint="api_leaderboard_reps")
@login_required
def api_leaderboard_reps():
    start = request.args.get("start")
    end = request.args.get("end")
    rows = reps_leaderboard(start, end)
    return jsonify(rows)
