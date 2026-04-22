"""
app.py  —  Centro de Mando · Neil Mesociclo
Migración completa desde Mesociclo_Neil.xlsx → Streamlit + SQLite
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime, timedelta
import os

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Training Command Center · Neil", page_icon=None, layout="wide")

DB_PATH = "training.db"
MACROS_TARGET = {"kcal": 1850, "protein": 135, "fat": 40, "carbs": 235}

DAY_LABELS = {
    1: ("DOM", "Pierna + Hombro + Core"),
    2: ("LUN", "Espalda + Bíceps"),
    3: ("MAR", "Pecho + Hombro + Tríceps + Core"),
    4: ("MIÉ", "Pierna Compuesta + Core"),
    5: ("JUE", "Espalda + Bíceps + Core"),
    6: ("VIE", "Hombro + Pecho + Tríceps + Core"),
}

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────────────────────
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS exercises (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        day      INTEGER NOT NULL,
        name     TEXT NOT NULL,
        reps_obj TEXT DEFAULT '8-12',
        order_idx INTEGER DEFAULT 0,
        active   INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS workout_sets (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_id INTEGER NOT NULL,
        microcycle  TEXT NOT NULL,
        set_num     INTEGER NOT NULL,
        reps        REAL DEFAULT 0,
        kg          REAL DEFAULT 0,
        rir         REAL DEFAULT 1,
        FOREIGN KEY(exercise_id) REFERENCES exercises(id)
    );
    CREATE TABLE IF NOT EXISTS macros_log (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date TEXT UNIQUE,
        kcal     REAL DEFAULT 0,
        protein  REAL DEFAULT 0,
        carbs    REAL DEFAULT 0,
        fat      REAL DEFAULT 0,
        notes    TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS body_metrics (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        metric_date TEXT UNIQUE,
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
    """)
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# BOOTSTRAP DATA
# ─────────────────────────────────────────────────────────────────────────────
ROUTINE_DATA = {
    1: [
        ("Zancadas con mancuernas", "10-12"),
        ("Extension de cuadriceps en maquina", "12-15 + DS"),
        ("Curl femoral tumbado en maquina", "12-15 + DS"),
        ("Elevaciones laterales con mancuerna", "15-20"),
        ("Elevaciones laterales en polea baja", "15-20"),
        ("Elevaciones laterales en polea media", "15-20"),
        ("Press declinado en maquina Smith", "8-12"),       # NUEVO
        ("Crunch abdominal en polea", "15-20 + Fallo"),
    ],
    2: [
        ("Jalon al pecho agarre neutro", "10-12"),
        ("Jalon al pecho agarre neutro cerrado", "10-12"),
        ("Jalon al pecho unilateral", "10-12"),
        ("Remo en T", "12-15 + RP"),                        # sustituye Remo mancuerna
        ("Remo Gironda Unilateral", "12-15 + RP"),          # sustituye Remo Gironda bilateral
        ("Pull-over con cuerda en polea alta", "12-15"),
        ("Pajaros para deltoide posterior en maquina", "15-20 + DS"),
        ("Curl Scott en maquina", "10-12 + Fallo"),
        ("Rueda abdominal", "10-15 + Fallo"),
    ],
    3: [
        ("Press plano en maquina", "8-12"),
        ("Press inclinado en multipower", "8-12 + RP"),
        ("Press declinado en maquina", "10-12"),
        ("Aperturas en Pec-Deck", "12-15 + DS"),
        ("Aperturas en polea alta a baja", "12-15"),        # NUEVO
        ("Elevaciones laterales con mancuerna", "15-20"),
        ("Elevaciones laterales en polea baja", "15-20"),
        ("Elevaciones laterales en polea media", "15-20"),
        ("Extension de triceps en polea alta", "12-15 + Fallo"),
        ("Extensiones Katana en polea", "12-15 + DS"),
        ("Crunch abdominal en polea", "15-20 + Fallo"),
    ],
    4: [
        ("Peso muerto rumano con mancuernas", "10-12"),
        ("Prensa de piernas inclinada", "10-12 + Fallo"),
        ("Extension de cuadriceps en maquina", "12-15 + DS"),
        ("Curl femoral sentado en maquina", "12-15 + RP"),
        ("Aductores en maquina", "15-20"),
        ("Gemelos en prensa", "15-20 + Fallo"),
        ("Elevaciones de piernas tumbado", "12-15 + Fallo"),
    ],
    5: [
        ("Remo Gironda Unilateral", "12-15"),               # tríada garantizada
        ("Remo con mancuerna unilateral", "10-12/lado"),
        ("Remo en T", "10-12"),
        ("Jalon al pecho con agarre neutro", "10-12 + RP"),
        ("Curl martillo con mancuernas", "10-12 + DS"),
        ("Curl Bayesian en polea", "12-15 + Fallo"),
        ("Plancha abdominal lastrada", "30-60 seg"),
    ],
    6: [
        ("Elevaciones laterales con mancuerna", "15-20"),
        ("Elevaciones laterales en polea baja", "15-20"),
        ("Elevaciones laterales en polea media", "15-20"),
        ("Press inclinado con mancuernas", "8-12"),
        ("Press plano convergente en maquina", "8-12"),
        ("Cruces en polea de alta a baja", "12-15"),
        ("Aperturas en polea baja", "12-15"),
        ("Fondos en maquina (pecho inferior)", "Al fallo"), # NUEVO
        ("Fondos de triceps en maquina", "10-12 + Fallo"),
        ("Extension de triceps a una mano en polea", "12-15"),
        ("Crunch abdominal en polea", "15-20 + Fallo"),
    ],
}

