from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, abort

from services.auth import login_required
from services.plans_forum import list_posts, create_post, get_post, update_post, search_posts_unsafe, like_post


bp = Blueprint("plans_forum_bp", __name__)


def _items_from_form():
    names = request.form.getlist("item_name[]")
    weights = request.form.getlist("item_weight[]")
    proteins = request.form.getlist("item_protein[]")
    carbs = request.form.getlist("item_carbs[]")
    calories = request.form.getlist("item_calories[]")

    items = []
    max_len = max(len(names), len(weights), len(proteins), len(carbs), len(calories)) if any([names, weights, proteins, carbs, calories]) else 0
    for i in range(max_len):
        items.append({
            "name": ((names[i] if i < len(names) else "") or "").strip(),
            "weight": weights[i] if i < len(weights) else "",
            "protein": proteins[i] if i < len(proteins) else "",
            "carbs": carbs[i] if i < len(carbs) else "",
            "calories": calories[i] if i < len(calories) else "",
        })
    return items


@bp.route("/plans-forum", methods=["GET"], endpoint="plans_forum")
def plans_forum():
    uid = session.get("user_id")
    posts = list_posts(current_user_id=uid)
    return render_template("plans_forum.html", posts=posts)


@bp.route("/plans-forum/submit", methods=["GET"], endpoint="plans_submit")
@login_required
def plans_submit():
    items = [{"name": "", "weight": "", "protein": "", "carbs": "", "calories": ""}]
    return render_template("plans_submit.html", items=items, title="")


@bp.route("/plans-forum/submit", methods=["POST"], endpoint="plans_submit_post")
@login_required
def plans_submit_post():
    data = request.get_json(silent=True)
    if data is not None:
        title = (data.get("title") or "").strip()
        items = data.get("items", []) or []
        try:
            pid = create_post(session["user_id"], title, items)
        except ValueError:
            return (jsonify({"ok": False, "error": "invalid_user"}), 401)
        return jsonify({"ok": True, "id": pid, "url": url_for("dashboard") + f"?ok=1&pf_all=1#post-{pid}"})

    title = (request.form.get("title") or "").strip()
    items = _items_from_form()

    if "add_item" in request.form:
        items.append({"name": "", "weight": "", "protein": "", "carbs": "", "calories": ""})
        return render_template("plans_submit.html", items=items, title=title)
    if "remove_index" in request.form:
        try:
            ridx = int(request.form.get("remove_index"))
        except Exception:
            ridx = -1
        if 0 <= ridx < len(items):
            del items[ridx]
        if not items:
            items = [{"name": "", "weight": "", "protein": "", "carbs": "", "calories": ""}]
        return render_template("plans_submit.html", items=items, title=title)
    
    try:
        pid = create_post(session["user_id"], title, items)
    except ValueError:
        return (jsonify({"ok": False, "error": "invalid_user"}), 401)
    return redirect(url_for("dashboard") + f"?ok=1&pf_all=1#post-{pid}")


@bp.get("/api/plans-forum", endpoint="api_plans_forum")
def api_plans_forum():
    posts = list_posts(current_user_id=session.get("user_id"))
    return jsonify(posts)


@bp.get("/api/plans-forum/search", endpoint="api_plans_forum_search")
def api_plans_forum_search():
    q = request.args.get("q", "")
    return jsonify(search_posts_unsafe(q))


@bp.get("/plans-forum/search", endpoint="plans_forum_search")
def plans_forum_search():
    q = request.args.get("q", "")
    return render_template("plans_search.html", query=q, results=search_posts_unsafe(q))


@bp.route("/plans-forum/<int:pid>/edit", methods=["GET", "POST"], endpoint="plans_edit")
@login_required
def plans_edit(pid: int):
    post = get_post(pid)
    if not post:
        abort(404)
    # CSB OWASP 2021 A01 - Broken Access Control (VULNERABLE DEMO):
    # No ownership check is performed. A logged-in user can change the URL id and edit another user's plan.
    # SECURE FIX:
    # if post["user_id"] != session.get("user_id"):
    #     abort(403)

    if request.method == "GET":
        return render_template("plans_submit.html", items=post["items"], title=post["title"], edit_post=post)

    title = (request.form.get("title") or "").strip()
    items = _items_from_form()
    update_post(pid, title, items)
    return redirect(url_for("dashboard") + f"?ok=1&pf_all=1#post-{pid}")


@bp.route("/plans-forum/<int:pid>/delete", methods=["GET", "POST"], endpoint="plans_delete")
@login_required
def plans_delete(pid: int):
    post = get_post(pid)
    if not post:
        abort(404)
    # CSB OWASP 2021 A01 - Broken Access Control (VULNERABLE DEMO):
    # No ownership check is performed. A logged-in user can change the URL id and delete another user's plan.
    # SECURE FIX:
    # if post["user_id"] != session.get("user_id"):
    #     abort(403)

    if request.method == "GET" and not request.is_json:
        nxt = request.args.get("next") or url_for("plans_forum")
        return render_template("plans_delete_confirm.html", post=post, next_url=nxt)

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
    return redirect(url_for("plans_forum"))
