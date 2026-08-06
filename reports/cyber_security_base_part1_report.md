# GymBro Security Flaws Report

LINK: https://github.com/KirinPoersti/GymBro

This project uses the OWASP Top 10 2021 list exclusively. The application and its five vulnerabilities are intended only for local course demonstrations. Do not deploy it publicly or use real credentials.

Installation instructions:

Install Git, Python 3.10 or newer, `pip`, and the SQLite command-line tool before continuing.

Windows PowerShell:

```powershell
git clone https://github.com/KirinPoersti/GymBro.git
cd GymBro
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
sqlite3 database.db ".read schema.sql"
python app.py
```

Linux (Ubuntu/Debian): first install the prerequisites with `sudo apt update && sudo apt install git python3 python3-venv python3-pip sqlite3`, then run:

```bash
git clone https://github.com/KirinPoersti/GymBro.git
cd GymBro
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
sqlite3 database.db < schema.sql
python app.py
```

macOS: install the prerequisites using their official installers or Homebrew with `brew install git python sqlite`, then run:

```bash
git clone https://github.com/KirinPoersti/GymBro.git
cd GymBro
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
sqlite3 database.db < schema.sql
python app.py
```

On every platform, open http://127.0.0.1:5000 in a browser. The app is a workout and meal logging service with accounts, private profile data, personal workout records, meal tracking, and a public meal-plan forum. Because the app stores personal data and credentials, the security flaws below matter even though this is a small course project. The code already contains commented secure fixes beside the vulnerable examples, so each flaw links both to the problem and to the intended repair.

FLAW 1:

Exact source link pinpointing flaw 1: https://github.com/KirinPoersti/GymBro/blob/main/blueprints/plans_forum.py#L99-L109 and https://github.com/KirinPoersti/GymBro/blob/main/blueprints/plans_forum.py#L120-L130

This is an OWASP A01 Broken Access Control problem. In the meal-plan forum, the edit and delete routes load a post by numeric id and only check whether the visitor is logged in. They do not check whether the logged-in user owns that post. As a result, one authenticated user can change the URL from, for example, `/plans-forum/2/edit` to `/plans-forum/1/edit` and potentially edit another user's plan. The delete route has the same issue. The UI may hide edit and delete buttons for posts not owned by the current user, but hiding buttons is not authorization. The server must enforce the rule because requests can be sent manually.

How to fix it: re-enable the commented ownership checks at lines 108-109 and 129-130. After `get_post(pid)` succeeds, compare `post["user_id"]` with `session.get("user_id")`; if they differ, return `abort(403)`. A stronger version would also push ownership into the database layer, for example by using an update/delete query with both `id` and `user_id` in the `WHERE` clause. `screenshots/flaw-1-before-1.png` shows the attacker logged in, `screenshots/flaw-1-before-2.png` shows that user opening another user's edit form, and `screenshots/flaw-1-after-1.png` shows the repaired route returning 403.

FLAW 2:

Exact source link pinpointing flaw 2: https://github.com/KirinPoersti/GymBro/blob/main/services/users.py#L16-L25, https://github.com/KirinPoersti/GymBro/blob/main/services/users.py#L93-L99, and https://github.com/KirinPoersti/GymBro/blob/main/services/users.py#L102-L108

This is an OWASP A02 Cryptographic Failures problem. The database column is named `password_hash`, but `create_user` saves the user's raw password directly into it. `check_password` then compares the submitted password to the stored value with `==`, and `set_password` stores new passwords in plaintext as well. If the database file is leaked, copied from a developer machine, or exposed through another bug, every user's password is immediately readable. Because many people reuse passwords, this can also endanger accounts outside GymBro.

How to fix it: use Werkzeug's password helpers that are already shown as commented code. First, uncomment the import at https://github.com/KirinPoersti/GymBro/blob/main/services/users.py#L4. Then replace the plaintext assignment in registration with `generate_password_hash(password_plain)` at line 21, replace the direct comparison with `check_password_hash(...)` at line 99, and hash password changes at line 107. Existing plaintext rows should be migrated by forcing affected users to reset their passwords, because plaintext cannot safely be converted to the original intended secret once accounts are already in use. `screenshots/flaw-2-before-1.png` shows readable database values and `screenshots/flaw-2-after-1.png` shows the same demo accounts stored as scrypt hashes.

FLAW 3:

Exact source link pinpointing flaw 3: https://github.com/KirinPoersti/GymBro/blob/main/services/plans_forum.py#L149-L169

This is an OWASP A03 Injection problem. The function `search_posts_unsafe` builds an SQL query with an f-string and inserts the user's search term directly into the `LIKE` expressions. The route using it is `/api/plans-forum/search?q=...`, so the attacker controls `term`. A malicious value can close or modify the intended string pattern and change the logic of the query. Even when the practical impact is only reading public forum search results, the pattern is dangerous because the same habit in a more sensitive query could expose private rows or damage data.

How to fix it: use parameterized SQL exactly as shown in the commented secure block at lines 160-168. Build `like = f"%{term}%"`, keep the SQL text static, and pass `(like, like)` as parameters to `db.query`. The database driver will then treat the search text as data instead of executable SQL. This preserves the same search feature while removing the injection path. `screenshots/flaw-3-before-1.png` shows a normal zero-result search, `screenshots/flaw-3-before-2.png` shows the injected term returning both plans, and `screenshots/flaw-3-after-1.png` shows the same term treated as data and returning zero results.

FLAW 4:

Exact source link pinpointing flaw 4: https://github.com/KirinPoersti/GymBro/blob/main/app.py#L48-L53 and https://github.com/KirinPoersti/GymBro/blob/main/app.py#L64-L68

This is an OWASP A05 Security Misconfiguration problem. The application includes a public `/debug/crash` route that intentionally raises an exception, and the main entry point runs Flask with `debug=True`. In a local classroom demo, this is useful for showing stack traces, but in a deployed application it reveals internal paths, framework details, route structure, and sometimes sensitive values. Debug behavior also encourages relying on development defaults instead of a production configuration.

How to fix it: remove the public crash route or replace it with the commented `abort(404)` at line 52. Also replace `app.run(debug=True)` with the commented `app.run(debug=False)` at line 68 for any non-local run. A cleaner production setup would read debug mode from an environment variable that defaults to false, keep test-only routes behind a separate development flag, and use a real WSGI server. `screenshots/flaw-4-before-1.png` shows the exposed debugger response and `screenshots/flaw-4-after-1.png` shows the repaired route returning 404.

FLAW 5:

Exact source link pinpointing flaw 5: https://github.com/KirinPoersti/GymBro/blob/main/blueprints/settings.py#L110-L129

This is an OWASP A07 Identification and Authentication Failures problem. The password-change form asks for `current_password`, but the route does not verify it. The code assigns the submitted current password to `_ = curr` and then immediately calls `users_svc.set_password(uid, new)`. That means anyone with access to an already logged-in browser session can change the account password without knowing the existing password. This is especially risky on shared computers or when a session cookie is stolen.

How to fix it: re-enable the commented check at lines 124-126. The route should call `users_svc.check_password(uid, curr)` and reject the request with a flash message if the current password is wrong. This fix works best after flaw 2 is repaired, because `check_password` should verify a password hash rather than compare plaintext. It would also be reasonable to require a minimum password length and to expire other sessions after a password change, but the essential fix is to authenticate the sensitive action before changing credentials. `screenshots/flaw-5-before-1.png` shows a deliberately wrong current password, `screenshots/flaw-5-before-2.png` shows the vulnerable success message, and `screenshots/flaw-5-after-1.png` shows the repaired rejection.
