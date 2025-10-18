from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from services import users as users_svc


bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"], endpoint="register")
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm = request.form["confirm"]

        if not email or not username or not password:
            flash("All fields are required.")
            return redirect(url_for("register"))
        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        if users_svc.user_exists_email_or_username(email, username):
            flash("Email or username already in use.")
            return redirect(url_for("register"))

        users_svc.create_user(email, username, password)
        flash("Account created. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = users_svc.find_by_username(username)
        if user and users_svc.check_password(user["id"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            # Remember me: only make session permanent if checked
            session.permanent = bool(request.form.get("remember"))
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@bp.route("/logout", endpoint="logout")
def logout():
    session.clear()
    flash("Signed out.")
    return redirect(url_for("home"))


@bp.route("/logout/confirm", methods=["GET"], endpoint="logout_confirm")
def logout_confirm():
    next_url = url_for("settings")
    return render_template("logout_confirm.html", next_url=next_url)
