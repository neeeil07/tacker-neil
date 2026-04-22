"""
database.py — Wrapper para operaciones Supabase
Todas las queries a training_logs, macros_log, body_metrics, exercises van aquí.
"""

import streamlit as st
from datetime import datetime, date
import time

# ─────────────────────────────────────────────────────────────────────────────
# DECORATORS & HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def retry_operation(func, max_retries=3, backoff_multiplier=1.5):
    """Reintentar operación con backoff exponencial en caso de error Supabase."""
    attempt = 0
    wait_time = 1
    while attempt < max_retries:
        try:
            return func()
        except Exception as e:
            attempt += 1
            if attempt >= max_retries:
                raise
            time.sleep(wait_time)
            wait_time *= backoff_multiplier

def get_supabase():
    """Obtener conexión Supabase (singleton via st.connection)."""
    return st.connection("supabase", type="SupabaseConnection").client()

# ─────────────────────────────────────────────────────────────────────────────
# EXERCISES TABLE
# ─────────────────────────────────────────────────────────────────────────────

def get_exercises(day: int):
    """Obtener ejercicios de un día específico, ordenados por order_idx."""
    def _query():
        supabase = get_supabase()
        response = supabase.table("exercises").select(
            "id, day, name, reps_obj, order_idx, active"
        ).eq("day", day).eq("active", True).order("order_idx", desc=False).execute()
        return response.data
    
    return retry_operation(_query)

def add_exercise(day: int, name: str, reps_obj: str = "8-12"):
    """Agregar nuevo ejercicio a un día."""
    def _query():
        supabase = get_supabase()
        # Obtener máximo order_idx para este día
        existing = supabase.table("exercises").select("order_idx").eq("day", day).order("order_idx", desc=True).limit(1).execute()
        next_idx = (existing.data[0]["order_idx"] if existing.data else 0) + 1
        
        response = supabase.table("exercises").insert({
            "day": day,
            "name": name,
            "reps_obj": reps_obj,
            "order_idx": next_idx,
            "active": True,
        }).execute()
        return response.data
    
    return retry_operation(_query)

def deactivate_exercise(exercise_id: int):
    """Soft-delete: marcar ejercicio como inactivo."""
    def _query():
        supabase = get_supabase()
        response = supabase.table("exercises").update({"active": False}).eq("id", exercise_id).execute()
        return response.data
    
    return retry_operation(_query)

# ─────────────────────────────────────────────────────────────────────────────
# WORKOUT_SETS TABLE
# ─────────────────────────────────────────────────────────────────────────────

def get_workout_sets(exercise_id: int, microcycle: str):
    """Obtener todos los sets de un ejercicio en un microciclo."""
    def _query():
        supabase = get_supabase()
        response = supabase.table("workout_sets").select(
            "id, exercise_id, microcycle, set_num, reps, kg, rir"
        ).eq("exercise_id", exercise_id).eq("microcycle", microcycle).order("set_num", desc=False).execute()
        return response.data
    
    return retry_operation(_query)

