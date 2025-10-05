from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import db
from datetime import date, timedelta, datetime
import calendar
from math import isfinite
import config
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key

@app.before_request
def _ensure_csrf():
    session.setdefault("csrf_token", secrets.token_hex(32))

# --- Exercise catalog for typeahead (flattened names) ---
EXERCISE_GROUPS = {
    "Glutes": [
        "Back Squat","Belt Squat","Box Pistol Squat","Bulgarian Split Squat, Barbell",
        "Bulgarian Split Squat, Dumbbells","Bulgarian Split Squat, Smith Machine",
        "Bulgarian Split Squat 1.5 Reps, Smith Machine","Deadlift","Deficit Deadlift",
        "Deficit Sumo Deadlift","Elevated Goblet Squat","Elevated Goblet Squat 1.5 Reps",
        "Forward Lunge with Barbell, One Leg at a Time","Front Squat","Glute Kickback",
        "Glute Kickback, Machine","Goblet Squat","Hack Squat","Hack Squat, 1.5 Reps",
        "Hip Abduction Machine","Hip Thrust","Hip Thrust Machine","Horizontal Leg Press",
        "Leg Press","Machine Step-Up","Paused Back Squat","Paused Bulgarian Split Squat, Smith Machine",
        "Paused Deadlift","Paused Sumo Deadlift","Pendulum Squat",
        "Reverse Lunge with Barbell, One Leg at a Time","Reverse Super Squat","Romanian Deadlift",
        "Romanian Sumo Deadlift","Safety Bar Squat","Single-Leg Hip Thrust",
        "Single-Leg Machine Hip Thrust","Single-Leg Romanian Deadlift",
        "Single-Leg Romanian Deadlift, Smith Machine","Single-Leg RDL, Kettlebell",
        "Smith Machine Squat","Step-Up","Sumo Deadlift","Trap Bar Deadlift",
        "Vertical Leg Press","Walking Lunges",
    ],
    "Shoulders": [
        "Arnold Press","Barbell Upright Row","Cable Cross Lateral Raise","Cable Lateral Raise",
        "Dumbbell Lateral Raise","Dumbbell Lateral Raise, 1.5 Reps","Dumbbell Lateral Raise, Paused",
        "Dumbbell Shoulder Press","Dumbbell Upright Row","Face Pull","Incline Dumbbell Lateral Raise",
        "Leaning Cable Lateral Raise","Leaning Lateral Raise","Machine Lateral Raise",
        "Machine Shoulder Press","Overhead Press","Rear Delt Machine",
        "Seated Dumbbell Lateral Raise","Seated Dumbbell Shoulder Press",
        "Single Arm Shoulder Press","Smith Machine Overhead Press","Standing Cable Row with Rope",
    ],
    "Quads": [
        "Back Squat","Belt Squat","Box Pistol Squat","Bulgarian Split Squat, Barbell",
        "Bulgarian Split Squat, Dumbbells","Bulgarian Split Squat, Smith Machine",
        "Bulgarian Split Squat 1.5 Reps, Smith Machine","Elevated Goblet Squat",
        "Elevated Goblet Squat, 1.5 Reps","Forward Lunge with Barbell, One Leg at a Time","Front Squat",
        "Goblet Squat","Hack Squat","Hack Squat, 1.5 Reps","Horizontal Leg Press","Leg Extension","Leg Press",
        "Machine Step-Up","Paused Back Squat","Paused Bulgarian Split Squat, Smith Machine","Pendulum Squat",
        "Reverse Lunge with Barbell, One Leg at a Time","Reverse Super Squat","Safety Bar Squat",
        "Single Leg Extension","Single Leg Press","Smith Machine Squat","Step-Up","Vertical Leg Press","Walking Lunges",
    ],
    "Chest": [
        "Barbell Bench Press","Barbell Bench Press 1.5 Reps","Barbell Bench Press with Pause",
        "Cable Chest Fly, Downward","Cable Chest Fly, Forward","Cable Chest Fly, Low to High",
        "Chest Fly Machine","Chest Fly Machine, 1.5 Reps","Chest Press Machine",
        "Close Grip Bench Press","Decline Push-Ups","Dips","Dumbbell Bench Press",
        "Dumbbell Bench Press, Paused","Incline Dumbbell Bench Press",
        "Incline Dumbbell Bench Press 1.5 Reps","Incline Dumbbell Fly","Incline Press Machine",
        "Kneeling Push-Up","Machine Assisted Dip","Push-Ups","Smith Machine Incline Bench Press",
    ],
    "Hamstrings": [
        "Back Extension","Bar Extension Machine","Deadlift","Deficit Deadlift","Deficit Sumo Deadlift",
        "Good Morning","Hip Adduction Machine","Lying Leg Curl","Romanian Deadlift",
        "Romanian Sumo Deadlift","Seated Leg Curl","Single-Leg Lying Leg Curl",
        "Single-Leg Romanian Deadlift","Single-Leg Romanian Deadlift, Smith Machine",
        "Single-Leg Romanian Deadlift, Trap Bar","Single-Leg RDL, Kettlebell",
        "Single-Leg Seated Leg Curl","Sumo Deadlift","Sumo Deadlift, Paused","Trap Bar Deadlift",
    ],
    "Triceps": [
        "Cable Tricep Kickback","Incline Tricep Extension, Dumbbell","JM Press",
        "Lying Barbell Tricep Extension","Lying Tricep Extension, Dumbbell","Machine Tricep Extension",
        "Overhead Barbell Tricep Extension","Overhead Cable Tricep Extension, Bar",
        "Overhead Cable Tricep Extension, Rope","Single Arm Tricep Extension, Dumbbell",
        "Triceps Pushdown, Rope","Triceps Pushdown, Straight Bar",
    ],
    "Calves": [
        "Horizontal Calf Press","Horizontal Calf Press Machine","Leg Press Calf Raise",
        "Seated Calf Raise","Smith Machine Calf Raise","Standing Calf Machine",
    ],
    "Biceps": [
        "21s (21 Shot)","Barbell Curl","Barbell Reverse Curl","Bayesian Cable Curl",
        "Cable Bicep Curl","Concentration Curl","Dumbbell Biceps Curl",
        "Dumbbell Preacher Curl","Hammer Curl","Incline Dumbbell Curl","Incline Hammer Curl",
        "Machine Biceps Curl","Preacher Curl",
    ],
    "Abs": [
        "Ab Rotations, Machine","Ab Wheel","Cable Crunch","Cable Oblique Twist",
        "Cable Oblique Twist, High-to-Low","Hanging Knee Raise","Hanging Leg Raise to 90 Degrees",
        "Hanging Leg Raises","Hanging Windshield Wipers","Incline Bench Sit-Up","Knee Raise, Supported",
        "Knee-Supported Ab Rotation, Machine","Leg Raises, Supported","Lying Leg Raises",
        "Pallof Press","Seated Machine Crunch","V Sit-Up","Weighted Ab Rotation",
    ],
    "Back": [
        "Band Assisted Chin-Up","Barbell Bent Over Row, Overhand Grip",
        "Barbell Bent Over Row, Smith Machine","Barbell Bent Over Row, Underhand Grip","Barbell Shrug",
        "Cable Lat Pullover","Cable Lat Pullover 1.5 Reps","Chest-Supported T-Bar Row","Chin-Ups","High Row",
        "Lat Pulldown, Neutral Grip","Lat Pulldown, Underhand Grip","Low Row","Machine Chest Supported Row",
        "Machine Chin-Up","Neutral Grip Chin-Up","Pull-Ups","Seal Row, Overhand Grip","Seal Row, Underhand Grip",
        "Seated Cable Row","Seated Cable Row, Overhand Grip","Single-Arm Chest-Supported Row, Machine",
        "Single-Arm Dumbbell Row","Single-Arm Lat Pulldown","Single-Arm Seated Cable Row","T-Bar Row",
    ],
}
EXERCISE_CATALOG = [name for group in EXERCISE_GROUPS.values() for name in group]

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

