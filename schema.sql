PRAGMA foreign_keys = ON;

-- Users table with profile fields
CREATE TABLE IF NOT EXISTS users (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  email           TEXT UNIQUE NOT NULL,
  username        TEXT UNIQUE NOT NULL,
  password_hash   TEXT NOT NULL,
  created_at      TEXT DEFAULT (datetime('now')),

  -- profile fields
  language        TEXT DEFAULT 'en',
  height_cm       REAL,
  weight_kg       REAL,
  age             INTEGER,
  sex             TEXT,      -- 'male' | 'female'
  activity        TEXT,      -- activity multiplier as string (e.g. "1.55")
  goal            TEXT,      -- 'fat_loss' | 'casual' | 'muscle'
  calorie_plan    TEXT,      -- 'maintain' | 'cut' | 'bulk'
  protein_target_g INTEGER,
  carbs_low_g      INTEGER,
  carbs_high_g     INTEGER,
  calories_target  INTEGER
);

-- Workouts (one per user per day)
CREATE TABLE IF NOT EXISTS workouts (
  id         INTEGER PRIMARY KEY,
  user_id    INTEGER NOT NULL,
  wdate      TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(user_id, wdate)
);

CREATE TABLE IF NOT EXISTS exercises (
  id         INTEGER PRIMARY KEY,
  workout_id INTEGER NOT NULL,
  name       TEXT NOT NULL,
  ord        INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sets (
  id          INTEGER PRIMARY KEY,
  exercise_id INTEGER NOT NULL,
  set_no      INTEGER NOT NULL,
  reps        INTEGER,
  weight      REAL
);

-- Meals
CREATE TABLE IF NOT EXISTS meal_days (
  id      INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  d       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meals (
  id     INTEGER PRIMARY KEY,
  day_id INTEGER NOT NULL,
  name   TEXT,
  ord    INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS meal_items (
  id       INTEGER PRIMARY KEY,
  meal_id  INTEGER NOT NULL,
  name     TEXT,     -- added so food items can have a name
  protein  REAL,
  carbs    REAL,
  calories INTEGER
);
