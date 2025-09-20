# GymBro

GymBro is a lightweight **Flask** application for logging **workouts** and **meals**.  
Users can register, log in, maintain a **profile** (height, weight, age, activity level, sex, goal), and log **workouts** (exercises + sets) as well as **meals** (meals + food items + macros).  
From the profile, the app computes **TDEE**, protein needs, and a **carb cycling schedule** (4 low-carb days + 1 high-carb day).  
The calendar highlights training days with ✓ and colors cells according to carb type.

---

## Features (assignment check)

- [x] **User registration and login** (`/register`, `/login`, with password hashing).
- [x] **Add, edit, delete entities**:
  - **Workouts**: add/edit (wipe & replace for v1). If all sets are removed, the workout row is deleted.
  - **Meals**: add/edit/delete. Saving with no meals/items deletes the meal-day entry.
  - **Profile**: updating values saves preferences and recalculates derived targets.
- [x] **View stored data**:
  - Calendar shows days, ✓ ticks for real workouts, carb cycle colors.
  - Day view with Training and Meals subpages.
  - Meals page lists saved meals/items.
  - Profile page displays computed calorie/macronutrient targets.
- [ ] **Search functionality**: not implemented yet (see “Search functionality” below).
- [x] **README with setup and testing instructions**.

⚠️ **Important repo hygiene:**  
Do **not** commit `database.db` to the repository. The database should be created locally from `schema.sql`.

---

## Requirements

- Python 3.10+
- `sqlite3` command-line tool (for initializing the DB)
- Works on Linux, macOS, Windows

---

## Installation and running

### 1. Clone repo & create virtual environment

**Linux/macOS**
```bash
git clone https://github.com/KirinPoersti/GymBro.git
cd GymBro
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # or: pip install flask werkzeug