# Historical sets: {day: {exercise_name: {MC: [(rir,reps,kg),...]}}}
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
        "Remo en maquina con apoyo en el pecho": {
            "MC02":[(1,10,60),(1,10,60),(1,10,60)], "MC03":[(1,10,60),(1,11,60),(1,10,60)],
            "MC04":[(1,10,80),(1,10,80),(1,10,80)],
        },
        "Remo Gironda en polea baja": {
            "MC02":[(1,10,70),(1,10,80),(0,10,70)], "MC03":[(1,12,80),(1,11,80),(0,10,80)],
            "MC04":[(1,12,80),(1,12,80),(0,12,80)],
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
    4: {
        "Peso muerto rumano con mancuernas": {
            "MC01":[(1,12,17.5),(1,12,17.5),(1,12,17.5)], "MC02":[(1,12,15),(1,12,15),(1,12,15)],
            "MC03":[(1,12,15),(1,12,15),(1,12,15)], "MC04":[(1,12,15),(1,12,15),(1,12,15)],
        },
        "Prensa de piernas inclinada": {
            "MC01":[(0,12,150),(0,10,150),(0,10,150)], "MC02":[(0,12,150),(0,9,150),(0,10,150)],
            "MC03":[(0,10,160),(0,10,160),(0,10,160)], "MC04":[(0,12,165),(0,10,185),(0,8,185)],
        },
        "Extension de cuadriceps en maquina": {
            "MC01":[(1,12,60),(0,12,60),(0,12,60)], "MC02":[(1,12,60),(0,12,60),(0,12,60)],
            "MC03":[(1,12,57.5),(0,12,57.5),(0,12,57.5)], "MC04":[(1,12,57.5),(0,12,57.5),(0,12,57.5)],
        },
        "Curl femoral sentado en maquina": {
            "MC01":[(1,13,47.5),(1,12,47.5),(0,12,47.5)], "MC02":[(1,12,47.5),(1,12,47.5),(0,12,47.5)],
            "MC03":[(1,12,42.5),(1,12,42.5),(0,12,42.5)], "MC04":[(1,12,42.5),(1,12,50),(0,12,50)],
        },
        "Aductores en maquina": {
            "MC01":[(0,15,35),(0,15,35),(0,13,35)], "MC02":[(0,15,35),(0,15,35),(0,15,35)],
            "MC03":[(0,12,35),(0,12,35),(0,12,35)], "MC04":[(0,12,42.5),(0,12,42.5),(0,12,42.5)],
        },
        "Gemelos en prensa": {
            "MC01":[(0,18,100),(0,18,100),(0,16,100)], "MC02":[(0,18,100),(0,18,100),(0,18,100)],
            "MC03":[(0,18,100),(0,18,100),(0,18,100)], "MC04":[(0,18,100),(0,18,100),(0,18,100)],
        },
        "Elevaciones de piernas tumbado": {
            "MC01":[(0,12,50),(0,12,50),(0,12,50)], "MC02":[(0,13,50),(0,13,50),(0,14,50)],
            "MC03":[(0,13,50),(0,13,50),(0,13,50)], "MC04":[(0,13,50),(0,13,50),(0,13,50)],
        },
    },
    5: {
        "Remo Gironda en polea baja": {
            "MC01":[(1,10,90),(1,12,80),(1,12,80)], "MC02":[(1,12,80),(1,12,70),(1,12,70)],
            "MC03":[(1,12,70),(1,12,70),(1,12,70)], "MC04":[(1,12,70),(1,12,70),(1,12,70)],
        },
        "Jalon al pecho con agarre neutro": {
            "MC01":[(1,12,70),(1,12,70),(0,12,70)], "MC02":[(1,12,70),(1,12,70),(0,12,70)],
            "MC03":[(1,12,70),(1,12,80),(0,10,80)], "MC04":[(1,12,70),(1,12,70),(0,12,70)],
        },
        "Remo unilateral en maquina": {
            "MC01":[(0,12,30),(0,12,30),(0,10,30)], "MC02":[(0,12,25),(0,12,25),(0,12,25)],
            "MC03":[(0,12,30),(0,12,30),(0,10,30)], "MC04":[(0,10,60),(0,10,60),(0,10,60)],
        },
        "Curl martillo con mancuernas": {
            "MC01":[(1,10,12.5),(0,10,12.5),(0,10,12.5)], "MC02":[(1,12,15),(0,12,15),(0,12,15)],
            "MC03":[(1,10,15),(0,10,15),(0,10,15)], "MC04":[(1,10,15),(0,10,15),(0,10,15)],
        },
        "Curl Bayesian en polea": {
            "MC01":[(0,10,20),(0,12,15),(0,12,15)], "MC02":[(0,15,15),(0,13,15),(0,12,15)],
            "MC03":[(0,13,20),(0,13,20),(0,12,20)], "MC04":[(0,15,20),(0,15,20),(0,15,20)],
        },
        "Plancha abdominal lastrada": {
            "MC01":[(0,12,50),(0,12,50),(0,12,50)], "MC02":[(0,12,50),(0,12,50),(0,12,50)],
            "MC03":[(0,12,50),(0,12,50),(0,12,50)], "MC04":[(0,12,50),(0,12,50),(0,12,50)],
        },
    },
    6: {
        "Elevaciones laterales con mancuerna": {
            "MC01":[(0,15,8),(0,15,8),(0,15,8)], "MC02":[(0,15,8),(0,15,8),(0,15,8)],
            "MC03":[(0,14,9.8),(0,14,9.8),(0,14,9.8)], "MC04":[(0,15,10),(0,15,10),(0,15,10)],
        },
        "Elevaciones laterales en polea baja": {
            "MC01":[(0,15,11.5),(0,15,11.5),(0,15,11.5)], "MC02":[(0,15,11.5),(0,15,11.5),(0,15,11.5)],
            "MC03":[(0,15,12),(0,15,12),(0,15,12)], "MC04":[(0,15,12),(0,15,12),(0,15,12)],
        },
        "Elevaciones laterales en polea media": {
            "MC01":[(0,15,20),(0,15,20),(0,15,20)], "MC02":[(0,15,15),(0,15,15),(0,15,15)],
            "MC03":[(0,16,15),(0,16,15),(0,16,15)], "MC04":[(0,16,15),(0,16,15),(0,16,15)],
        },
        "Press inclinado con mancuernas": {
            "MC01":[(0,10,20.7),(0,10,20.7),(0,10,20.7)], "MC02":[(0,10,20),(0,10,20),(0,10,20)],
            "MC03":[(0,10,22),(0,10,22),(0,10,22)], "MC04":[(0,10,22),(0,10,22),(0,10,22)],
        },
        "Press plano convergente en maquina": {
            "MC01":[(0,10,50),(0,10,50),(0,10,50)], "MC02":[(0,10,54),(0,10,54),(0,10,54)],
            "MC03":[(0,10,60),(0,10,60),(0,10,60)], "MC04":[(0,10,60),(0,10,60),(0,10,60)],
        },
        "Cruces en polea de alta a baja": {
            "MC01":[(0,15,30),(0,15,30),(0,15,30)], "MC02":[(0,10,25.3),(0,10,25.3),(0,10,25.3)],
            "MC03":[(0,15,20),(0,15,20),(0,15,20)], "MC04":[(0,15,20),(0,15,20),(0,15,20)],
        },
        "Aperturas en polea baja": {
            "MC01":[(0,12,15),(0,12,15),(0,12,15)], "MC02":[(0,12,15),(0,12,15),(0,12,15)],
            "MC03":[(0,12,20),(0,12,20),(0,12,20)], "MC04":[(0,12,20),(0,12,20),(0,12,20)],
        },
        "Fondos de triceps en maquina": {
            "MC01":[(0,15,80.9),(0,15,80.9),(0,15,80.9)], "MC02":[(0,15,93),(0,15,93),(0,15,93)],
            "MC03":[(0,12,77.5),(0,12,77.5),(0,12,77.5)], "MC04":[(0,12,77.5),(0,12,77.5),(0,12,77.5)],
        },
        "Extension de triceps a una mano en polea": {
            "MC01":[(0,12,20),(0,12,20),(0,12,20)], "MC02":[(0,12,21.1),(0,12,21.1),(0,12,21.1)],
            "MC03":[(0,12,23.9),(0,12,23.9),(0,12,23.9)], "MC04":[(0,12,25),(0,12,25),(0,12,25)],
        },
        "Crunch abdominal en polea": {
            "MC01":[(0,15,58.1),(0,15,58.1),(0,15,58.1)], "MC02":[(0,16,59.9),(0,16,59.9),(0,16,59.9)],
            "MC03":[(0,16,59.9),(0,16,59.9),(0,16,60.4)], "MC04":[(0,16,64.7),(0,16,64.7),(0,16,64.7)],
        },
    },
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


def bootstrap(conn):
    c = conn.cursor()
    for day, exercises in ROUTINE_DATA.items():
        for idx, (name, reps_obj) in enumerate(exercises):
            c.execute("INSERT OR IGNORE INTO exercises (day,name,reps_obj,order_idx) VALUES(?,?,?,?)",
                      (day, name, reps_obj, idx))
    conn.commit()

    for day, exercises in HIST.items():
        for ex_name, mc_data in exercises.items():
            c.execute("SELECT id FROM exercises WHERE day=? AND name LIKE ?",
                      (day, f"%{ex_name[:25]}%"))
            row = c.fetchone()
            if row:
                ex_id = row["id"]
            else:
                c.execute("INSERT INTO exercises(day,name,reps_obj,order_idx) VALUES(?,?,?,?)",
                          (day, ex_name, "10-12", 99))
                conn.commit()
                ex_id = c.lastrowid
            for mc, sets in mc_data.items():
                for s_idx, (rir, reps, kg) in enumerate(sets):
                    c.execute("INSERT INTO workout_sets(exercise_id,microcycle,set_num,reps,kg,rir) VALUES(?,?,?,?,?,?)",
                              (ex_id, mc, s_idx+1, reps, kg, rir))
    conn.commit()

    for row in HIST_MACROS:
        c.execute("INSERT OR IGNORE INTO macros_log(log_date,kcal,protein,carbs,fat) VALUES(?,?,?,?,?)", row)
    for row in HIST_METRICS:
        c.execute("INSERT OR IGNORE INTO body_metrics(metric_date,weight,steps,sleep,bf_pct,notes) VALUES(?,?,?,?,?,?)", row)
    c.execute("INSERT OR REPLACE INTO app_config(key,value) VALUES('bootstrapped','1')")
    conn.commit()


def is_bootstrapped():
    conn = get_conn()
    try:
        row = conn.execute("SELECT value FROM app_config WHERE key='bootstrapped'").fetchone()
        return row is not None and row["value"] == "1"
    except:
        return False
    finally:
        conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_current_mc():
    conn = get_conn()
    row = conn.execute("SELECT value FROM app_config WHERE key='current_mc'").fetchone()
    conn.close()
    return row["value"] if row else "MC05"

def set_current_mc(mc):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO app_config(key,value) VALUES('current_mc',?)", (mc,))
    conn.commit()
    conn.close()

def get_exercises(day):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM exercises WHERE day=? AND active=1 ORDER BY order_idx", (day,)
    ).fetchall()
    conn.close()
    return rows

