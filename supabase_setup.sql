-- Ejecuta esto en el SQL Editor de Supabase (una vez)
-- https://supabase.com/dashboard/project/xjudkbyktndaimkypaze/sql

CREATE TABLE IF NOT EXISTS exercises (
    id        SERIAL PRIMARY KEY,
    day       INTEGER NOT NULL,
    name      TEXT NOT NULL,
    reps_obj  TEXT DEFAULT '8-12',
    order_idx INTEGER DEFAULT 0,
    active    INTEGER DEFAULT 1,
    UNIQUE(day, name)
);

CREATE TABLE IF NOT EXISTS workout_sets (
    id          SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id),
    microcycle  TEXT NOT NULL,
    set_num     INTEGER NOT NULL,
    reps        REAL DEFAULT 0,
    kg          REAL DEFAULT 0,
    rir         REAL DEFAULT 1,
    UNIQUE(exercise_id, microcycle, set_num)
);

CREATE TABLE IF NOT EXISTS macros_log (
    log_date DATE PRIMARY KEY,
    kcal     REAL DEFAULT 0,
    protein  REAL DEFAULT 0,
    carbs    REAL DEFAULT 0,
    fat      REAL DEFAULT 0,
    notes    TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS body_metrics (
    metric_date DATE PRIMARY KEY,
    weight      REAL,
    steps       REAL,
    sleep       REAL,
    bf_pct      REAL,
    notes       TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS app_config (
    key   TEXT PRIMARY KEY,
    value TEXT
);
