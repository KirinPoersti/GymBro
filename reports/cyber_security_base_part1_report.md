# GymBro Cyber Security Base Part I Report

Repository: https://github.com/KirinPoersti/GymBro

This demo intentionally implements five backend security flaws from OWASP Top 10 2021 only. Each vulnerable block is clearly marked in code with `CSB OWASP 2021`, and the secure fix is placed as commented-out code next to the flaw.

## Install And Run

```powershell
git clone https://github.com/KirinPoersti/GymBro.git
cd GymBro
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
sqlite3 database.db < schema.sql
python app.py
```

Open http://127.0.0.1:5000 in a browser.

## Flaw 1: A01 Broken Access Control

GitHub line links:

- Edit flaw and fix: https://github.com/KirinPoersti/GymBro/blob/main/blueprints/plans_forum.py#L93-L111
- Delete flaw and fix: https://github.com/KirinPoersti/GymBro/blob/main/blueprints/plans_forum.py#L114-L124

Description: A logged-in user can change the numeric `pid` in `/plans-forum/<pid>/edit` or `/plans-forum/<pid>/delete` and edit or delete another user's meal plan. The backend fetches the object but does not verify that `post["user_id"]` matches `session["user_id"]`.

Fix: Re-enable the commented ownership check and abort with `403` when the object belongs to another user.

Screenshots:

- Before: `screenshots/a01-before.png`
- After: `screenshots/a01-after.png`

## Flaw 2: A02 Cryptographic Failures

GitHub line links:

- Plaintext password storage: https://github.com/KirinPoersti/GymBro/blob/main/services/users.py#L16-L25
- Plaintext password comparison and update: https://github.com/KirinPoersti/GymBro/blob/main/services/users.py#L93-L108

Description: Registration and password changes store the raw password in the `password_hash` column, and login compares plaintext values directly. A database leak would expose usable passwords immediately.

Fix: Re-enable `generate_password_hash` when saving passwords and `check_password_hash` when checking submitted credentials.

Screenshots:

- Before: `screenshots/a02-before.png`
- After: `screenshots/a02-after.png`

## Flaw 3: A03 Injection

GitHub line links:

- Unsafe SQL search and fix: https://github.com/KirinPoersti/GymBro/blob/main/services/plans_forum.py#L149-L169

Description: `/api/plans-forum/search?q=...` sends user-controlled search text into an SQL string with f-string formatting. A crafted query can alter the SQL condition.

Fix: Use placeholders and pass the `LIKE` values as parameters.

Screenshots:

- Before: `screenshots/a03-before.png`
- After: `screenshots/a03-after.png`

## Flaw 4: A05 Security Misconfiguration

GitHub line links:

- Public crash route and fix: https://github.com/KirinPoersti/GymBro/blob/main/app.py#L48-L53
- Debug mode and fix: https://github.com/KirinPoersti/GymBro/blob/main/app.py#L64-L68

Description: The app exposes `/debug/crash`, which raises an exception, and runs Flask with `debug=True`. In a deployed environment this can reveal stack traces and internal details.

Fix: Remove or hide the crash route and run with debug disabled.

Screenshots:

- Before: `screenshots/a05-before.png`
- After: `screenshots/a05-after.png`

## Flaw 5: A07 Identification And Authentication Failures

GitHub line links:

- Password change flaw and fix: https://github.com/KirinPoersti/GymBro/blob/main/blueprints/settings.py#L110-L129

Description: The password-change form reads `current_password` but does not verify it before setting a new password. Anyone with an active session can change the account password without knowing the existing password.

Fix: Re-enable the commented `users_svc.check_password(uid, curr)` check and reject incorrect current passwords.

Screenshots:

- Before: `screenshots/a07-before.png`
- After: `screenshots/a07-after.png`

## Screenshot Index

The `screenshots/` folder contains one before and one after image for every flaw:

- `a01-before.png`, `a01-after.png`
- `a02-before.png`, `a02-after.png`
- `a03-before.png`, `a03-after.png`
- `a05-before.png`, `a05-after.png`
- `a07-before.png`, `a07-after.png`
