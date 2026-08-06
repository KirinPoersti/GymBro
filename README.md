# 🏋🏿 GymBro

> **Security course demo:** This version intentionally contains five OWASP Top 10 2021 vulnerabilities. Run it only locally and never use real credentials or personal information.

GymBro is a lightweight **Flask** application for logging **workouts** and **meals**.  
Users can register, log in, maintain a **profile** (height, weight, age, activity level, sex, goal), and log **workouts** (exercises + sets) as well as **meals** (meals + food items + macros).  
From the profile, the app computes **TDEE**, protein needs, and a **carb cycling schedule** (4 low-carb days + 1 high-carb day).  
The calendar highlights training days with ⭕ and colors cells according to carb type.

---

## 🚀 Features (assignment check)

- [x] **User registration and login** (`/register`, `/login`; plaintext password handling is intentional for the A02 course demonstration, with the hashed fix commented beside it).
- [x] **Add, edit, delete entities**:
  - **Workouts**:
    - Add, edit, and delete workouts per day
    - Each workout contains exercises and sets
  - **Meals**: 
    - Add, edit, and delete meals per day
    - Each meal can contain multiple food items with weight, protein, carbs, and calories
    - Suggested carb intake shown for low/high-carb days  
  - **Profile**: updating values saves preferences and recalculates derived targets.
- [x] **View stored data**:
    - Calendar shows days, ⭕ for real workouts, carb cycle colors.
    - Day view with Training and Meals subpages.
    - Meals page lists saved meals/items.
    - Profile page displays computed calorie/macronutrient targets.
- [x] **Search functionality**: 
    - Exercise search with auto-suggestions
      - Type into the exercise input to get suggestions
      - Filter by **muscle group** (Glutes, Shoulders, Quads, Chest, Hamstrings, Triceps, Calves, Biceps, Abs, Back)  
- [x] **README with setup and testing instructions**.
- [x] **Leaderboard** that shows who's got the most reps for the week.
- [x] **Recipe sharing section** for people to share what they are eating

---

## Requirements

- Git
- Python 3.10+ and `pip`
- `sqlite3` command-line tool (for initializing the DB)

---

## 🛠 Installation

Install Git, Python 3.10 or newer, `pip`, and SQLite before continuing.

### Windows PowerShell

```powershell
git clone https://github.com/KirinPoersti/GymBro.git
cd GymBro
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
sqlite3 database.db ".read schema.sql"
python app.py
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip sqlite3
git clone https://github.com/KirinPoersti/GymBro.git
cd GymBro
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
sqlite3 database.db < schema.sql
python app.py
```

### macOS

Install the prerequisites using their official installers or Homebrew (`brew install git python sqlite`), then run:

```bash
git clone https://github.com/KirinPoersti/GymBro.git
cd GymBro
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
sqlite3 database.db < schema.sql
python app.py
```

Open http://127.0.0.1:5000 in a browser.

## 🔍 How to test?
To verify the goals of submissions, you can verify the following actions like this:

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
  - This can be tested by creating an account with your email and any wanted username + password
  <img width="466" height="519" alt="image" src="https://github.com/user-attachments/assets/f2b5a0bc-8e0e-4283-95aa-cdf96c28a795" />
  <img width="517" height="673" alt="image" src="https://github.com/user-attachments/assets/f609ddda-7e23-4353-91b8-d4b78ce281c0" />
  
  - Remember to check the box for "Remember me" while logging in
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan tietokohteita.
  - The user can add exercises entries and meals, and also meals to share with other users
  <img width="605" height="385" alt="image" src="https://github.com/user-attachments/assets/a14ab50c-84c9-4b7c-9e0b-d345bd66e2cf" />
- Käyttäjä näkee sovellukseen lisätyt tietokohteet.
  - Added entries and meals are visible in the app
- Käyttäjä pystyy etsimään tietokohteita hakusanalla tai muulla perusteella.
  - The user can search for entered entries through the calendar in the dashboard interface.
  <img width="1039" height="936" alt="image" src="https://github.com/user-attachments/assets/a61830c8-60e3-4ee4-9a53-f59c1032040c" />
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisämät tietokohteet.
  - Under this block, the leaderboard will list out users with the most amount of reps done during the week. The rep amount is being summed through user documentation.
  - To test this part, please create 2 users and also at least ONE training entry for one day.
    - By documentating your training session in the following way:
  <img width="1013" height="621" alt="image" src="https://github.com/user-attachments/assets/2330c816-aa6f-4aee-be0f-50d45e42c7a3" />
  <img width="1003" height="503" alt="image" src="https://github.com/user-attachments/assets/e75f16c4-dcdc-48dc-adb5-6ae6d858c208" />
     you will be able to revisit the documented training by clicking on the days with the ⭕ mark.
  <img width="937" height="337" alt="image" src="https://github.com/user-attachments/assets/33f2391b-773c-4ad1-ae91-69dbf324782e" />
 
- Käyttäjä pystyy valitsemaan tietokohteelle yhden tai useamman luokittelun. Mahdolliset luokat ovat tietokannassa.
  - While documentating your trainings, you're able to filter preset exercises with the dropbox
  <img width="680" height="412" alt="image" src="https://github.com/user-attachments/assets/ba049add-08f3-40e0-8b02-33d6edf4203c" />

- Käyttäjä pystyy lähettämän toisen käyttäjän tietokohteeseen liittyen jotain lisätietoa, joka tulee näkyviin sovelluksessa.
  - You can check diets posted by other users and give them a like. You can also submit your own to recieve feed back from the others
  <img width="1026" height="457" alt="image" src="https://github.com/user-attachments/assets/5cafabcb-8cc0-4fc6-bc70-f11b0020d85c" />
  - To test this part, please create 2 users and also at least 2 recipes to view the results


## 🪮 Linting

To run Pylint locally:
```
pip install -r requirements.txt
python -m pylint blueprints services app.py
```
Notes:
- The linter is configured via .pylintrc to ignore env/, static/, and 	emplates/.
- Some warnings are relaxed to fit this codebase (docstrings, function size, etc.).
- Max line length is 120.

### Lint report artifacts

- To generate and save lint reports under reports/:
```
python scripts/lint_report.py
```
- This writes:
  - reports/pylint-YYYYMMDD-HHMMSS.txt (human-readable)
  - reports/pylint-YYYYMMDD-HHMMSS.json (machine-parseable)
  - reports/pylint-latest.txt and 
  - reports/pylint-latest.json convenience copies
- The reports/ directory is kept in the repo with a .gitkeep; individual reports are git-ignored by default.
