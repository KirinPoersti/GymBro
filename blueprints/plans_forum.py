from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, abort

from services.auth import login_required
from services.plans_forum import list_posts, create_post, get_post, like_post


bp = Blueprint("plans_forum_bp", __name__)


@bp.route("/plans-forum", methods=["GET"], endpoint="plans_forum")
def plans_forum():
    uid = session.get("user_id")
    posts = list_posts(current_user_id=uid)
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
    items = data.get("items", []) or []
    try:
        pid = create_post(session["user_id"], title, items)
    except ValueError:
        return (jsonify({"ok": False, "error": "invalid_user"}), 401)
    return jsonify({"ok": True, "id": pid, "url": url_for("dashboard") + f"?ok=1#post-{pid}"})


@bp.get("/api/plans-forum", endpoint="api_plans_forum")
def api_plans_forum():
    posts = list_posts(current_user_id=session.get("user_id"))
    return jsonify(posts)


@bp.route("/plans-forum/<int:pid>/delete", methods=["GET", "POST"], endpoint="plans_delete")
@login_required
def plans_delete(pid: int):
    post = get_post(pid)
    if not post:
        abort(404)
    if post["user_id"] != session.get("user_id"):
        abort(403)

    # Confirmation page for GET
    if request.method == "GET" and not request.is_json:
        nxt = request.args.get("next") or url_for("plans_forum")
        return render_template("plans_delete_confirm.html", post=post, next_url=nxt)

    # Perform delete on POST
    import db
    db.execute("DELETE FROM meal_forum_posts WHERE id=?", (pid,))
    if request.is_json:
        return jsonify({"ok": True})
    nxt = request.form.get("next") or request.args.get("next")
    if nxt:
        return redirect(nxt)
    return redirect(url_for("plans_forum"))


@bp.route("/plans-forum/<int:pid>/like", methods=["POST"], endpoint="plans_like")
@login_required
def plans_like(pid: int):
    post = get_post(pid)
    if not post:
        abort(404)
    uid = session.get("user_id")
    res = like_post(pid, uid)
    if request.is_json:
        return jsonify({"ok": True, **res})
    nxt = request.form.get("next") or request.args.get("next")
    if nxt:
        return redirect(nxt)
    # Fallback to forum list
    return redirect(url_for("plans_forum"))
