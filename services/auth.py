from functools import wraps
from flask import session, redirect, url_for, request, abort
import db


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        uid = session.get("user_id")
        if not uid:
            return redirect(url_for("login", next=request.path))
        row = db.query_one("SELECT id FROM users WHERE id=?", (uid,))
        if not row:
            session.clear()
            if request.is_json or request.headers.get("Accept", "").startswith("application/json"):
                abort(401)
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

