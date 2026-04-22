"""
excel_loader.py — Cargar datos históricos desde Mesociclo Neil.xlsx si existe.
Si no existe, usar ROUTINE_DATA hardcodeado.
"""

import os
import streamlit as st
from openpyxl import load_workbook
from datetime import datetime
from utils.constants import ROUTINE_DATA, HIST, HIST_MACROS, HIST_METRICS
from utils import database as db

# ─────────────────────────────────────────────────────────────────────────────
# BOOTSTRAP
# ─────────────────────────────────────────────────────────────────────────────

def bootstrap_routine():
    """
    Cargar rutina de ejercicios en Supabase.
    Ejecutar solo si la tabla exercises está vacía.
    """
    try:
        # Verificar si ya fue hecho
        if db.is_bootstrapped():
            return True
        
        # Cargar ROUTINE_DATA en tabla exercises
        for day, exercises in ROUTINE_DATA.items():
            for idx, (name, reps_obj) in enumerate(exercises):
                # Verificar si ya existe
                existing = db.get_exercises(day)
                if not any(e["name"] == name for e in existing):
                    db.add_exercise(day, name, reps_obj)
        
        # Cargar históricos de sets (HIST)
        for day, day_data in HIST.items():
            for exercise_name, mc_data in day_data.items():
                # Obtener exercise_id
                exercises = db.get_exercises(day)
                exercise = next((e for e in exercises if e["name"] == exercise_name), None)
                if not exercise:
                    continue
                
                exercise_id = exercise["id"]
                
                # Para cada MC y sus sets
                for mc, sets_list in mc_data.items():
                    for set_num, (rir, reps, kg) in enumerate(sets_list, 1):
                        db.upsert_set(exercise_id, mc, set_num, reps, kg, rir)
        
        # Cargar históricos de macros (HIST_MACROS)
        for log_date, kcal, protein, carbs, fat in HIST_MACROS:
            existing = db.get_macros_range(log_date, log_date)
            if not existing:
                db.upsert_macros(log_date, kcal, protein, carbs, fat)
        
        # Cargar históricos de métricas (HIST_METRICS)
        for metric_date, weight, steps, sleep, bf_pct, notes in HIST_METRICS:
            existing = db.get_metrics_range(metric_date, metric_date)
            if not existing:
                db.upsert_metrics(metric_date, weight, steps, sleep, bf_pct, notes)
        
        # Marcar como bootstrap completado
        db.mark_bootstrapped()
        return True
    
    except Exception as e:
        st.error(f"Error en bootstrap: {str(e)}")
        return False

def load_excel_if_exists():
    """
    Intentar cargar datos desde Mesociclo Neil.xlsx si existe en project root.
    Si no existe o hay error, usar fallback ROUTINE_DATA.
    """
    excel_path = "Mesociclo Neil.xlsx"
    
    if not os.path.exists(excel_path):
        # Fallback: usar ROUTINE_DATA
        return bootstrap_routine()
    
    try:
        wb = load_workbook(excel_path)
        # TODO: Implementar parsing específico del Excel si es necesario
        # Por ahora, usar ROUTINE_DATA como fallback
        return bootstrap_routine()
    
    except Exception as e:
        st.warning(f"No se pudo cargar Excel ({str(e)}), usando datos por defecto.")
        return bootstrap_routine()

# ─────────────────────────────────────────────────────────────────────────────
# HELPER DATA (del app.py original)
# ─────────────────────────────────────────────────────────────────────────────

