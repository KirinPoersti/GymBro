from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
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

if __name__ == "__main__":
    app.run(debug=True)