def get_sets(exercise_id, mc):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM workout_sets WHERE exercise_id=? AND microcycle=? ORDER BY set_num",
        (exercise_id, mc)
    ).fetchall()
    conn.close()
    return rows

def calc_tonelaje(exercise_id, mc):
    conn = get_conn()
    row = conn.execute(
        "SELECT COALESCE(SUM(reps*kg),0) as t FROM workout_sets WHERE exercise_id=? AND microcycle=?",
        (exercise_id, mc)
    ).fetchone()
    conn.close()
    return row["t"] if row else 0

def upsert_set(exercise_id, mc, set_num, reps, kg, rir):
    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM workout_sets WHERE exercise_id=? AND microcycle=? AND set_num=?",
        (exercise_id, mc, set_num)
    ).fetchone()
    if existing:
        conn.execute("UPDATE workout_sets SET reps=?,kg=?,rir=? WHERE id=?",
                     (reps, kg, rir, existing["id"]))
    else:
        conn.execute("INSERT INTO workout_sets(exercise_id,microcycle,set_num,reps,kg,rir) VALUES(?,?,?,?,?,?)",
                     (exercise_id, mc, set_num, reps, kg, rir))
    conn.commit()
    conn.close()

def delete_set(exercise_id, mc, set_num):
    conn = get_conn()
    conn.execute("DELETE FROM workout_sets WHERE exercise_id=? AND microcycle=? AND set_num=?",
                 (exercise_id, mc, set_num))
    conn.commit()
    conn.close()

def add_exercise(day, name, reps_obj):
    conn = get_conn()
    row = conn.execute("SELECT MAX(order_idx) as m FROM exercises WHERE day=?", (day,)).fetchone()
    next_idx = (row["m"] or 0) + 1
    conn.execute("INSERT INTO exercises(day,name,reps_obj,order_idx) VALUES(?,?,?,?)",
                 (day, name, reps_obj, next_idx))
    conn.commit()
    conn.close()

def deactivate_exercise(ex_id):
    conn = get_conn()
    conn.execute("UPDATE exercises SET active=0 WHERE id=?", (ex_id,))
    conn.commit()
    conn.close()

def get_tonelaje_history(day, exercise_name):
    conn = get_conn()
    rows = conn.execute("""
        SELECT ws.microcycle, COALESCE(SUM(ws.reps * ws.kg), 0) as tonelaje
        FROM workout_sets ws
        JOIN exercises e ON ws.exercise_id = e.id
        WHERE e.day=? AND e.name=?
        GROUP BY ws.microcycle
        ORDER BY ws.microcycle
    """, (day, exercise_name)).fetchall()
    conn.close()
    return {r["microcycle"]: r["tonelaje"] for r in rows}

def get_day_tonelaje_by_mc(day):
    conn = get_conn()
    rows = conn.execute("""
        SELECT ws.microcycle, COALESCE(SUM(ws.reps * ws.kg), 0) as tonelaje
        FROM workout_sets ws JOIN exercises e ON ws.exercise_id=e.id
        WHERE e.day=?
        GROUP BY ws.microcycle ORDER BY ws.microcycle
    """, (day,)).fetchall()
    conn.close()
    return {r["microcycle"]: r["tonelaje"] for r in rows}

def get_prev_mc(current_mc):
    num = int(current_mc[2:])
    return f"MC{(num-1):02d}" if num > 1 else None

def get_avg_rir(exercise_id, mc):
    conn = get_conn()
    row = conn.execute(
        "SELECT AVG(rir) as avg_rir FROM workout_sets WHERE exercise_id=? AND microcycle=? AND reps>0",
        (exercise_id, mc)
    ).fetchone()
    conn.close()
    return row["avg_rir"] if row and row["avg_rir"] is not None else None

def estimate_1rm(reps, kg, rir=0):
    effective = reps + rir
    if effective <= 0 or kg <= 0:
        return 0.0
    return round(kg * (1 + effective / 30), 1)

