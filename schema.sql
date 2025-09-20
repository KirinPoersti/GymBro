PRAGMA foreign_keys = ON;

-- Users
CREATE TABLE IF NOT EXISTS users (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  email             TEXT UNIQUE NOT NULL,
  username          TEXT UNIQUE NOT NULL,
  password_hash     TEXT NOT NULL,
  created_at        TEXT DEFAULT (datetime('now')),

  -- profile fields
  language          TEXT DEFAULT 'en',
  height_cm         REAL,
  weight_kg         REAL,
  age               INTEGER,
  sex               TEXT,                   -- 'male' | 'female'
  activity          TEXT,                   -- e.g. "1.55"
  goal              TEXT,                   -- 'fat_loss' | 'casual' | 'muscle'
  calorie_plan      TEXT,                   -- 'maintain' | 'cut' | 'bulk'
  protein_target_g  INTEGER,
  carbs_low_g       INTEGER,
  carbs_high_g      INTEGER,
  calories_target   INTEGER,
  low_carb_start    TEXT                    -- YYYY-MM-DD
);

-- Workouts (one per user per day)
CREATE TABLE IF NOT EXISTS workouts (
  id         INTEGER PRIMARY KEY,
  user_id    INTEGER NOT NULL,
  wdate      TEXT NOT NULL,                 -- YYYY-MM-DD
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(user_id, wdate),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Exercises within a workout
CREATE TABLE IF NOT EXISTS exercises (
  id          INTEGER PRIMARY KEY,
  workout_id  INTEGER NOT NULL,
  name        TEXT NOT NULL,
  ord         INTEGER DEFAULT 0,
  FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE
);

-- Sets for each exercise
CREATE TABLE IF NOT EXISTS sets (
  id          INTEGER PRIMARY KEY,
  exercise_id INTEGER NOT NULL,
  set_no      INTEGER NOT NULL,
  reps        INTEGER,
  weight      REAL,
  FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
);

-- Meal tracking: one row per user+date
CREATE TABLE IF NOT EXISTS meal_days (
  id      INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  d       TEXT NOT NULL,                   
  UNIQUE(user_id, d),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Meals on a day
CREATE TABLE IF NOT EXISTS meals (
  id     INTEGER PRIMARY KEY,
  day_id INTEGER NOT NULL,
  name   TEXT,
  ord    INTEGER DEFAULT 0,
  FOREIGN KEY (day_id) REFERENCES meal_days(id) ON DELETE CASCADE
);

-- Items inside a meal
CREATE TABLE IF NOT EXISTS meal_items (
  id       INTEGER PRIMARY KEY,
  meal_id  INTEGER NOT NULL,
  name     TEXT,
  protein  REAL,                            
  carbs    REAL,
  calories INTEGER,
  FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_workouts_user_date ON workouts(user_id, wdate);
CREATE INDEX IF NOT EXISTS idx_exercises_workout  ON exercises(workout_id, ord);
CREATE INDEX IF NOT EXISTS idx_sets_exercise      ON sets(exercise_id, set_no);
CREATE INDEX IF NOT EXISTS idx_meals_day          ON meals(day_id, ord);
CREATE INDEX IF NOT EXISTS idx_meal_items_meal    ON meal_items(meal_id);