def _to_float(x, default=None):
    try:
        v = float(str(x))
        return v if isfinite(v) else default
    except Exception:
        return default

def _to_int(x, default=None):
    try:
        return int(float(str(x)))
    except Exception:
        return default
    
def _valid_iso_date(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False

def compute_calories_and_macros(weight_kg, height_cm, age, sex, activity_factor, goal, calorie_plan):
    if None in (weight_kg, height_cm, age) or sex not in ("male", "female") or activity_factor is None:
        return None, None, None, None
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if sex == "male" else -161)
    tdee = round(bmr * activity_factor)

    if calorie_plan == "cut":
        calories = round(tdee * 0.80)
    elif calorie_plan == "bulk":
        calories = round(tdee * 1.10)
    else:
        calories = tdee

    perkg = {"fat_loss": 1.0, "casual": 1.5, "muscle": 2.2}.get(goal, 1.5)
    protein_g = round(perkg * weight_kg)

    calories_after_protein = max(0, calories - protein_g * 4)
    carbs_low_g  = round((calories_after_protein * 0.30) / 4)
    carbs_high_g = round((calories_after_protein * 0.60) / 4)

    return calories, protein_g, carbs_low_g, carbs_high_g

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
        _ = date(y, m, dd) 
    except Exception:
        abort(404)
    return render_template("day.html", d=d)

