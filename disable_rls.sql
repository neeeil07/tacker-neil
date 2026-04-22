-- Ejecuta esto en el SQL Editor de Supabase
-- Desactiva Row Level Security en todas las tablas de la app
-- (app personal de un solo usuario, no necesita RLS)

ALTER TABLE exercises    DISABLE ROW LEVEL SECURITY;
ALTER TABLE workout_sets DISABLE ROW LEVEL SECURITY;
ALTER TABLE macros_log   DISABLE ROW LEVEL SECURITY;
ALTER TABLE body_metrics DISABLE ROW LEVEL SECURITY;
ALTER TABLE app_config   DISABLE ROW LEVEL SECURITY;
