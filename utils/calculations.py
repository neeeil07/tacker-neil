"""
calculations.py — Lógica de cálculos: tonelaje, validaciones, tendencias
"""

import pandas as pd
from datetime import datetime, timedelta, date
from utils.constants import MACROS_TARGET, STEPS_TARGET
from utils import database as db

# ─────────────────────────────────────────────────────────────────────────────
# VALIDATIONS
# ─────────────────────────────────────────────────────────────────────────────

def validate_set_input(reps: float, kg: float, rir: float) -> tuple[bool, str]:
    """Validar inputs de un set (reps, kg, rir). Retorna (is_valid, error_message)."""
    if reps < 0 or kg < 0 or rir < 0:
        return False, "Valores no pueden ser negativos"
    if reps == 0 or kg == 0:
        return False, "Reps y Kg no pueden ser 0"
    if rir < -5 or rir > 5:
        return False, "RIR debe estar entre -5 y 5"
    return True, ""

def validate_macros_input(kcal: float, protein: float, carbs: float, fat: float) -> tuple[bool, str]:
    """Validar inputs de macros. Retorna (is_valid, error_message)."""
    if kcal < 0 or protein < 0 or carbs < 0 or fat < 0:
        return False, "Valores no pueden ser negativos"
    if kcal == 0 and protein == 0 and carbs == 0 and fat == 0:
        return False, "Debe registrar al menos una macro"
    
    # Aproximación: 4 kcal/g proteína, 4 kcal/g carbs, 9 kcal/g grasa
    estimated_kcal = (protein * 4) + (carbs * 4) + (fat * 9)
    tolerance = kcal * 0.15  # 15% de tolerancia
    
    if abs(kcal - estimated_kcal) > tolerance:
        return False, f"Kcal inconsistente. Estimado: {int(estimated_kcal)} (tolerancia: ±{int(tolerance)})"
    
    return True, ""

def validate_steps_input(steps: float, is_weekend: bool = False) -> tuple[bool, str]:
    """Validar input de pasos según día."""
    if steps < 0:
        return False, "Pasos no pueden ser negativos"
    target = STEPS_TARGET["weekend"] if is_weekend else STEPS_TARGET["weekday"]
    if steps > target * 1.5:
        return False, f"Pasos demasiado altos (máximo lógico: {int(target * 1.5)})"
    return True, ""

# ─────────────────────────────────────────────────────────────────────────────
# TONELAJE CALCULATIONS
# ─────────────────────────────────────────────────────────────────────────────

def calc_exercise_tonelaje(reps: float, kg: float) -> float:
    """Calcular tonelaje de un set: reps * kg."""
    return reps * kg

def calc_session_tonelaje(day: int, microcycle: str) -> float:
    """Calcular tonelaje total de una sesión (día + MC)."""
    return db.get_tonelaje_by_day_mc(day, microcycle)

def get_exercise_tonelaje_trend(exercise_id: int) -> dict:
    """Obtener histórico de tonelaje de un ejercicio por MC. Retorna {MC: tonelaje}."""
    return db.get_exercise_tonelaje_history(exercise_id)

# ─────────────────────────────────────────────────────────────────────────────
# MACROS CALCULATIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_macro_vs_target(log_date: str = None) -> dict:
    """
    Obtener macros del día vs target.
    Retorna: {
        'kcal': {'current': X, 'target': Y, 'pct': Z, 'status': 'ok'|'over'},
        'protein': {...},
        'carbs': {...},
        'fat': {...},
    }
    """
    if log_date is None:
        log_date = str(date.today())
    
    macros = db.get_macros_today() if log_date == str(date.today()) else db.get_macros_range(log_date, log_date)[0] if log_date else None
    
    result = {}
    for macro_name, target_val in MACROS_TARGET.items():
        if macros:
            current_val = macros.get(macro_name, 0)
        else:
            current_val = 0
        
        pct = (current_val / target_val * 100) if target_val > 0 else 0
        status = "ok" if current_val <= target_val else "over"
        
        result[macro_name] = {
            "current": current_val,
            "target": target_val,
            "pct": pct,
            "status": status,
        }
    
    return result

