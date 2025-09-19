PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  email         TEXT UNIQUE NOT NULL,
  username      TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at    TEXT DEFAULT (datetime('now'))
  ALTER TABLE users ADD COLUMN height_cm INTEGER;
  ALTER TABLE users ADD COLUMN weight_kg REAL;
  ALTER TABLE users ADD COLUMN age INTEGER;
  ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'en';
  -- Workouts (one per user per day)
  CREATE TABLE workouts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    wdate TEXT NOT NULL,              
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, wdate)
  );

  CREATE TABLE exercises (
    id INTEGER PRIMARY KEY,
    workout_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    ord INTEGER DEFAULT 0
  );

  CREATE TABLE sets (
    id INTEGER PRIMARY KEY,
    exercise_id INTEGER NOT NULL,
    set_no INTEGER NOT NULL,
    reps INTEGER,
    weight REAL
  );

  -- Meals
  CREATE TABLE IF NOT EXISTS meal_days (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  d TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meals (
  id INTEGER PRIMARY KEY,
  day_id INTEGER NOT NULL,
  name TEXT,
  ord INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS meal_items (
  id INTEGER PRIMARY KEY,
  meal_id INTEGER NOT NULL,
  protein REAL,
  carbs REAL,
  calories INTEGER
);
