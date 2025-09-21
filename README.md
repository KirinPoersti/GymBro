# 🏋🏿 GymBro

GymBro is a lightweight **Flask** application for logging **workouts** and **meals**.  
Users can register, log in, maintain a **profile** (height, weight, age, activity level, sex, goal), and log **workouts** (exercises + sets) as well as **meals** (meals + food items + macros).  
From the profile, the app computes **TDEE**, protein needs, and a **carb cycling schedule** (4 low-carb days + 1 high-carb day).  
The calendar highlights training days with ✓ and colors cells according to carb type.

---

## 🚀 Features (assignment check)

- [x] **User registration and login** (`/register`, `/login`, with password hashing).
- [x] **Add, edit, delete entities**:
  - **Workouts**:
    - Add, edit, and delete workouts per day
    - Each workout contains exercises and sets
  - **Meals**: 
    - Add, edit, and delete meals per day
    - Each meal can contain multiple food items with protein, carbs, and calories
    - Suggested carb intake shown for low/high-carb days  
  - **Profile**: updating values saves preferences and recalculates derived targets.
- [x] **View stored data**:
    - Calendar shows days, ✓ ticks for real workouts, carb cycle colors.
    - Day view with Training and Meals subpages.
    - Meals page lists saved meals/items.
    - Profile page displays computed calorie/macronutrient targets.
- [x] **Search functionality**: 
    - Exercise search with auto-suggestions
      - Type into the exercise input to get suggestions
      - Filter by **muscle group** (Glutes, Shoulders, Quads, Chest, Hamstrings, Triceps, Calves, Biceps, Abs, Back)  
- [x] **README with setup and testing instructions**.
- [ ] ❗The logic part for language change isn't ready yet, what's shown is just a shell that does no changes to the UI

---

## Requirements

- Python 3.10+
- `sqlite3` command-line tool (for initializing the DB)
- Developed on Windows11

---

## 🛠 Installation

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

## Potential Future Development 
- Statistics dashboard
- Performance enhancement
- Multi Language support
- Weekly/monthly workout summaries
- Charts for calories, macros, and weight changes
- Preloaded exercises with descriptions and images