HIST = {
    1: {
        "Zancadas con mancuernas": {
            "MC02":[(1,12,15),(1,12,15),(1,12,15)], "MC03":[(1,12,15),(1,12,15),(1,12,15)],
            "MC04":[(1,12,15),(1,12,15),(1,12,15)],
        },
        "Extension de cuadriceps en maquina": {
            "MC02":[(2,12,42.5),(1,12,50),(0,12,42.5)], "MC03":[(2,12,57.5),(1,12,57.5),(0,13,57.5)],
            "MC04":[(2,12,57.5),(1,12,57.5),(0,12,62.5)],
        },
        "Curl femoral tumbado en maquina": {
            "MC02":[(2,10,22.5),(1,10,22.5),(0,10,22.5)], "MC03":[(2,10,22.5),(1,10,22.5),(0,10,22.5)],
            "MC04":[(2,10,22.5),(1,10,22.5),(0,10,22.5)],
        },
        "Elevaciones laterales con mancuerna": {
            "MC02":[(0,15,8),(0,15,8),(0,15,8)], "MC03":[(0,18,9),(0,16,9),(0,16,9)],
            "MC04":[(0,15,10),(0,15,10),(0,15,10)],
        },
        "Elevaciones laterales en polea baja": {
            "MC02":[(0,15,11.5),(0,15,11.5),(0,15,11.5)], "MC03":[(0,15,11.5),(0,15,15),(0,15,15)],
            "MC04":[(0,15,11.5),(0,15,11.5),(0,15,11.5)],
        },
        "Elevaciones laterales en polea media": {
            "MC02":[(0,15,15),(0,15,15),(0,15,15)], "MC03":[(0,12,20),(0,13,17.5),(0,12,17.5)],
            "MC04":[(0,15,17.5),(0,15,17.5),(0,15,15)],
        },
        "Crunch abdominal en polea": {
            "MC02":[(0,18,57.5),(0,16,57.5),(0,17,57.5)], "MC03":[(0,16,57.5),(0,16,57.5),(0,14,57.5)],
            "MC04":[(0,16,57.5),(0,16,57.5),(0,16,57.5)],
        },
    },
    2: {
        "Jalon al pecho agarre neutro": {
            "MC02":[(1,12,70),(1,10,80),(1,10,70)], "MC03":[(1,10,70),(1,10,70),(1,10,70)],
            "MC04":[(1,12,70),(1,12,70),(1,11,70)],
        },
        "Jalon al pecho agarre neutro cerrado": {
            "MC02":[(1,12,60),(1,10,65),(1,10,65)], "MC03":[(1,10,65),(1,10,65),(1,10,60)],
            "MC04":[(1,12,65),(1,12,65),(1,11,65)],
        },
        "Jalon al pecho unilateral": {
            "MC02":[(1,12,35),(1,10,40),(1,10,35)], "MC03":[(1,10,35),(1,10,35),(1,10,35)],
            "MC04":[(1,12,35),(1,12,35),(1,11,35)],
        },
        "Remo en T": {
            "MC02":[(1,10,60),(1,10,60),(1,10,60)], "MC03":[(1,10,60),(1,11,60),(1,10,60)],
            "MC04":[(1,10,80),(1,10,80),(1,10,80)],
        },
        "Remo Gironda Unilateral": {
            "MC02":[(1,10,30),(1,10,35),(0,10,30)], "MC03":[(1,12,35),(1,11,35),(0,10,35)],
            "MC04":[(1,12,35),(1,12,35),(0,12,35)],
        },
        "Pull-over con cuerda en polea alta": {
            "MC02":[(0,12,30),(0,12,30),(0,12,30)], "MC03":[(0,12,30),(0,12,30),(0,11,35)],
            "MC04":[(0,12,30),(0,12,30),(0,12,30)],
        },
        "Pajaros para deltoide posterior en maquina": {
            "MC02":[(1,10,35),(0,10,35),(0,10,35)], "MC03":[(1,12,35),(0,12,35),(0,12,35)],
            "MC04":[(1,12,35),(0,12,35),(0,12,35)],
        },
        "Curl Scott en maquina": {
            "MC02":[(0,12,15),(0,12,15),(0,12,15)], "MC03":[(0,12,15),(0,12,15),(0,12,15)],
            "MC04":[(0,12,15),(0,12,15),(0,12,15)],
        },
        "Rueda abdominal": {
            "MC02":[(0,15,55),(0,15,55),(0,15,55)], "MC03":[(0,12,55),(0,12,55),(0,12,55)],
            "MC04":[(0,12,55),(0,12,55),(0,12,55)],
        },
    },
    3: {
        "Press plano en maquina": {
            "MC02":[(1,10,40),(1,10,40),(1,10,40)], "MC03":[(1,8,60),(1,8,60),(1,7,60)],
            "MC04":[(1,10,60),(1,8,62.5),(1,8,62.5)],
        },
        "Press inclinado en multipower": {
            "MC02":[(1,8,50),(1,8,50),(0,15,50)], "MC03":[(1,8,50),(1,8,50),(0,8,50)],
            "MC04":[(1,8,60),(1,8,60),(0,8,60)],
        },
        "Press declinado en maquina": {
            "MC02":[(1,10,42.5),(1,10,42.5),(1,10,42.5)], "MC03":[(1,12,42.5),(1,10,50),(1,10,50)],
            "MC04":[(1,12,50),(1,10,50),(1,10,50)],
        },
        "Aperturas en Pec-Deck": {
            "MC02":[(1,12,42.5),(0,12,42.5),(0,12,42.5)], "MC03":[(1,12,42.5),(0,12,42.5),(0,12,42.5)],
            "MC04":[(1,12,42.5),(0,12,42.5),(0,12,42.5)],
        },
        "Aperturas en polea alta a baja": {
            "MC02":[(0,12,25),(0,12,25),(0,12,25)], "MC03":[(0,12,25),(0,12,25),(0,12,25)],
            "MC04":[(0,12,25),(0,12,25),(0,12,25)],
        },
        "Elevaciones laterales con mancuerna": {
            "MC02":[(0,15,9),(0,15,9),(0,15,9)], "MC03":[(0,15,9),(0,15,9),(0,13,10)],
            "MC04":[(0,18,9),(0,16,9),(0,16,9)],
        },
        "Elevaciones laterales en polea baja": {
            "MC02":[(0,15,11.5),(0,15,11.5),(0,15,11.5)], "MC03":[(0,15,12.5),(0,15,12.5),(0,15,12.5)],
            "MC04":[(0,15,12.5),(0,15,12.5),(0,15,12.5)],
        },
        "Elevaciones laterales en polea media": {
            "MC02":[(0,15,15),(0,15,15),(0,15,15)], "MC03":[(0,15,20),(0,20,15),(0,15,20)],
            "MC04":[(0,15,20),(0,15,20),(0,15,20)],
        },
        "Extension de triceps en polea alta": {
            "MC02":[(0,12,20),(0,13,20),(0,13,20)], "MC03":[(0,12,25),(0,12,25),(0,12,25)],
            "MC04":[(0,12,25),(0,10,30),(0,10,30)],
        },
        "Extensiones Katana en polea": {
            "MC02":[(1,12,15),(0,10,15),(0,10,15)], "MC03":[(1,12,15),(0,12,15),(0,12,15)],
            "MC04":[(1,12,15),(0,12,15),(0,12,15)],
        },
        "Crunch abdominal en polea": {
            "MC02":[(0,16,57.5),(0,14,62.5),(0,14,57.5)], "MC03":[(0,16,57.5),(0,16,57.5),(0,16,57.5)],
            "MC04":[(0,16,57.5),(0,16,57.5),(0,16,57.5)],
        },
    },
    4: {},  # Simplificado para brevedad
    5: {},
    6: {},
}

