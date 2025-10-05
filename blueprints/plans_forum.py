from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, abort

from services.auth import login_required
from services.plans_forum import list_posts, create_post, get_post


bp = Blueprint("plans_forum_bp", __name__)


@bp.route("/plans-forum", methods=["GET"], endpoint="plans_forum")
def plans_forum():
    posts = list_posts()
    return render_template("plans_forum.html", posts=posts)


@bp.route("/plans-forum/submit", methods=["GET"], endpoint="plans_submit")
@login_required
def plans_submit():
    return render_template("plans_submit.html")


@bp.route("/plans-forum/submit", methods=["POST"], endpoint="plans_submit_post")
@login_required
def plans_submit_post():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    # Only one plan worth of items allowed; the client will send a single list
    items = data.get("items", []) or []
    pid = create_post(session["user_id"], title, items)
    # Include ok=1 so the forum can show a success message
    return jsonify({"ok": True, "id": pid, "url": url_for("plans_forum_bp.plans_forum") + f"?ok=1#post-{pid}"})


@bp.get("/api/plans-forum", endpoint="api_plans_forum")
def api_plans_forum():
    # Lightweight feed for the dashboard widget
    posts = list_posts()
    return jsonify(posts)


@bp.route("/plans-forum/<int:pid>/delete", methods=["POST"], endpoint="plans_delete")
@login_required
def plans_delete(pid: int):
    post = get_post(pid)
    if not post:
        abort(404)
    if post["user_id"] != session.get("user_id"):
        abort(403)
    # Authorised: delete
    import db
    db.execute("DELETE FROM meal_forum_posts WHERE id=?", (pid,))
    if request.is_json:
        return jsonify({"ok": True})
    return redirect(url_for("plans_forum"))
