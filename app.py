from datetime import timedelta
from flask import Flask, abort
from flask_wtf import CSRFProtect
import config

from blueprints import register_blueprints
from blueprints.dashboard import dashboard as _bp_dashboard, day_view as _bp_day_view, home as _bp_home
from blueprints.settings import (
    profile as _bp_profile,
    settings as _bp_settings,
    settings_username as _bp_settings_username,
    settings_password as _bp_settings_password,
    settings_delete as _bp_settings_delete,
)
from blueprints.auth import login as _bp_login, register as _bp_register, logout as _bp_logout


app = Flask(__name__)
app.secret_key = config.secret_key
app.permanent_session_lifetime = timedelta(days=30)

app.config.update(
    WTF_CSRF_TIME_LIMIT=None,           
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False)        

csrf = CSRFProtect(app)


register_blueprints(app)

app.add_url_rule("/", endpoint="home", view_func=_bp_home, methods=["GET"])
app.add_url_rule("/dashboard", endpoint="dashboard", view_func=_bp_dashboard, methods=["GET"])
app.add_url_rule("/day/<d>", endpoint="day_view", view_func=_bp_day_view, methods=["GET"])

app.add_url_rule("/login", endpoint="login", view_func=_bp_login, methods=["GET", "POST"])
app.add_url_rule("/register", endpoint="register", view_func=_bp_register, methods=["GET", "POST"])
app.add_url_rule("/logout", endpoint="logout", view_func=_bp_logout, methods=["GET"])

app.add_url_rule("/profile", endpoint="profile", view_func=_bp_profile, methods=["GET", "POST"])
app.add_url_rule("/settings", endpoint="settings", view_func=_bp_settings, methods=["GET"])
app.add_url_rule("/settings/username", endpoint="settings_username", view_func=_bp_settings_username, methods=["GET", "POST"])
app.add_url_rule("/settings/password", endpoint="settings_password", view_func=_bp_settings_password, methods=["GET", "POST"])
app.add_url_rule("/settings/delete", endpoint="settings_delete", view_func=_bp_settings_delete, methods=["POST"])


@app.route("/debug/crash")
def debug_crash():
    # CSB OWASP 2021 A05 - Security Misconfiguration (VULNERABLE DEMO):
    # Public crash endpoint intentionally exposes debug stack traces when debug mode is enabled.
    # SECURE FIX:
    # abort(404)
    raise RuntimeError("Intentional Cyber Security Base demo crash")


@app.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

if __name__ == "__main__":
    # CSB OWASP 2021 A05 - Security Misconfiguration (VULNERABLE DEMO):
    # Debug mode must never be exposed outside a local teaching/demo environment.
    app.run(debug=True)
    # SECURE FIX:
    # app.run(debug=False)