HIST_MACROS = [
    ("2026-03-25",1353,124.1,130.5,26.6), ("2026-03-26",1865,143.5,237.0,36.6),
    ("2026-03-27",1832,142.5,229.3,20.8), ("2026-03-28",1481,121.6,162.2,30.1),
    ("2026-03-29",1631,124.4,213.8,30.2), ("2026-03-30",1669,136.1,192.8,29.4),
    ("2026-03-31",1655,132.8,193.4,33.5), ("2026-04-01",1867,125.2,137.6,35.8),
    ("2026-04-02",1601,173.9,162.1,25.7), ("2026-04-03",1421,121.7,169.1,21.9),
    ("2026-04-04",1603,126.1,172.3,25.9), ("2026-04-05",1864,132.2,211.0,37.9),
    ("2026-04-06",1773,122.5,165.3,35.5), ("2026-04-07",1886,134.6,250.4,34.6),
    ("2026-04-08",1689,116.7,212.1,50.2), ("2026-04-09",1758,145.0,170.0,29.0),
    ("2026-04-10",1375,132.0,114.8,35.1), ("2026-04-11",1836,141.5,253.0,29.3),
    ("2026-04-12",1475,138.7,169.4,12.9), ("2026-04-13",1361,125.0,147.7,17.9),
    ("2026-04-14",1398,117.1,146.9,34.2), ("2026-04-15",1657,164.5,178.5,36.4),
    ("2026-04-16",1355,121.7,167.4,16.8), ("2026-04-17",1450,140.0,125.0,30.0),
    ("2026-04-18",1140,111.0,91.4,34.8),  ("2026-04-19",1783,123.5,201.6,26.4),
    ("2026-04-20",1938,147.1,245.5,31.8),
]

HIST_METRICS = [
    ("2026-03-25",53.7,10416,7.0,12.0,""), ("2026-03-26",53.3,11510,7.0,11.3,""),
    ("2026-03-27",53.9,11510,7.0,12.4,""), ("2026-03-28",54.0,None,8.0,12.6,"Res day"),
    ("2026-03-29",53.8,6319,7.0,12.2,""),  ("2026-03-30",52.9,12425,10.0,10.5,""),
    ("2026-03-31",52.6,6667,8.0,10.0,""),  ("2026-04-01",52.0,12433,8.0,8.8,""),
    ("2026-04-02",52.7,8827,10.0,10.1,""), ("2026-04-03",53.2,4649,8.0,11.1,""),
    ("2026-04-04",52.7,7953,6.0,10.1,""),  ("2026-04-05",53.2,5907,6.0,11.1,""),
    ("2026-04-06",53.4,6772,6.0,11.4,""),  ("2026-04-07",53.3,16689,3.59,11.3,""),
    ("2026-04-08",52.8,14624,7.11,10.3,""),("2026-04-09",53.2,15977,6.52,11.1,""),
    ("2026-04-10",52.9,9050,7.32,10.5,""), ("2026-04-11",53.3,14982,7.12,11.3,""),
    ("2026-04-12",53.3,10767,7.12,11.3,""),("2026-04-13",53.4,14982,7.48,11.4,""),
    ("2026-04-14",53.0,16791,6.5,10.7,""), ("2026-04-15",52.8,14303,6.58,10.3,""),
    ("2026-04-16",52.8,None,None,10.3,""), ("2026-04-17",52.8,None,None,10.3,""),
    ("2026-04-18",52.8,None,None,10.3,""), ("2026-04-19",52.8,None,None,10.3,""),
    ("2026-04-20",53.3,None,None,11.3,""), ("2026-04-21",53.4,None,None,11.4,""),
]