def month_grid(year:int, month:int):
    """42 dates (6 rows * 7 cols) starting on Monday for the given month."""
    cal = calendar.Calendar(firstweekday=0)  
    days = list(cal.itermonthdates(year, month))
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

    if m == 1:  prev_y, prev_m = y-1, 12
    else:       prev_y, prev_m = y, m-1
    if m == 12: next_y, next_m = y+1, 1
    else:       next_y, next_m = y, m+1

    start_iso, end_iso = grid[0].isoformat(), grid[-1].isoformat()
    rows = db.query(
        """
        SELECT DISTINCT w.wdate
        FROM workouts w
        JOIN exercises e ON e.workout_id = w.id
        JOIN sets s      ON s.exercise_id = e.id
        WHERE w.user_id = ? AND w.wdate BETWEEN ? AND ?
        """,
        (session["user_id"], start_iso, end_iso)
    )
    workout_dates = {r["wdate"] for r in rows}

    uid = session["user_id"]
    user_row = db.query_one("SELECT low_carb_start FROM users WHERE id=?", (uid,))
    lowcarb_dates, highcarb_dates = set(), set()

    if user_row and user_row.get("low_carb_start"):
        try:
            start = datetime.strptime(user_row["low_carb_start"], "%Y-%m-%d").date()
            for d in grid:
                delta = (d - start).days
                if delta >= 0:
                    r = delta % 5
                    if 0 <= r <= 3:
                        lowcarb_dates.add(d.isoformat())   
                    elif r == 4:
                        highcarb_dates.add(d.isoformat())  
        except ValueError:
            pass  

    return render_template(
        "dashboard.html",
        grid=grid, year=y, month=m,
        prev_y=prev_y, prev_m=prev_m,
        next_y=next_y, next_m=next_m,
        today=today,
        workout_dates=workout_dates,
        lowcarb_dates=lowcarb_dates,
        highcarb_dates=highcarb_dates,
    )