def get_best_set(exercise_id, mc):
    """Returns the set with highest estimated 1RM for a given exercise/mc."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT reps, kg, rir FROM workout_sets WHERE exercise_id=? AND microcycle=? AND reps>0 AND kg>0",
        (exercise_id, mc)
    ).fetchall()
    conn.close()
    if not rows:
        return None
    best = max(rows, key=lambda r: estimate_1rm(r["reps"], r["kg"], r["rir"]))
    return dict(best)

def get_streak():
    conn = get_conn()
    rows = conn.execute("SELECT log_date FROM macros_log ORDER BY log_date DESC").fetchall()
    conn.close()
    if not rows:
        return 0
    today = date.today()
    streak = 0
    for row in rows:
        d = date.fromisoformat(row["log_date"])
        if d == today - timedelta(days=streak):
            streak += 1
        else:
            break
    return streak

def get_weekly_compliance(days=7):
    conn = get_conn()
    rows = conn.execute(
        "SELECT kcal, protein FROM macros_log ORDER BY log_date DESC LIMIT ?", (days,)
    ).fetchall()
    conn.close()
    total = len(rows)
    kcal_ok = sum(1 for r in rows if r["kcal"] >= MACROS_TARGET["kcal"] * 0.9)
    prot_ok = sum(1 for r in rows if r["protein"] >= MACROS_TARGET["protein"] * 0.9)
    return {"total": total, "kcal_ok": kcal_ok, "prot_ok": prot_ok}

def get_rir_trend(exercise_id):
    """Returns list of (mc, avg_rir) sorted by microcycle."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT microcycle, AVG(rir) as avg_rir
        FROM workout_sets WHERE exercise_id=? AND reps>0
        GROUP BY microcycle ORDER BY microcycle
    """, (exercise_id,)).fetchall()
    conn.close()
    return [(r["microcycle"], r["avg_rir"]) for r in rows]

def get_session_note(day, mc):
    conn = get_conn()
    row = conn.execute(
        "SELECT value FROM app_config WHERE key=?", (f"note_day{day}_{mc}",)
    ).fetchone()
    conn.close()
    return row["value"] if row else ""

def save_session_note(day, mc, note):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO app_config(key,value) VALUES(?,?)",
                 (f"note_day{day}_{mc}", note))
    conn.commit()
    conn.close()

def export_all_csv():
    """Returns a dict of DataFrames for CSV export."""
    conn = get_conn()
    sets_df = pd.read_sql_query("""
        SELECT e.day, e.name as ejercicio, ws.microcycle, ws.set_num,
               ws.reps, ws.kg, ws.rir, ROUND(ws.reps*ws.kg,1) as tonelaje_set
        FROM workout_sets ws JOIN exercises e ON ws.exercise_id=e.id
        ORDER BY e.day, ws.microcycle, ws.set_num
    """, conn)
    macros_df = pd.read_sql_query("SELECT * FROM macros_log ORDER BY log_date", conn)
    metrics_df = pd.read_sql_query("SELECT * FROM body_metrics ORDER BY metric_date", conn)
    conn.close()
    return sets_df, macros_df, metrics_df

# ─────────────────────────────────────────────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────
def macro_bar(label, current, target, color):
    pct = min(current / target, 1.0) if target > 0 else 0
    over = current > target
    bar_color = "#e74c3c" if over else color
    st.markdown(f"""
    <div style='margin-bottom:8px'>
      <div style='display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px'>
        <span><b>{label}</b></span>
        <span style='color:{"#e74c3c" if over else "#94a3b8"}'>  {current:.0f} / {target} {" " if over else ""}</span>
      </div>
      <div style='background:#e9ecef;border-radius:8px;height:12px'>
        <div style='background:{bar_color};width:{pct*100:.1f}%;height:12px;border-radius:8px;transition:width 0.3s'></div>
      </div>
    </div>""", unsafe_allow_html=True)


def render_exercise_block(ex, current_mc):
    ex_id  = ex["id"]
    ex_name = ex["name"]
    sets    = get_sets(ex_id, current_mc)
    tonelaje = calc_tonelaje(ex_id, current_mc)
    prev_mc = get_prev_mc(current_mc)
    avg_rir = get_avg_rir(ex_id, current_mc)
    best    = get_best_set(ex_id, current_mc)
    e1rm    = estimate_1rm(best["reps"], best["kg"], best["rir"]) if best else 0

    # RIR color badge
    if avg_rir is None:
        rir_badge = "<span style='color:#8b949e'>RIR —</span>"
    elif avg_rir <= 0.5:
        rir_badge = f"<span style='color:#e74c3c;font-weight:600'>RIR {avg_rir:.1f} ⚠ Fatiga</span>"
    elif avg_rir <= 1.5:
        rir_badge = f"<span style='color:#f39c12;font-weight:600'>RIR {avg_rir:.1f}</span>"
    else:
        rir_badge = f"<span style='color:#27ae60;font-weight:600'>RIR {avg_rir:.1f}</span>"

    label = (f"**{ex_name}** — {ex['reps_obj']}  |  "
             f"Ton: **{tonelaje:,.0f} kg**  |  1RM est: **{e1rm} kg**")

    with st.expander(label):
        # ── Inline prev MC comparison ──
        if prev_mc:
            prev_sets = get_sets(ex_id, prev_mc)
            prev_ton  = calc_tonelaje(ex_id, prev_mc)
            if prev_sets:
                delta_ton = tonelaje - prev_ton
                delta_color = "#27ae60" if delta_ton >= 0 else "#e74c3c"
                delta_sign  = "+" if delta_ton >= 0 else ""
                st.markdown(
                    f"<div style='background:#0d1117;border:1px solid #21262d;border-radius:6px;"
                    f"padding:8px 12px;margin-bottom:10px;font-size:0.82rem;color:#8b949e'>"
                    f"<b style='color:#c9d1d9'>{prev_mc}</b> &nbsp;·&nbsp; Tonelaje: {prev_ton:,.0f} kg"
                    f"&nbsp;&nbsp;<span style='color:{delta_color}'>{delta_sign}{delta_ton:,.0f} kg vs ahora</span>"
                    f"&nbsp;&nbsp;|&nbsp;&nbsp;{rir_badge}</div>",
                    unsafe_allow_html=True
                )

        # ── Set table header ──
        cols = st.columns([0.25, 0.25, 0.2, 0.2, 0.1])
        for h, c in zip(["**RIR**", "**Reps**", "**Kg**", "**Ton.**", ""], cols):
            c.markdown(h)

        existing = {s["set_num"]: s for s in sets}
        n_sets   = max(len(sets), 3)

        for sn in range(1, n_sets + 1):
            s = existing.get(sn, {})
            c0, c1, c2, c3, c4 = st.columns([0.25, 0.25, 0.2, 0.2, 0.1])
            key  = f"{ex_id}_{current_mc}_{sn}"
            rir  = c0.number_input("", value=float(s.get("rir", 1)), min_value=0.0,
                                   max_value=5.0, step=0.5, key=f"rir_{key}",
                                   label_visibility="collapsed")
            reps = c1.number_input("", value=float(s.get("reps", 0)), min_value=0.0,
                                   step=1.0, key=f"reps_{key}",
                                   label_visibility="collapsed")
            kg   = c2.number_input("", value=float(s.get("kg", 0)), min_value=0.0,
                                   step=2.5, key=f"kg_{key}",
                                   label_visibility="collapsed")
            c3.markdown(f"<div style='padding-top:8px'>{reps*kg:,.0f}</div>",
                        unsafe_allow_html=True)
            # Confirmation-safe delete
            del_key = f"del_confirm_{key}"
            if del_key not in st.session_state:
                st.session_state[del_key] = False
            if not st.session_state[del_key]:
                if c4.button("✕", key=f"del_{key}") and sn in existing:
                    st.session_state[del_key] = True
                    st.rerun()
            else:
                if c4.button("OK", key=f"conf_{key}"):
                    delete_set(ex_id, current_mc, sn)
                    st.session_state[del_key] = False
                    st.rerun()
            if reps > 0 and kg > 0:
                upsert_set(ex_id, current_mc, sn, reps, kg, rir)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        c_add, c_del_ex = st.columns(2)
        if c_add.button("+ Añadir serie", key=f"add_set_{ex_id}_{current_mc}"):
            upsert_set(ex_id, current_mc, n_sets + 1, 0, 0, 1)
            st.rerun()
        del_ex_key = f"del_ex_confirm_{ex_id}"
        if del_ex_key not in st.session_state:
            st.session_state[del_ex_key] = False
        if not st.session_state[del_ex_key]:
            if c_del_ex.button("Quitar ejercicio", key=f"del_ex_{ex_id}"):
                st.session_state[del_ex_key] = True
                st.rerun()
        else:
            c_del_ex.warning("Confirmar eliminacion")
            cc1, cc2 = st.columns(2)
            if cc1.button("Si, quitar", key=f"conf_ex_yes_{ex_id}"):
                deactivate_exercise(ex_id)
                st.session_state[del_ex_key] = False
                st.rerun()
            if cc2.button("Cancelar", key=f"conf_ex_no_{ex_id}"):
                st.session_state[del_ex_key] = False
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────────────────────────────────────
def page_dashboard():
    st.title("Inicio")
    current_mc = get_current_mc()

    # ── Racha + Cumplimiento ──
    streak = get_streak()
    compliance = get_weekly_compliance(7)
    total_days = compliance["total"]
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Racha", f"{streak} dias", "dias seguidos con registro")
    s2.metric("Registros esta semana", f"{total_days}/7")
    kcal_pct = int(compliance["kcal_ok"] / total_days * 100) if total_days else 0
    prot_pct = int(compliance["prot_ok"] / total_days * 100) if total_days else 0
    s3.metric("Dias con kcal ok", f"{compliance['kcal_ok']}/{total_days}", f"{kcal_pct}%")
    s4.metric("Dias con proteina ok", f"{compliance['prot_ok']}/{total_days}", f"{prot_pct}%")

    st.markdown("---")

    # ── KPIs hoy ──
    st.subheader("Nutricion de hoy")
    today_str = str(date.today())
    conn = get_conn()
    today_row = conn.execute("SELECT * FROM macros_log WHERE log_date=?", (today_str,)).fetchone()
    conn.close()
    cur = {k: (today_row[k] if today_row else 0) for k in ["kcal","protein","carbs","fat"]}

    k1, k2, k3, k4 = st.columns(4)
    def kpi(col, label, val, target, unit):
        delta = val - target
        col.metric(label, f"{val:.0f} {unit}", f"{delta:+.0f} vs objetivo")
    kpi(k1,"Calorias", cur["kcal"],   MACROS_TARGET["kcal"],   "kcal")
    kpi(k2,"Proteina", cur["protein"],MACROS_TARGET["protein"],"g")
    kpi(k3,"Carbos",   cur["carbs"],  MACROS_TARGET["carbs"],  "g")
    kpi(k4,"Grasa",    cur["fat"],    MACROS_TARGET["fat"],    "g")

    # ── Nutrition insight banner ──
    conn = get_conn()
    last7 = conn.execute(
        "SELECT protein FROM macros_log ORDER BY log_date DESC LIMIT 7"
    ).fetchall()
    conn.close()
    low_prot_days = sum(1 for r in last7 if r["protein"] < MACROS_TARGET["protein"] * 0.85)
    if low_prot_days >= 3:
        st.warning(f"Proteina baja los ultimos {low_prot_days} de 7 dias (< 85% objetivo). Revisa tu ingesta proteica.")
    elif cur["kcal"] > MACROS_TARGET["kcal"] * 1.15:
        st.warning(f"Calorias de hoy superan el objetivo en mas de un 15% ({cur['kcal']:.0f} kcal).")
    elif streak >= 7:
        st.success(f"Racha de {streak} dias. Excelente consistencia en el seguimiento nutricional.")

    st.markdown("---")

    # ── Registrar macros hoy ──
    with st.expander("Registrar lo que has comido hoy", expanded=not bool(today_row)):
        with st.form("macro_form"):
            col_a, col_b, col_c, col_d = st.columns(4)
            kcal    = col_a.number_input("Kcal",        value=float(cur["kcal"]),    step=10.0)
            protein = col_b.number_input("Proteina (g)", value=float(cur["protein"]), step=1.0)
            carbs   = col_c.number_input("Carbos (g)",  value=float(cur["carbs"]),   step=1.0)
            fat     = col_d.number_input("Grasa (g)",   value=float(cur["fat"]),     step=0.5)
            notes   = st.text_input("Notas", value=today_row["notes"] if today_row else "")
            if st.form_submit_button("Guardar"):
                conn = get_conn()
                conn.execute("""INSERT OR REPLACE INTO macros_log(log_date,kcal,protein,carbs,fat,notes)
                                VALUES(?,?,?,?,?,?)""", (today_str, kcal, protein, carbs, fat, notes))
                conn.commit(); conn.close()
                st.success("Guardado correctamente."); st.rerun()

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Macros de hoy")
        macro_bar("Calorias", cur["kcal"],    MACROS_TARGET["kcal"],    "#e67e22")
        macro_bar("Proteina", cur["protein"], MACROS_TARGET["protein"], "#2980b9")
        macro_bar("Carbos",   cur["carbs"],   MACROS_TARGET["carbs"],   "#27ae60")
        macro_bar("Grasa",    cur["fat"],     MACROS_TARGET["fat"],     "#8e44ad")

        # Donut chart
        if any(cur[k] > 0 for k in ["protein","carbs","fat"]):
            fig_donut = go.Figure(go.Pie(
                labels=["Proteina","Carbos","Grasa"],
                values=[cur["protein"]*4, cur["carbs"]*4, cur["fat"]*9],
                hole=0.55,
                marker_colors=["#2980b9","#27ae60","#8e44ad"],
                textinfo="label+percent",
                hovertemplate="%{label}: %{value:.0f} kcal<extra></extra>"
            ))
            fig_donut.update_layout(
                height=220, margin=dict(t=10,b=10,l=10,r=10),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#c9d1d9")
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    with col_right:
        st.subheader("Peso corporal")
        conn = get_conn()
        bm = pd.DataFrame([dict(r) for r in conn.execute(
            "SELECT metric_date, weight, bf_pct FROM body_metrics WHERE weight IS NOT NULL ORDER BY metric_date"
        ).fetchall()])
        conn.close()
        if not bm.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=bm["metric_date"], y=bm["weight"],
                                     mode="lines+markers", name="Peso (kg)",
                                     line=dict(color="#2980b9", width=2)))
            fig.update_layout(
                height=310, margin=dict(t=10,b=20,l=20,r=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#c9d1d9"),
                xaxis=dict(gridcolor="#21262d"), yaxis=dict(title="kg", gridcolor="#21262d")
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Macro trends ──
    st.subheader("Calorias y proteina — ultimas 4 semanas")
    conn = get_conn()
    ml = pd.DataFrame([dict(r) for r in conn.execute(
        "SELECT * FROM macros_log ORDER BY log_date DESC LIMIT 28"
    ).fetchall()])
    conn.close()
    if not ml.empty:
        ml = ml.sort_values("log_date")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=ml["log_date"], y=ml["kcal"],    name="Kcal",    line=dict(color="#e67e22")))
        fig2.add_trace(go.Scatter(x=ml["log_date"], y=ml["protein"]*4, name="Proteina (kcal)", line=dict(color="#2980b9", dash="dot")))
        fig2.add_hline(y=MACROS_TARGET["kcal"], line_dash="dash", line_color="#e67e22", annotation_text="Target Kcal")
        fig2.update_layout(
            height=280, margin=dict(t=10,b=20,l=20,r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c9d1d9"),
            xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig2, use_container_width=True)


def page_day(day):
    abbr, descr = DAY_LABELS[day]
    current_mc = get_current_mc()
    st.title(f"{abbr} — {descr}")

    exercises = get_exercises(day)
    session_ton = sum(calc_tonelaje(e["id"], current_mc) for e in exercises)
    prev_mc = get_prev_mc(current_mc)
    prev_ton = sum(calc_tonelaje(e["id"], prev_mc) for e in exercises) if prev_mc else 0
    delta_ton = session_ton - prev_ton

    m1, m2, m3 = st.columns(3)
    m1.metric("Tonelaje total", f"{session_ton:,.0f} kg",
              f"{delta_ton:+,.0f} kg vs {prev_mc}" if prev_mc else None)
    m2.metric("Ejercicios", f"{len(exercises)}")
    m2.caption(f"Microciclo: **{current_mc}**")

    # Session note
    existing_note = get_session_note(day, current_mc)
    note_val = m3.text_input("Nota de sesion", value=existing_note,
                             key=f"snote_{day}_{current_mc}",
                             placeholder="Como fue el entreno...")
    if note_val != existing_note:
        save_session_note(day, current_mc, note_val)

    st.markdown("---")

    for ex in exercises:
        render_exercise_block(ex, current_mc)

    st.markdown("---")
    with st.expander("Añadir ejercicio nuevo"):
        with st.form(f"add_ex_day{day}"):
            new_name = st.text_input("Nombre del ejercicio")
            new_reps = st.text_input("Reps objetivo", value="10-12")
            if st.form_submit_button("Añadir") and new_name:
                add_exercise(day, new_name, new_reps)
                st.success(f"'{new_name}' añadido."); st.rerun()


def page_progress():
    st.title("Progresion y fuerza")
    current_mc = get_current_mc()
    all_mcs = ["MC01","MC02","MC03","MC04","MC05","MC06","MC07","MC08"]
    dark_layout = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )

    # ── Tonelaje total por día y por MC ──
    st.subheader("Tonelaje por sesion y por ciclo")
    rows = []
    for d in range(1, 7):
        ton_by_mc = get_day_tonelaje_by_mc(d)
        for mc in all_mcs:
            rows.append({"Dia": f"Day {d}", "MC": mc, "Tonelaje": ton_by_mc.get(mc, 0)})
    df = pd.DataFrame(rows)
    df_nonzero = df[df["Tonelaje"] > 0]
    if not df_nonzero.empty:
        fig = px.bar(df_nonzero, x="MC", y="Tonelaje", color="Dia", barmode="group",
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(height=380, margin=dict(t=10,b=20,l=20,r=10), **dark_layout)
        st.plotly_chart(fig, use_container_width=True)

    # ── Progresión por ejercicio + 1RM + RIR ──
    st.subheader("Por ejercicio")
    tab_labels = [f"Day {d}" for d in range(1,7)]
    tabs = st.tabs(tab_labels)

    for ti, day in enumerate(range(1,7)):
        with tabs[ti]:
            conn = get_conn()
            exs = conn.execute(
                "SELECT id, name FROM exercises WHERE day=? AND active=1", (day,)
            ).fetchall()
            conn.close()
            if not exs:
                st.info("Sin datos.")
                continue
            ex_map = {e["name"]: e["id"] for e in exs}
            sel = st.selectbox("Ejercicio", list(ex_map.keys()), key=f"prog_sel_{day}")
            ex_id = ex_map[sel]

            col_ton, col_1rm = st.columns(2)

            # Tonelaje bar chart
            hist = get_tonelaje_history(day, sel)
            with col_ton:
                if hist:
                    mcs_sorted = sorted(hist.keys())
                    vals = [hist[m] for m in mcs_sorted]
                    colors = ["#1f6feb" if m <= "MC04" else "#e74c3c" for m in mcs_sorted]
                    fig2 = go.Figure(go.Bar(
                        x=mcs_sorted, y=vals, marker_color=colors,
                        text=[f"{v:,.0f}" for v in vals], textposition="outside"
                    ))
                    fig2.update_layout(
                        title="Tonelaje por MC", yaxis_title="Reps x Kg",
                        height=300, margin=dict(t=40,b=20,l=20,r=10), **dark_layout
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Sin datos de tonelaje.")

            # 1RM estimated per MC
            with col_1rm:
                conn = get_conn()
                rm_rows = conn.execute("""
                    SELECT ws.microcycle, ws.reps, ws.kg, ws.rir
                    FROM workout_sets ws
                    WHERE ws.exercise_id=? AND ws.reps>0 AND ws.kg>0
                    ORDER BY ws.microcycle, ws.set_num
                """, (ex_id,)).fetchall()
                conn.close()
                rm_by_mc = {}
                for r in rm_rows:
                    mc = r["microcycle"]
                    v  = estimate_1rm(r["reps"], r["kg"], r["rir"])
                    if mc not in rm_by_mc or v > rm_by_mc[mc]:
                        rm_by_mc[mc] = v
                if rm_by_mc:
                    mc_list = sorted(rm_by_mc.keys())
                    fig_rm = go.Figure(go.Scatter(
                        x=mc_list, y=[rm_by_mc[m] for m in mc_list],
                        mode="lines+markers+text",
                        text=[f"{rm_by_mc[m]:.1f}" for m in mc_list],
                        textposition="top center",
                        line=dict(color="#f39c12", width=2),
                        marker=dict(size=8)
                    ))
                    fig_rm.update_layout(
                        title="1RM Estimado (Epley)", yaxis_title="kg",
                        height=300, margin=dict(t=40,b=20,l=20,r=10), **dark_layout
                    )
                    st.plotly_chart(fig_rm, use_container_width=True)
                else:
                    st.info("Sin datos para 1RM.")

            # RIR trend
            rir_data = get_rir_trend(ex_id)
            if len(rir_data) >= 2:
                mcs_r, vals_r = zip(*rir_data)
                fig_rir = go.Figure(go.Scatter(
                    x=mcs_r, y=vals_r, mode="lines+markers",
                    line=dict(color="#27ae60", width=2), marker=dict(size=7),
                    fill="tozeroy", fillcolor="rgba(39,174,96,0.1)"
                ))
                fig_rir.add_hline(y=1, line_dash="dash", line_color="#f39c12",
                                  annotation_text="RIR objetivo")
                fig_rir.update_layout(
                    title="Tendencia RIR promedio", yaxis_title="RIR",
                    height=220, margin=dict(t=40,b=20,l=20,r=10), **dark_layout
                )
                st.plotly_chart(fig_rir, use_container_width=True)

    # ── Biometrics: Peso + BF% + Pasos + Sueño ──
    st.subheader("Peso, BF% y habitos")
    conn = get_conn()
    bm = pd.DataFrame([dict(r) for r in conn.execute(
        "SELECT metric_date,weight,bf_pct,steps,sleep FROM body_metrics ORDER BY metric_date"
    ).fetchall()])
    conn.close()
    if not bm.empty:
        c_body, c_habits = st.columns(2)
        with c_body:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=bm["metric_date"], y=bm["weight"],
                                      mode="lines+markers", name="Peso (kg)",
                                      line=dict(color="#2980b9")))
            fig3.add_trace(go.Scatter(x=bm["metric_date"], y=bm["bf_pct"],
                                      mode="lines+markers", name="BF%",
                                      yaxis="y2", line=dict(color="#e74c3c", dash="dot")))
            fig3.update_layout(
                yaxis=dict(title="Peso (kg)", gridcolor="#21262d"),
                yaxis2=dict(title="BF%", overlaying="y", side="right"),
                height=300, margin=dict(t=10,b=20,l=20,r=60),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#c9d1d9"), legend=dict(bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig3, use_container_width=True)
        with c_habits:
            bm_hab = bm.dropna(subset=["steps","sleep"], how="all")
            if not bm_hab.empty:
                fig4 = go.Figure()
                fig4.add_trace(go.Bar(x=bm_hab["metric_date"], y=bm_hab["steps"],
                                      name="Pasos", marker_color="#1f6feb", yaxis="y"))
                fig4.add_trace(go.Scatter(x=bm_hab["metric_date"], y=bm_hab["sleep"],
                                          name="Sueno (h)", mode="lines+markers",
                                          line=dict(color="#8e44ad"), yaxis="y2"))
                fig4.update_layout(
                    yaxis=dict(title="Pasos", gridcolor="#21262d"),
                    yaxis2=dict(title="h sueno", overlaying="y", side="right"),
                    height=300, margin=dict(t=10,b=20,l=20,r=60),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#c9d1d9"), legend=dict(bgcolor="rgba(0,0,0,0)")
                )
                st.plotly_chart(fig4, use_container_width=True)


def page_settings():
    st.title("Ajustes de la app")
    current_mc = get_current_mc()
    all_mcs = [f"MC{i:02d}" for i in range(1,9)]
    st.subheader("Ciclo activo")
    new_mc = st.selectbox("Selecciona el microciclo en el que estas ahora", all_mcs,
                          index=all_mcs.index(current_mc) if current_mc in all_mcs else 4)
    if new_mc != current_mc:
        set_current_mc(new_mc)
        st.success(f"Cambiado a {new_mc}")
        st.rerun()

    st.markdown("---")
    st.subheader("Peso, pasos y sueno")
    with st.form("body_form"):
        col1, col2, col3, col4 = st.columns(4)
        b_date  = col1.date_input("Fecha", value=date.today())
        b_w     = col2.number_input("Peso (kg)", min_value=0.0, step=0.1)
        b_steps = col3.number_input("Pasos", min_value=0, step=500)
        b_sleep = col4.number_input("Sueno (h)", min_value=0.0, step=0.25)
        b_notes = st.text_input("Notas")
        if st.form_submit_button("Guardar"):
            conn = get_conn()
            conn.execute("""INSERT OR REPLACE INTO body_metrics(metric_date,weight,steps,sleep,notes)
                            VALUES(?,?,?,?,?)""",
                         (str(b_date), b_w, b_steps, b_sleep, b_notes))
            conn.commit(); conn.close()
            st.success("Guardado correctamente.")

    st.markdown("---")
    st.subheader("Ultimas entradas")
    conn = get_conn()
    bm = pd.DataFrame([dict(r) for r in conn.execute(
        "SELECT metric_date,weight,steps,sleep,bf_pct,notes FROM body_metrics ORDER BY metric_date DESC LIMIT 14"
    ).fetchall()])
    conn.close()
    if not bm.empty:
        st.dataframe(bm, use_container_width=True)

    # ── Deload warning ──
    st.markdown("---")
    st.subheader("Como vas con la fatiga")
    conn = get_conn()
    exs_all = conn.execute("SELECT id FROM exercises WHERE active=1").fetchall()
    low_rir_count = sum(
        1 for e in exs_all
        if (get_avg_rir(e["id"], current_mc) or 99) <= 0.5
    )
    conn.close()
    total_ex = len(exs_all) or 1
    fatigue_pct = low_rir_count / total_ex
    if fatigue_pct >= 0.4:
        st.error(
            f"{low_rir_count} de {total_ex} ejercicios tienen RIR promedio <= 0.5 en {current_mc}. "
            "Considera programar una semana de descarga en el proximo microciclo."
        )
    elif fatigue_pct >= 0.2:
        st.warning(
            f"{low_rir_count} ejercicios con RIR bajo en {current_mc}. "
            "Monitoriza la fatiga acumulada."
        )
    else:
        st.success(f"Fatiga bajo control en {current_mc}. RIR general adecuado.")

    st.markdown("---")
    st.subheader("Descargar todos tus datos")
    st.caption("Genera un ZIP con tres archivos CSV: series de entreno, macros y metricas corporales.")
    if st.button("Preparar exportacion"):
        import io, zipfile
        sets_df, macros_df, metrics_df = export_all_csv()
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("entrenos.csv", sets_df.to_csv(index=False))
            zf.writestr("macros.csv",   macros_df.to_csv(index=False))
            zf.writestr("metricas.csv", metrics_df.to_csv(index=False))
        zip_buf.seek(0)
        st.download_button(
            label="Descargar ZIP con todos los datos",
            data=zip_buf,
            file_name=f"training_export_{date.today()}.zip",
            mime="application/zip"
        )

    st.markdown("---")
    st.caption("Zona peligrosa: esto borra y recrea todos los ejercicios historicos desde cero.")
    if st.button("Restaurar datos de ejemplo"):
        conn = get_conn()
        conn.execute("DELETE FROM app_config WHERE key='bootstrapped'")
        conn.commit()
        bootstrap(conn)
        conn.close()
        st.success("Datos restaurados correctamente."); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App background ── */
.stApp {
    background: #0d1117;
    color: #e6edf3;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
[data-testid="stSidebar"] .stMarkdown h2 {
    color: #58a6ff !important;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── Sidebar nav buttons ── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    color: #8b949e !important;
    font-size: 0.875rem;
    font-weight: 500;
    text-align: left;
    padding: 8px 12px;
    margin-bottom: 2px;
    transition: all 0.15s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #21262d;
    border-color: #30363d;
    color: #e6edf3 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #1f6feb;
    border-color: #1f6feb;
    color: #ffffff !important;
}

/* ── Main content headings ── */
h1 {
    font-size: 1.625rem;
    font-weight: 700;
    color: #e6edf3;
    letter-spacing: -0.02em;
    border-bottom: 1px solid #21262d;
    padding-bottom: 0.5rem;
    margin-bottom: 1.25rem;
}
h2 { font-size: 1.125rem; font-weight: 600; color: #c9d1d9; }
h3 { font-size: 0.95rem; font-weight: 500; color: #8b949e; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 16px;
}
[data-testid="stMetricLabel"] { color: #8b949e; font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; }
[data-testid="stMetricValue"] { color: #e6edf3; font-size: 1.5rem; font-weight: 700; }
[data-testid="stMetricDelta"] { font-size: 0.8rem; }

/* ── Expanders ── */
.stExpander {
    background: #161b22;
    border: 1px solid #21262d !important;
    border-radius: 8px;
    margin-bottom: 8px;
}
.stExpander summary {
    font-weight: 500;
    color: #c9d1d9;
    font-size: 0.9rem;
}

/* ── Number inputs ── */
div[data-testid="stNumberInput"] > div > input {
    font-size: 14px;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
}

/* ── Buttons ── */
.stButton > button {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #c9d1d9;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: #30363d;
    border-color: #58a6ff;
    color: #58a6ff;
}

/* ── Divider ── */
hr { border-color: #21262d; margin: 1.25rem 0; }

/* ── Dataframe ── */
.stDataFrame { border: 1px solid #21262d; border-radius: 8px; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: transparent; gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 6px;
    color: #8b949e;
    font-size: 0.85rem;
    font-weight: 500;
    padding: 6px 14px;
}
.stTabs [aria-selected="true"] {
    background: #1f6feb;
    border-color: #1f6feb;
    color: #ffffff;
}

/* ── Selectbox / inputs ── */
.stSelectbox > div, .stTextInput > div > div > input {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
}

/* ── Success / Info alerts ── */
.stAlert { border-radius: 8px; }
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
init_db()
if not is_bootstrapped():
    with st.spinner("Importando datos históricos — primer arranque…"):
        conn = get_conn()
        bootstrap(conn)
        conn.close()
    st.success("Bootstrap completado. Datos importados correctamente.")
    st.rerun()

with st.sidebar:
    st.markdown("""
    <div style='padding:4px 0 12px 0'>
      <div style='font-size:1.05rem;font-weight:700;color:#e6edf3;letter-spacing:-0.01em'>Neil Mesociclo</div>
      <div style='font-size:0.78rem;color:#58a6ff;margin-top:2px'>Seguimiento de entrenamiento</div>
    </div>
    """, unsafe_allow_html=True)

    current_mc = get_current_mc()
    st.markdown(
        f"<div style='background:#1f6feb22;border:1px solid #1f6feb55;border-radius:6px;"
        f"padding:6px 10px;font-size:0.82rem;color:#58a6ff;margin-bottom:12px'>"
        f"Ciclo activo &nbsp; <b style='color:#e6edf3'>{current_mc}</b></div>",
        unsafe_allow_html=True
    )

    # Bloque: Resumen
    st.markdown("<div style='font-size:0.7rem;color:#484f58;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px'>Resumen</div>", unsafe_allow_html=True)
    if st.button("Inicio", key="nav_dashboard", use_container_width=True,
                 type="primary" if st.session_state.get("page") == "dashboard" else "secondary"):
        st.session_state.page = "dashboard"; st.rerun()

    # Bloque: Entrenamientos
    st.markdown("<div style='font-size:0.7rem;color:#484f58;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin:10px 0 4px 0'>Entrenamientos</div>", unsafe_allow_html=True)
    DAY_NAV = [
        ("Domingo  ·  Pierna y Hombro",   "day1"),
        ("Lunes  ·  Espalda y Biceps",     "day2"),
        ("Martes  ·  Pecho y Triceps",     "day3"),
        ("Miercoles  ·  Pierna comp.",     "day4"),
        ("Jueves  ·  Espalda y Biceps",    "day5"),
        ("Viernes  ·  Hombro y Pecho",     "day6"),
    ]
    for label, key in DAY_NAV:
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if st.session_state.get("page") == key else "secondary"):
            st.session_state.page = key; st.rerun()

    # Bloque: Analisis
    st.markdown("<div style='font-size:0.7rem;color:#484f58;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin:10px 0 4px 0'>Analisis</div>", unsafe_allow_html=True)
    if st.button("Progresion y fuerza", key="nav_progress", use_container_width=True,
                 type="primary" if st.session_state.get("page") == "progress" else "secondary"):
        st.session_state.page = "progress"; st.rerun()

    # Bloque: App
    st.markdown("<div style='font-size:0.7rem;color:#484f58;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin:10px 0 4px 0'>App</div>", unsafe_allow_html=True)
    if st.button("Ajustes de la app", key="nav_settings", use_container_width=True,
                 type="primary" if st.session_state.get("page") == "settings" else "secondary"):
        st.session_state.page = "settings"; st.rerun()

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

page = st.session_state.page
if   page == "dashboard": page_dashboard()
elif page == "day1":      page_day(1)
elif page == "day2":      page_day(2)
elif page == "day3":      page_day(3)
elif page == "day4":      page_day(4)
elif page == "day5":      page_day(5)
elif page == "day6":      page_day(6)
elif page == "progress":  page_progress()
elif page == "settings":  page_settings()