def upsert_set(exercise_id: int, microcycle: str, set_num: int, reps: float, kg: float, rir: float):
    """Insertar o actualizar un set de entrenamiento."""
    if reps <= 0 or kg <= 0:
        raise ValueError("Reps y Kg deben ser > 0")
    
    def _query():
        supabase = get_supabase()
        # Verificar si existe
        existing = supabase.table("workout_sets").select("id").eq("exercise_id", exercise_id).eq("microcycle", microcycle).eq("set_num", set_num).execute()
        
        if existing.data:
            # UPDATE
            response = supabase.table("workout_sets").update({
                "reps": reps,
                "kg": kg,
                "rir": rir,
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            # INSERT
            response = supabase.table("workout_sets").insert({
                "exercise_id": exercise_id,
                "microcycle": microcycle,
                "set_num": set_num,
                "reps": reps,
                "kg": kg,
                "rir": rir,
            }).execute()
        
        return response.data
    
    return retry_operation(_query)

def delete_set(workout_set_id: int):
    """Eliminar un set de entrenamiento."""
    def _query():
        supabase = get_supabase()
        response = supabase.table("workout_sets").delete().eq("id", workout_set_id).execute()
        return response.data
    
    return retry_operation(_query)

def get_tonelaje_by_day_mc(day: int, microcycle: str):
    """Calcular tonelaje total (SUM reps*kg) para un día en un MC."""
    def _query():
        supabase = get_supabase()
        # JOIN entre workout_sets y exercises, filtrar por día y MC, sumar tonelaje
        response = supabase.table("workout_sets").select(
            "id, reps, kg, exercise_id"
        ).eq("microcycle", microcycle).execute()
        
        # Filtrar por day manualmente (Supabase join puede ser complejo sin RLS)
        all_sets = response.data
        day_exercises = supabase.table("exercises").select("id").eq("day", day).execute().data
        day_exercise_ids = [e["id"] for e in day_exercises]
        
        total = 0
        for s in all_sets:
            if s["exercise_id"] in day_exercise_ids:
                total += s["reps"] * s["kg"]
        
        return total
    
    return retry_operation(_query)

def get_exercise_tonelaje_history(exercise_id: int):
    """Obtener histórico de tonelaje (por MC) de un ejercicio."""
    def _query():
        supabase = get_supabase()
        response = supabase.table("workout_sets").select(
            "microcycle, reps, kg"
        ).eq("exercise_id", exercise_id).execute()
        
        # Agrupar y sumar por MC
        history = {}
        for s in response.data:
            mc = s["microcycle"]
            tonelaje = s["reps"] * s["kg"]
            if mc not in history:
                history[mc] = 0
            history[mc] += tonelaje
        
        return history
    
    return retry_operation(_query)

# ─────────────────────────────────────────────────────────────────────────────
# MACROS_LOG TABLE
# ─────────────────────────────────────────────────────────────────────────────

def get_macros_today():
    """Obtener registro de macros de hoy."""
    today = str(date.today())
    def _query():
        supabase = get_supabase()
        response = supabase.table("macros_log").select(
            "id, log_date, kcal, protein, carbs, fat, notes"
        ).eq("log_date", today).execute()
        return response.data[0] if response.data else None
    
    return retry_operation(_query)

def upsert_macros(log_date: str, kcal: float, protein: float, carbs: float, fat: float, notes: str = ""):
    """Insertar o actualizar registro de macros."""
    def _query():
        supabase = get_supabase()
        existing = supabase.table("macros_log").select("id").eq("log_date", log_date).execute()
        
        if existing.data:
            response = supabase.table("macros_log").update({
                "kcal": kcal,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
                "notes": notes,
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            response = supabase.table("macros_log").insert({
                "log_date": log_date,
                "kcal": kcal,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
                "notes": notes,
            }).execute()
        
        return response.data
    
    return retry_operation(_query)

def get_macros_range(start_date: str, end_date: str):
    """Obtener histórico de macros en un rango de fechas."""
    def _query():
        supabase = get_supabase()
        response = supabase.table("macros_log").select(
            "log_date, kcal, protein, carbs, fat, notes"
        ).gte("log_date", start_date).lte("log_date", end_date).order("log_date", desc=False).execute()
        return response.data
    
    return retry_operation(_query)

# ─────────────────────────────────────────────────────────────────────────────
# BODY_METRICS TABLE
# ─────────────────────────────────────────────────────────────────────────────

def get_metrics_today():
    """Obtener métricas corporales de hoy."""
    today = str(date.today())
    def _query():
        supabase = get_supabase()
        response = supabase.table("body_metrics").select(
            "id, metric_date, weight, steps, sleep, bf_pct, notes"
        ).eq("metric_date", today).execute()
        return response.data[0] if response.data else None
    
    return retry_operation(_query)

def upsert_metrics(metric_date: str, weight: float = None, steps: float = None, sleep: float = None, bf_pct: float = None, notes: str = ""):
    """Insertar o actualizar métricas corporales."""
    def _query():
        supabase = get_supabase()
        existing = supabase.table("body_metrics").select("id").eq("metric_date", metric_date).execute()
        
        data = {"notes": notes}
        if weight is not None:
            data["weight"] = weight
        if steps is not None:
            data["steps"] = steps
        if sleep is not None:
            data["sleep"] = sleep
        if bf_pct is not None:
            data["bf_pct"] = bf_pct
        
        if existing.data:
            response = supabase.table("body_metrics").update(data).eq("id", existing.data[0]["id"]).execute()
        else:
            data["metric_date"] = metric_date
            response = supabase.table("body_metrics").insert(data).execute()
        
        return response.data
    
    return retry_operation(_query)

def get_metrics_range(start_date: str, end_date: str):
    """Obtener histórico de métricas en rango de fechas."""
    def _query():
        supabase = get_supabase()
        response = supabase.table("body_metrics").select(
            "metric_date, weight, steps, sleep, bf_pct, notes"
        ).gte("metric_date", start_date).lte("metric_date", end_date).order("metric_date", desc=False).execute()
        return response.data
    
    return retry_operation(_query)

# ─────────────────────────────────────────────────────────────────────────────
# APP_CONFIG TABLE
# ─────────────────────────────────────────────────────────────────────────────

def get_config(key: str):
    """Obtener valor de configuración."""
    def _query():
        supabase = get_supabase()
        response = supabase.table("app_config").select("value").eq("key", key).execute()
        return response.data[0]["value"] if response.data else None
    
    return retry_operation(_query)

def set_config(key: str, value: str):
    """Establecer o actualizar valor de configuración."""
    def _query():
        supabase = get_supabase()
        existing = supabase.table("app_config").select("key").eq("key", key).execute()
        
        if existing.data:
            response = supabase.table("app_config").update({"value": value}).eq("key", key).execute()
        else:
            response = supabase.table("app_config").insert({"key": key, "value": value}).execute()
        
        return response.data
    
    return retry_operation(_query)

def get_current_mc():
    """Obtener microciclo activo."""
    mc = get_config("current_mc")
    return mc if mc else "MC01"

def set_current_mc(mc: str):
    """Establecer microciclo activo."""
    set_config("current_mc", mc)

def is_bootstrapped():
    """Verificar si el bootstrap ya fue ejecutado."""
    value = get_config("bootstrapped")
    return value == "true"

def mark_bootstrapped():
    """Marcar que bootstrap fue ejecutado."""
    set_config("bootstrapped", "true")
