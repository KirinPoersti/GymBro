from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import db
from datetime import date, timedelta
import calendar

app = Flask(__name__)
app.secret_key = "change-me-in-production"  # put in .env later

@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

def require_auth():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return None

@app.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

def get_or_create_workout(uid, d):
    w = db.query_one("SELECT * FROM workouts WHERE user_id=? AND wdate=?", (uid, d))
    if not w:
        db.execute("INSERT INTO workouts (user_id, wdate) VALUES (?, ?)", (uid, d))
        w = db.query_one("SELECT * FROM workouts WHERE user_id=? AND wdate=?", (uid, d))
    return w

# ---------- Register ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm  = request.form["confirm"]

        if not email or not username or not password:
            flash("All fields are required.")
            return redirect(url_for("register"))
        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        if db.query_one("SELECT id FROM users WHERE email = ? OR username = ?", (email, username)):
            flash("Email or username already in use.")
            return redirect(url_for("register"))

        db.execute(
            "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
            (email, username, generate_password_hash(password))
        )
        flash("Account created. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------- Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = db.query_one("SELECT * FROM users WHERE username = ?", (username,))
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            flash("Signed in!")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.clear()
    flash("Signed out.")
    return redirect(url_for("home"))

def login_required():
    return "user_id" in session

def week_dates(offset_weeks=0):
    """Return a list of 7 date objects for the week (Mon–Sun), shifted by offset."""
    today = date.today()
    monday = today - timedelta(days=today.isoweekday() - 1) + timedelta(weeks=offset_weeks)
    return [monday + timedelta(days=i) for i in range(7)]

# ---------- Main Dashboard ----------
@app.route("/day/<d>")
def day_view(d):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    try:
        y, m, dd = map(int, d.split("-"))
        _ = date(y, m, dd)  # validate
    except Exception:
        abort(404)
    return render_template("day.html", d=d)

def month_grid(year:int, month:int):
    """42 dates (6 rows * 7 cols) starting on Monday for the given month."""
    cal = calendar.Calendar(firstweekday=0)  # 0=Monday
    days = list(cal.itermonthdates(year, month))
    # ensure exactly 42 cells
    if len(days) < 42:
      days += [days[-1] + timedelta(days=i+1) for i in range(42 - len(days))]
    return days[:42]

@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    today = date.today()
    y = int(request.args.get("y", today.year))
    m = int(request.args.get("m", today.month))

    grid = month_grid(y, m)

    # prev/next month
    if m == 1:  prev_y, prev_m = y-1, 12
    else:       prev_y, prev_m = y, m-1
    if m == 12: next_y, next_m = y+1, 1
    else:       next_y, next_m = y, m+1

    return render_template(
        "dashboard.html",
        grid=grid, year=y, month=m,
        prev_y=prev_y, prev_m=prev_m,
        next_y=next_y, next_m=next_m,
        today=today
    )

# -------- Profile (height/weight/age) --------
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if (r := require_auth()): return r

    uid = session["user_id"]

    if request.method == "POST":
        # fetch current values first
        current = db.query_one(
            "SELECT height_cm, weight_kg, age FROM users WHERE id = ?",
            (uid,)
        )

        def keep_or_cast(field, caster):
            raw = request.form.get(field, "").strip()
            if raw == "":                      # nothing typed → keep old value
                return current[field]
            try:
                raw = raw.replace(",", ".")    # allow 70,5 etc.
                return caster(raw)
            except Exception:
                # invalid input → also keep old value
                return current[field]

        h = keep_or_cast("height_cm", int)
        w = keep_or_cast("weight_kg", float)
        a = keep_or_cast("age", int)

        db.execute(
            "UPDATE users SET height_cm = ?, weight_kg = ?, age = ? WHERE id = ?",
            (h, w, a, uid)
        )
        flash("Profile updated.")
        return redirect(url_for("profile"))

    user = db.query_one(
        "SELECT username, height_cm, weight_kg, age FROM users WHERE id = ?",
        (uid,)
    )
    return render_template("profile.html", user=user)


# -------- Settings menu --------
@app.route("/settings")
def settings():
    if (r := require_auth()): return r
    return render_template("settings.html")

# -------- Change username --------
@app.route("/settings/username", methods=["GET", "POST"])
def settings_username():
    if (r := require_auth()): return r
    uid = session["user_id"]

    if request.method == "POST":
        new_name = request.form["new_username"].strip()
        if not new_name:
            flash("Username cannot be empty.")
            return redirect(url_for("settings_username"))
        # ensure unique
        exists = db.query_one("SELECT id FROM users WHERE username = ? AND id != ?", (new_name, uid))
        if exists:
            flash("Username already taken.")
            return redirect(url_for("settings_username"))
        db.execute("UPDATE users SET username = ? WHERE id = ?", (new_name, uid))
        session["username"] = new_name
        flash("Username updated.")
        return redirect(url_for("settings"))

    current = db.query_one("SELECT username FROM users WHERE id = ?", (uid,))
    return render_template("settings_username.html", current=current["username"])

# -------- Change password --------
@app.route("/settings/password", methods=["GET","POST"])
def settings_password():
    if (r := require_auth()): return r
    uid = session["user_id"]

    if request.method == "POST":
        curr = request.form["current_password"]
        new  = request.form["new_password"]
        conf = request.form["confirm_password"]
        if new != conf:
            flash("New passwords do not match.")
            return redirect(url_for("settings_password"))
        row = db.query_one("SELECT password_hash FROM users WHERE id = ?", (uid,))
        if not row or not check_password_hash(row["password_hash"], curr):
            flash("Current password is incorrect.")
            return redirect(url_for("settings_password"))
        db.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                   (generate_password_hash(new), uid))
        flash("Password changed.")
        return redirect(url_for("settings"))
    return render_template("settings_password.html")