def get_weight_trend(days: int = 30) -> pd.DataFrame:
    """Obtener tendencia de peso (últimos N días). Retorna DataFrame con columns [metric_date, weight]."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    metrics = db.get_metrics_range(str(start_date), str(end_date))
    df = pd.DataFrame(metrics) if metrics else pd.DataFrame(columns=["metric_date", "weight"])
    
    if not df.empty:
        df["metric_date"] = pd.to_datetime(df["metric_date"])
        df = df.sort_values("metric_date")
    
    return df

def get_bf_trend(days: int = 30) -> pd.DataFrame:
    """Obtener tendencia de BF% (últimos N días). Retorna DataFrame con columns [metric_date, bf_pct]."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    metrics = db.get_metrics_range(str(start_date), str(end_date))
    df = pd.DataFrame(metrics) if metrics else pd.DataFrame(columns=["metric_date", "bf_pct"])
    
    if not df.empty:
        df["metric_date"] = pd.to_datetime(df["metric_date"])
        df = df.sort_values("metric_date")
    
    return df

def get_weight_change() -> dict:
    """
    Obtener cambio de peso desde el inicio.
    Retorna: {'current': X, 'initial': Y, 'change': Z, 'pct_change': W}
    """
    metrics = db.get_metrics_range("2000-01-01", str(date.today()))
    
    if not metrics:
        return {"current": 0, "initial": 0, "change": 0, "pct_change": 0}
    
    current = metrics[-1]["weight"] if metrics[-1]["weight"] else 0
    initial = metrics[0]["weight"] if metrics[0]["weight"] else 0
    
    change = current - initial
    pct_change = (change / initial * 100) if initial > 0 else 0
    
    return {
        "current": current,
        "initial": initial,
        "change": change,
        "pct_change": pct_change,
    }

def get_macros_range_trend(days: int = 14) -> pd.DataFrame:
    """Obtener histórico de macros (últimos N días)."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    macros = db.get_macros_range(str(start_date), str(end_date))
    df = pd.DataFrame(macros) if macros else pd.DataFrame()
    
    if not df.empty:
        df["log_date"] = pd.to_datetime(df["log_date"])
        df = df.sort_values("log_date")
    
    return df

def get_steps_vs_target(log_date: str = None) -> dict:
    """Obtener pasos del día vs target (diferenciado L-V vs S-D)."""
    if log_date is None:
        log_date = str(date.today())
    
    # Determinar si es fin de semana (0=Mon, 6=Sun)
    date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    is_weekend = date_obj.weekday() >= 4  # Viernes=4, Sábado=5, Domingo=6
    
    target = STEPS_TARGET["weekend"] if is_weekend else STEPS_TARGET["weekday"]
    
    metrics = db.get_metrics_today() if log_date == str(date.today()) else db.get_metrics_range(log_date, log_date)
    
    if metrics and isinstance(metrics, list):
        metrics = metrics[0] if metrics else None
    
    current = metrics["steps"] if metrics and metrics.get("steps") else 0
    pct = (current / target * 100) if target > 0 else 0
    status = "ok" if current >= target else "pending"
    
    return {
        "current": current,
        "target": target,
        "pct": pct,
        "status": status,
        "is_weekend": is_weekend,
    }

# ─────────────────────────────────────────────────────────────────────────────
# BODY METRICS CALCULATIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_bf_change() -> dict:
    """
    Obtener cambio de BF% desde el inicio.
    Retorna: {'current': X, 'initial': Y, 'change': Z}
    """
    metrics = db.get_metrics_range("2000-01-01", str(date.today()))
    
    if not metrics:
        return {"current": 12.0, "initial": 12.0, "change": 0}
    
    current = metrics[-1]["bf_pct"] if metrics[-1]["bf_pct"] else 12.0
    initial = metrics[0]["bf_pct"] if metrics[0]["bf_pct"] else 12.0
    
    change = current - initial
    
    return {
        "current": current,
        "initial": initial,
        "change": change,
    }

def get_bf_status(bf_pct: float) -> str:
    """Obtener estado de BF% (rojo/naranja/verde)."""
    if bf_pct > 15:
        return "over"
    elif bf_pct >= 12:
        return "warning"
    else:
        return "ok"
