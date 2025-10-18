# 🏋🏿 GymBro

GymBro is a lightweight **Flask** application for logging **workouts** and **meals**.  
Users can register, log in, maintain a **profile** (height, weight, age, activity level, sex, goal), and log **workouts** (exercises + sets) as well as **meals** (meals + food items + macros).  
From the profile, the app computes **TDEE**, protein needs, and a **carb cycling schedule** (4 low-carb days + 1 high-carb day).  
The calendar highlights training days with 猸?and colors cells according to carb type.

---

## 🚀 Features (assignment check)

- [x] **User registration and login** (`/register`, `/login`, with password hashing).
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
    - Calendar shows days, 猸?for real workouts, carb cycle colors.
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

- Python 3.10+
- `sqlite3` command-line tool (for initializing the DB)
- Developed on Windows11

---

## 🛠 Installation

Download the code of the main branch
- and extract it

Install the `flask` library:

```
pip install flask
pip install -r requirements.txt
```

Create the database tables:

```
sqlite3 database.db < schema.sql
```

Run the application:

```
python -m flask run
```
Open in Browser:

```
http://127.0.0.1:5000
```

## 🔍 How to test?
To verify the goals of submissions, you can verify the following actions like this:

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
  - This can be tested by creating an account with your email and any wanted username + password
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan tietokohteita.
  - The user can add exercises entries and meals, and also meals to share with other users
- Käyttäjä näkee sovellukseen lisätyt tietokohteet.
  - Added entries and meals are visible in the app
- Käyttäjä pystyy etsimään tietokohteita hakusanalla tai muulla perusteella.
  - The user can search for entered entries through the calendar in the dashboard interface.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisämät tietokohteet.
  - Under this block, the leaderboard will list out users with the most amount of reps done during the week. The rep amount is being summed through user documentation.
  - To test this part, please create 2 users and also at least ONE training entry for one day.
    <img width="1069" height="509" alt="image" src="https://github.com/user-attachments/assets/36f33101-e0dd-4f1a-87fa-ece9554874d1" />
    - By documentating your training session in the following way:
    <img width="1003" height="503" alt="image" src="https://github.com/user-attachments/assets/e75f16c4-dcdc-48dc-adb5-6ae6d858c208" />
     you will be able to revisit the documented training by clicking on the days with the 猸曪笍 mark.
     <img width="937" height="337" alt="image" src="https://github.com/user-attachments/assets/33f2391b-773c-4ad1-ae91-69dbf324782e" />
 
- Käyttäjä pystyy valitsemaan tietokohteelle yhden tai useamman luokittelun. Mahdolliset luokat ovat tietokannassa.
  - While documentating your trainings, you're able to filter preset exercises with the dropbox
    <img width="680" height="412" alt="image" src="https://github.com/user-attachments/assets/ba049add-08f3-40e0-8b02-33d6edf4203c" />

- Käyttäjä pystyy lähettämän toisen käyttäjän tietokohteeseen liittyen jotain lisätietoa, joka tulee näkyviin sovelluksessa.
  - You can check diets posted by other users and give them a like. You can also submit your own to recieve feed back from the others
  - <img width="1026" height="457" alt="image" src="https://github.com/user-attachments/assets/5cafabcb-8cc0-4fc6-bc70-f11b0020d85c" />
  - To test this part, please create 2 users and also at least 2 recipes to view the results


## 🪮 Linting

To run Pylint locally:

`
pip install -r requirements.txt
python -m pylint blueprints services app.py
`

Notes:
- The linter is configured via .pylintrc to ignore env/, static/, and 	emplates/.
- Some warnings are relaxed to fit this codebase (docstrings, function size, etc.).
- Max line length is 120.

### Lint report artifacts

To generate and save lint reports under 
eports/:

`
python scripts/lint_report.py
`

This writes:
- 
eports/pylint-YYYYMMDD-HHMMSS.txt (human-readable)
- 
eports/pylint-YYYYMMDD-HHMMSS.json (machine-parseable)
- 
eports/pylint-latest.txt and 
eports/pylint-latest.json convenience copies

The 
eports/ directory is kept in the repo with a .gitkeep; individual reports are git-ignored by default.