# -------- Language --------
@app.route("/settings/language", methods=["GET","POST"])
def settings_language():
    if (r := require_auth()): return r
    uid = session["user_id"]
    if request.method == "POST":
        lang = request.form.get("language","en")
        db.execute("UPDATE users SET language = ? WHERE id = ?", (lang, uid))
        flash("Language saved.")
        return redirect(url_for("settings"))
    current = db.query_one("SELECT language FROM users WHERE id = ?", (uid,))
    return render_template("settings_language.html", current=current["language"])

# -------- Delete account --------
@app.route("/settings/delete", methods=["POST"])
def settings_delete():
    if (r := require_auth()): return r
    uid = session["user_id"]
    # TODO: also delete dependent data (plans/exercises/meals) when those exist
    db.execute("DELETE FROM users WHERE id = ?", (uid,))
    session.clear()
    flash("Account deleted.")
    return redirect(url_for("register"))

def get_or_create_workout(uid, d):
    w = db.query_one("SELECT * FROM workouts WHERE user_id=? AND wdate=?", (uid, d))
    if not w:
        db.execute("INSERT INTO workouts (user_id, wdate) VALUES (?, ?)", (uid, d))
        w = db.query_one("SELECT * FROM workouts WHERE user_id=? AND wdate=?", (uid, d))
    return w