# -------- Profile (height/weight/age) --------
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if (r := require_auth()): return r
    uid = session["user_id"]

    if request.method == "POST":
        current = db.query_one(
            "SELECT height_cm, weight_kg, age, sex, activity, goal, calorie_plan, low_carb_start "
            "FROM users WHERE id = ?",
            (uid,)
        ) or {}

        def keep_or_cast(field, caster, default_key=None):
            raw = request.form.get(field, "").strip()
            if raw == "":
                return current.get(default_key or field)
            try:
                raw = raw.replace(",", ".")
                return caster(raw)
            except Exception:
                return current.get(default_key or field)

        h = keep_or_cast("height_cm", int)
        w = keep_or_cast("weight_kg", float)
        a = keep_or_cast("age", int)

        sex = request.form.get("sex") or current.get("sex") or "male"
        activity = request.form.get("activity") or current.get("activity") or "1.55"
        goal = request.form.get("goal") or current.get("goal") or "casual"
        calorie_plan = request.form.get("calorie_plan") or current.get("calorie_plan") or "maintain"

        raw_start = (request.form.get("low_carb_start") or "").strip()
        if raw_start and _valid_iso_date(raw_start):
            low_carb_start = raw_start
        else:
            low_carb_start = current.get("low_carb_start")

        activity_f = _to_float(activity, None)

        calories, protein_g, carbs_low_g, carbs_high_g = compute_calories_and_macros(
            weight_kg=w, height_cm=h, age=a,
            sex=sex, activity_factor=activity_f,
            goal=goal, calorie_plan=calorie_plan
        )

        db.execute(
            """UPDATE users
               SET height_cm = ?, weight_kg = ?, age = ?,
                   sex = ?, activity = ?, goal = ?, calorie_plan = ?,
                   low_carb_start = ?,
                   calories_target = ?, protein_target_g = ?, carbs_low_g = ?, carbs_high_g = ?
               WHERE id = ?""",
            (h, w, a, sex, str(activity), goal, calorie_plan,
             low_carb_start,
             calories, protein_g, carbs_low_g, carbs_high_g, uid)
        )

        flash("Profile updated.")
        return redirect(url_for("profile"))

    user = db.query_one(
        "SELECT username, height_cm, weight_kg, age, sex, activity, goal, calorie_plan, "
        "low_carb_start, calories_target, protein_target_g, carbs_low_g, carbs_high_g "
        "FROM users WHERE id = ?",
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

# -------- Trainings --------
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

    # helper to load DB into payload (unchanged in spirit) 
    def load_exercises_from_db():
        w = db.query_one("SELECT * FROM workouts WHERE user_id=? AND wdate=?", (uid, d))
        payload = []
        if w:
            ex_rows = db.query("SELECT * FROM exercises WHERE workout_id=? ORDER BY ord", (w["id"],))
            for e in ex_rows:
                sets_rows = db.query("SELECT * FROM sets WHERE exercise_id=? ORDER BY set_no", (e["id"],))
                payload.append({
                    "name": e["name"] or "",
                    "group": e.get("group") or "All" if "group" in e else "All",
                    "sets": [{
                        "reps": (s["reps"] if s["reps"] is not None else None),
                        "weight": (s["weight"] if s["weight"] is not None else None)
                    } for s in sets_rows]
                })
        return payload

    if request.method == "POST":
        # CSRF
        token = request.form.get("csrf_token")
        if not token or token != session.get("csrf_token"):
            abort(400)

        action = request.form.get("action", "")
        ex_state = _parse_form_exercises(request.form)

        # add/remove UI actions (no DB writes yet)
        if action == "add_ex":
            ex_state.append({"name": "", "group": "All", "sets": []})
            return render_template("training.html", d=d, exercises=ex_state)

        if action.startswith("del_ex_"):
            try:
                i = int(action.split("_")[-1])
                if 0 <= i < len(ex_state):
                    ex_state.pop(i)
            except Exception:
                pass
            return render_template("training.html", d=d, exercises=ex_state)

        if action.startswith("add_set_"):
            try:
                i = int(action.split("_")[-1])
                ex_state[i]["sets"].append({"weight": None, "reps": None})
            except Exception:
                pass
            return render_template("training.html", d=d, exercises=ex_state)

        if action.startswith("del_set_"):
            try:
                _, _, ei, sj = action.split("_")
                ei, sj = int(ei), int(sj)
                if 0 <= ei < len(ex_state) and 0 <= sj < len(ex_state[ei]["sets"]):
                    ex_state[ei]["sets"].pop(sj)
            except Exception:
                pass
            return render_template("training.html", d=d, exercises=ex_state)

        if action == "save":
            cleaned = []
            for e in ex_state:
                nm = (e.get("name") or "").strip()
                sets = [s for s in (e.get("sets") or []) if (s.get("reps") is not None or s.get("weight") is not None)]
                if nm or sets:
                    cleaned.append({"name": nm, "sets": sets})

            w = db.query_one("SELECT * FROM workouts WHERE user_id=? AND wdate=?", (uid, d))
            if not w:
                db.execute("INSERT INTO workouts (user_id, wdate) VALUES (?, ?)", (uid, d))
                w = db.query_one("SELECT * FROM workouts WHERE user_id=? AND wdate=?", (uid, d))

            db.execute("DELETE FROM sets WHERE exercise_id IN (SELECT id FROM exercises WHERE workout_id=?)", (w["id"],))
            db.execute("DELETE FROM exercises WHERE workout_id=?", (w["id"],))

            inserted_exercises = 0
            for idx, ex in enumerate(cleaned):
                db.execute("INSERT INTO exercises (workout_id, name, ord) VALUES (?, ?, ?)", (w["id"], ex["name"] or f"Exercise {idx+1}", idx))
                ex_id = db.query_one("SELECT id FROM exercises WHERE workout_id=? AND ord=?", (w["id"], idx))["id"]
                inserted_exercises += 1
                for s_idx, s in enumerate(ex["sets"], start=1):
                    db.execute("INSERT INTO sets (exercise_id, set_no, reps, weight) VALUES (?, ?, ?, ?)",
                               (ex_id, s.get("reps"), s.get("weight")))
            if inserted_exercises == 0:
                db.execute("DELETE FROM workouts WHERE id=?", (w["id"],))

            flash("Training saved.")
            return redirect(url_for("training", d=d))

        return render_template("training.html", d=d, exercises=ex_state)

    exercises_payload = load_exercises_from_db()
    if not exercises_payload:
        exercises_payload = [{ "name": "", "group": "All", "sets": [] }]
    return render_template("training.html", d=d, exercises=exercises_payload)

# -------- Meal --------
def _carb_flags(uid: int, d_str: str):
    """Return (is_low, is_high, target_g) based on user profile + date.
       If neither low/high, compute a 'medium' target as avg(low, high)."""
    is_low = is_high = False
    target = None

    y, m, dd = map(int, d_str.split("-"))
    cur_date = date(y, m, dd)

    u = db.query_one(
        "SELECT low_carb_start, carbs_low_g, carbs_high_g FROM users WHERE id=?",
        (uid,)
    ) or {}

    start_raw = (u.get("low_carb_start") or "").strip()
    low = u.get("carbs_low_g")
    high = u.get("carbs_high_g")

    if start_raw:
        try:
            start = datetime.strptime(start_raw, "%Y-%m-%d").date()
            delta = (cur_date - start).days
            if delta >= 0:
                r = delta % 5         
                if 0 <= r <= 3:
                    is_low = True
                    target = low
                elif r == 4:
                    is_high = True
                    target = high
        except Exception:
            pass

    if not is_low and not is_high:
        if isinstance(low, (int, float)) and isinstance(high, (int, float)):
            target = round((low + high) / 2)
        else:
            target = low or high or None

    return is_low, is_high, target

def _parse_form_meals(form):
    """
    Turn flat form fields into:
      [{"name": str, "items":[{"name":..., "protein":..., "carbs":..., "calories":...}, ...]}, ...]
    Field names:
      meals-<i>-name
      meals-<i>-items-<j>-name / -protein / -carbs / -calories
    """
    meal_idxs = set()
    for k in form.keys():
        if k.startswith("meals-") and k.endswith("-name") and "-items-" not in k:
            try: meal_idxs.add(int(k.split("-")[1]))
            except: pass

    out = []
    for i in sorted(meal_idxs):
        name = (form.get(f"meals-{i}-name") or "").strip()

        item_idxs = set()
        pref = f"meals-{i}-items-"
        for k in form.keys():
            if k.startswith(pref) and k.endswith("-name"):
                try: item_idxs.add(int(k.split("-")[3]))
                except: pass

        items = []
        for j in sorted(item_idxs):
            nm = (form.get(f"meals-{i}-items-{j}-name") or "").strip()
            w =  (form.get(f"meals-{i}-items-{j}-weight") or "").strip()
            p  = (form.get(f"meals-{i}-items-{j}-protein") or "").strip()
            c  = (form.get(f"meals-{i}-items-{j}-carbs") or "").strip()
            k  = (form.get(f"meals-{i}-items-{j}-calories") or "").strip()
            items.append({"name": nm, "protein": p, "carbs": c, "calories": k})

        out.append({"name": name, "items": items})
    return out

@app.route("/day/<d>/meals", methods=["GET", "POST"])
def meals_view(d):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    uid = session["user_id"]

    is_lowcarb = False
    is_highcarb = False
    suggested_carbs = None

    def load_meals_from_db():
        day = db.query_one("SELECT id FROM meal_days WHERE user_id=? AND d=?", (uid, d))
        meals = []
        if day:
            cols = {c["name"] for c in db.query("PRAGMA table_info(meal_items)")}
            has_name = "name" in cols
            has_food = "food" in cols
            for m in db.query("SELECT id, name FROM meals WHERE day_id=? ORDER BY ord", (day["id"],)):
                if has_name and has_food:
                    q = "SELECT COALESCE(name, food) AS name, protein, carbs, calories FROM meal_items WHERE meal_id=?"
                elif has_name:
                    q = "SELECT name, protein, carbs, calories FROM meal_items WHERE meal_id=?"
                elif has_food:
                    q = "SELECT food AS name, protein, carbs, calories FROM meal_items WHERE meal_id=?"
                else:
                    q = "SELECT '' AS name, protein, carbs, calories FROM meal_items WHERE meal_id=?"
                items = db.query(q, (m["id"],))
                meals.append({"name": m["name"], "items": items})
        return meals

    if request.method == "POST":
        token = request.form.get("csrf_token")
        if not token or token != session.get("csrf_token"):
            abort(400)

        action = request.form.get("action", "")
        meals_state = _parse_form_meals(request.form)

        if action == "add_meal":
            is_lowcarb, is_highcarb, suggested_carbs = _carb_flags(uid, d)
            meals_state.append({"name": "", "items": []})
            return render_template("meals.html", d=d, meals=meals_state,
                                   is_lowcarb=is_lowcarb, is_highcarb=is_highcarb, suggested_carbs=suggested_carbs)

        if action.startswith("add_item_"):
            try:
                i = int(action.split("_")[-1])
                meals_state[i]["items"].append({"name": "", "protein": "", "carbs": "", "calories": ""})
            except: pass
            is_lowcarb, is_highcarb, suggested_carbs = _carb_flags(uid, d)
            return render_template("meals.html", d=d, meals=meals_state,
                                   is_lowcarb=is_lowcarb, is_highcarb=is_highcarb, suggested_carbs=suggested_carbs)

        if action.startswith("del_meal_"):
            try:
                i = int(action.split("_")[-1])
                if 0 <= i < len(meals_state): meals_state.pop(i)
            except: pass
            is_lowcarb, is_highcarb, suggested_carbs = _carb_flags(uid, d)
            return render_template("meals.html", d=d, meals=meals_state,
                                   is_lowcarb=is_lowcarb, is_highcarb=is_highcarb, suggested_carbs=suggested_carbs)

        if action.startswith("del_item_"):
            try:
                _, _, mi, ji = action.split("_")
                mi, ji = int(mi), int(ji)
                if 0 <= mi < len(meals_state) and 0 <= ji < len(meals_state[mi]["items"]):
                    meals_state[mi]["items"].pop(ji)
            except: pass
            is_lowcarb, is_highcarb, suggested_carbs = _carb_flags(uid, d)
            return render_template("meals.html", d=d, meals=meals_state,
                                   is_lowcarb=is_lowcarb, is_highcarb=is_highcarb, suggested_carbs=suggested_carbs)

        if action == "save":
            def _to_float(x):
                if x in ("", None): return None
                try: return float(str(x).replace(",", "."))
                except: return None
            def _to_int(x):
                f = _to_float(x)
                return int(f) if f is not None else None

            cleaned = []
            for m in meals_state:
                name = (m.get("name") or "").strip()
                items = []
                for it in (m.get("items") or []):
                    nm = (it.get("name") or "").strip()
                    p  = _to_float(it.get("protein")); c = _to_float(it.get("carbs")); k = _to_int(it.get("calories"))
                    if nm or p is not None or c is not None or k is not None:
                        items.append({"name": nm, "protein": p or 0.0, "carbs": c or 0.0, "calories": k or 0})
                if name or items:
                    cleaned.append({"name": name, "items": items})

            day = db.query_one("SELECT id FROM meal_days WHERE user_id=? AND d=?", (uid, d))
            if not day:
                db.execute("INSERT INTO meal_days (user_id, d) VALUES (?, ?)", (uid, d))
                day = db.query_one("SELECT id FROM meal_days WHERE user_id=? AND d=?", (uid, d))

            db.execute("DELETE FROM meal_items WHERE meal_id IN (SELECT id FROM meals WHERE day_id=?)", (day["id"],))
            db.execute("DELETE FROM meals WHERE day_id=?", (day["id"],))

            inserted = 0
            cols = {c["name"] for c in db.query("PRAGMA table_info(meal_items)")}
            has_name = "name" in cols
            has_food = "food" in cols

            for i, meal in enumerate(cleaned):
                db.execute("INSERT INTO meals (day_id, name, ord) VALUES (?, ?, ?)", (day["id"], meal["name"], i))
                meal_id = db.query_one("SELECT id FROM meals WHERE day_id=? AND ord=?", (day["id"], i))["id"]
                inserted += 1
                for it in meal["items"]:
                    if has_name:
                        db.execute(
                            "INSERT INTO meal_items (meal_id, name, protein, carbs, calories) VALUES (?,?,?,?,?)",
                            (meal_id, it["name"], it["protein"], it["carbs"], it["calories"])
                        )
                    elif has_food:
                        db.execute(
                            "INSERT INTO meal_items (meal_id, food, protein, carbs, calories) VALUES (?,?,?,?,?)",
                            (meal_id, it["name"] or "-", it["protein"], it["carbs"], it["calories"])
                        )
                    else:
                        db.execute(
                            "INSERT INTO meal_items (meal_id, protein, carbs, calories) VALUES (?,?,?,?)",
                            (meal_id, it["protein"], it["carbs"], it["calories"])
                        )

            if inserted == 0:
                db.execute("DELETE FROM meal_days WHERE id=?", (day["id"],))

            flash("Meals saved.")
            return redirect(url_for("meals_view", d=d))

        is_lowcarb, is_highcarb, suggested_carbs = _carb_flags(uid, d)
        return render_template("meals.html", d=d, meals=meals_state,
                               is_lowcarb=is_lowcarb, is_highcarb=is_highcarb, suggested_carbs=suggested_carbs)

    meals = load_meals_from_db() or [{"name": "", "items": []}]
    is_lowcarb, is_highcarb, suggested_carbs = _carb_flags(uid, d)
    return render_template("meals.html", d=d, meals=meals,
                           is_lowcarb=is_lowcarb, is_highcarb=is_highcarb, suggested_carbs=suggested_carbs)

if __name__ == "__main__":
    app.run(debug=True)