# -------- Training session --------
@app.route("/day/<d>/training", methods=["GET", "POST"])
def training(d):
    if "user_id" not in session:
        return redirect(url_for("login"))
    uid = session["user_id"]

    # validate date
    try:
        y, m, dd = (int(x) for x in d.split("-"))
        _ = date(y, m, dd)
    except Exception:
        abort(404)

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        exercises = data.get("exercises", [])

        w = get_or_create_workout(uid, d)

        # wipe & replace for v1
        db.execute("DELETE FROM sets WHERE exercise_id IN (SELECT id FROM exercises WHERE workout_id=?)", (w["id"],))
        db.execute("DELETE FROM exercises WHERE workout_id=?", (w["id"],))

        for idx, ex in enumerate(exercises):
            name = (ex.get("name") or "").strip()
            if not name and not ex.get("sets"):  # skip empty rows
                continue

            db.execute("INSERT INTO exercises (workout_id, name, ord) VALUES (?, ?, ?)",
                       (w["id"], name or f"Exercise {idx+1}", idx))
            ex_id = db.query_one("SELECT id FROM exercises WHERE workout_id=? AND ord=?",
                                 (w["id"], idx))["id"]

            for s_idx, s in enumerate(ex.get("sets", []), start=1):
                reps_raw = s.get("reps")
                weight_raw = s.get("weight")

                reps = int(reps_raw) if reps_raw not in (None, "") else None
                weight = (float(str(weight_raw).replace(",", ".")) 
                          if weight_raw not in (None, "") else None)

                db.execute("INSERT INTO sets (exercise_id, set_no, reps, weight) VALUES (?, ?, ?, ?)",
                           (ex_id, s_idx, reps, weight))

        if request.is_json:
            return jsonify({"ok": True})
        return redirect(url_for("training", d=d), code=303)

    # GET
    w = db.query_one("SELECT * FROM workouts WHERE user_id=? AND wdate=?", (uid, d))
    exercises_payload = []
    if w:
        ex_rows = db.query("SELECT * FROM exercises WHERE workout_id=? ORDER BY ord", (w["id"],))
        for e in ex_rows:
            sets_rows = db.query("SELECT * FROM sets WHERE exercise_id=? ORDER BY set_no", (e["id"],))
            exercises_payload.append({
                "name": e["name"] or "",
                "sets": [{"reps": (s["reps"] if s["reps"] is not None else ""),
                          "weight": (s["weight"] if s["weight"] is not None else "")}
                         for s in sets_rows]
            })

    return render_template("training.html", d=d, exercises=exercises_payload)
# -------- Meal --------
@app.route("/day/<d>/meals", methods=["GET", "POST"])
def meals_view(d):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    uid = session["user_id"]

    # validate date (YYYY-MM-DD)
    from datetime import date as _d
    try:
        y, m, dd = map(int, d.split("-"))
        _ = _d(y, m, dd)
    except Exception:
        abort(404)

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        meals = data.get("meals", [])

        # ensure a day row exists (or similar to workouts)
        day = db.query_one("SELECT id FROM meal_days WHERE user_id=? AND d=?", (uid, d))
        if not day:
            db.execute("INSERT INTO meal_days (user_id, d) VALUES (?, ?)", (uid, d))
            day = db.query_one("SELECT id FROM meal_days WHERE user_id=? AND d=?", (uid, d))

        # wipe + replace
        db.execute("DELETE FROM meal_items WHERE meal_id IN (SELECT id FROM meals WHERE day_id=?)", (day["id"],))
        db.execute("DELETE FROM meals WHERE day_id=?", (day["id"],))

        for i, meal in enumerate(meals):
            name = (meal.get("name") or "").strip()
            db.execute("INSERT INTO meals (day_id, name, ord) VALUES (?, ?, ?)", (day["id"], name, i))
            meal_id = db.query_one("SELECT id FROM meals WHERE day_id=? AND ord=?", (day["id"], i))["id"]
            for it in meal.get("items", []):
                p = float(it.get("protein") or 0)
                c = float(it.get("carbs") or 0)
                k = int(float(it.get("calories") or 0))
                db.execute("INSERT INTO meal_items (meal_id, protein, carbs, calories) VALUES (?,?,?,?)",
                           (meal_id, p, c, k))
        return jsonify({"ok": True})

    # GET: load
    day = db.query_one("SELECT id FROM meal_days WHERE user_id=? AND d=?", (uid, d))
    meals = []
    if day:
        for m in db.query("SELECT id, name FROM meals WHERE day_id=? ORDER BY ord", (day["id"],)):
            items = db.query("SELECT protein, carbs, calories FROM meal_items WHERE meal_id=?", (m["id"],))
            meals.append({"name": m["name"], "items": items})
    return render_template("meals.html", d=d, meals=meals)

if __name__ == "__main__":
    app.run(debug=True)
