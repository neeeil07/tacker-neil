"""
CENTRO DE MANDO - ARQUITECTURA SUPABASE
Migración completa y refactorización técnica
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
from st_supabase_connection import SupabaseConnection

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN CORE Y CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="CENTRO DE MANDO", layout="wide")

SUPABASE_URL = "https://xjudkbyktndaimkypaze.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhqdWRrYnlrdG5kYWlta3lwYXplIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4NDkwODEsImV4cCI6MjA5MjQyNTA4MX0.52xarCRRTxugUYvTioSipLrMd37c5kUHJAV2YkJqB1g"

MACROS_TARGET = {"kcal": 1850, "protein": 135, "fat": 40, "carbs": 235}

DAY_LABELS = {
    1: ("[ DOM ] PIERNA + HOMBRO + CORE"),
    2: ("[ LUN ] ESPALDA + BICEPS"),
    3: ("[ MAR ] PECHO + HOMBRO + TRICEPS + CORE"),
    4: ("[ MIE ] PIERNA COMPUESTA + CORE"),
    5: ("[ JUE ] ESPALDA + BICEPS + CORE"),
    6: ("[ VIE ] HOMBRO + PECHO + TRICEPS + CORE"),
}

# ─────────────────────────────────────────────────────────────────────────────
# DATA DE BOOTSTRAPPING (HISTÓRICO)
# ─────────────────────────────────────────────────────────────────────────────
ROUTINE_DATA = {
    1: [
        ("Zancadas con mancuernas", "10-12"),
        ("Extension de cuadriceps en maquina", "12-15 + DS"),
        ("Curl femoral tumbado en maquina", "12-15 + DS"),
        ("Elevaciones laterales con mancuerna", "15-20"),
        ("Elevaciones laterales en polea baja", "15-20"),
        ("Elevaciones laterales en polea media", "15-20"),
        ("Press declinado en maquina Smith", "8-12"),
        ("Crunch abdominal en polea", "15-20 + Fallo"),
    ],
    2: [
        ("Jalon al pecho agarre neutro", "10-12"),
        ("Jalon al pecho agarre neutro cerrado", "10-12"),
        ("Jalon al pecho unilateral", "10-12"),
        ("Remo en T", "12-15 + RP"),
        ("Remo Gironda Unilateral", "12-15 + RP"),
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
        ("Aperturas en polea alta a baja", "12-15"),
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
        ("Remo Gironda Unilateral", "12-15"),
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
        ("Fondos en maquina (pecho inferior)", "Al fallo"),
        ("Fondos de triceps en maquina", "10-12 + Fallo"),
        ("Extension de triceps a una mano en polea", "12-15"),
        ("Crunch abdominal en polea", "15-20 + Fallo"),
    ],
}

HIST = {
    1: {
        "Zancadas con mancuernas": {"MC02":[(1,12,15),(1,12,15),(1,12,15)], "MC03":[(1,12,15),(1,12,15),(1,12,15)], "MC04":[(1,12,15),(1,12,15),(1,12,15)]},
        "Extension de cuadriceps en maquina": {"MC02":[(2,12,42.5),(1,12,50),(0,12,42.5)], "MC03":[(2,12,57.5),(1,12,57.5),(0,13,57.5)], "MC04":[(2,12,57.5),(1,12,57.5),(0,12,62.5)]},
        "Curl femoral tumbado en maquina": {"MC02":[(2,10,22.5),(1,10,22.5),(0,10,22.5)], "MC03":[(2,10,22.5),(1,10,22.5),(0,10,22.5)], "MC04":[(2,10,22.5),(1,10,22.5),(0,10,22.5)]},
        "Elevaciones laterales con mancuerna": {"MC02":[(0,15,8),(0,15,8),(0,15,8)], "MC03":[(0,18,9),(0,16,9),(0,16,9)], "MC04":[(0,15,10),(0,15,10),(0,15,10)]},
        "Elevaciones laterales en polea baja": {"MC02":[(0,15,11.5),(0,15,11.5),(0,15,11.5)], "MC03":[(0,15,11.5),(0,15,15),(0,15,15)], "MC04":[(0,15,11.5),(0,15,11.5),(0,15,11.5)]},
        "Elevaciones laterales en polea media": {"MC02":[(0,15,15),(0,15,15),(0,15,15)], "MC03":[(0,12,20),(0,13,17.5),(0,12,17.5)], "MC04":[(0,15,17.5),(0,15,17.5),(0,15,15)]},
        "Crunch abdominal en polea": {"MC02":[(0,18,57.5),(0,16,57.5),(0,17,57.5)], "MC03":[(0,16,57.5),(0,16,57.5),(0,14,57.5)], "MC04":[(0,16,57.5),(0,16,57.5),(0,16,57.5)]},
    },
    2: {
        "Jalon al pecho agarre neutro": {"MC02":[(1,12,70),(1,10,80),(1,10,70)], "MC03":[(1,10,70),(1,10,70),(1,10,70)], "MC04":[(1,12,70),(1,12,70),(1,11,70)]},
        "Remo en maquina con apoyo en el pecho": {"MC02":[(1,10,60),(1,10,60),(1,10,60)], "MC03":[(1,10,60),(1,11,60),(1,10,60)], "MC04":[(1,10,80),(1,10,80),(1,10,80)]},
        "Remo Gironda en polea baja": {"MC02":[(1,10,70),(1,10,80),(0,10,70)], "MC03":[(1,12,80),(1,11,80),(0,10,80)], "MC04":[(1,12,80),(1,12,80),(0,12,80)]},
        "Pull-over con cuerda en polea alta": {"MC02":[(0,12,30),(0,12,30),(0,12,30)], "MC03":[(0,12,30),(0,12,30),(0,11,35)], "MC04":[(0,12,30),(0,12,30),(0,12,30)]},
        "Pajaros para deltoide posterior en maquina": {"MC02":[(1,10,35),(0,10,35),(0,10,35)], "MC03":[(1,12,35),(0,12,35),(0,12,35)], "MC04":[(1,12,35),(0,12,35),(0,12,35)]},
        "Curl Scott en maquina": {"MC02":[(0,12,15),(0,12,15),(0,12,15)], "MC03":[(0,12,15),(0,12,15),(0,12,15)], "MC04":[(0,12,15),(0,12,15),(0,12,15)]},
        "Rueda abdominal": {"MC02":[(0,15,55),(0,15,55),(0,15,55)], "MC03":[(0,12,55),(0,12,55),(0,12,55)], "MC04":[(0,12,55),(0,12,55),(0,12,55)]},
    },
    3: {
        "Press plano en maquina": {"MC02":[(1,10,40),(1,10,40),(1,10,40)], "MC03":[(1,8,60),(1,8,60),(1,7,60)], "MC04":[(1,10,60),(1,8,62.5),(1,8,62.5)]},
        "Press inclinado en multipower": {"MC02":[(1,8,50),(1,8,50),(0,15,50)], "MC03":[(1,8,50),(1,8,50),(0,8,50)], "MC04":[(1,8,60),(1,8,60),(0,8,60)]},
        "Press declinado en maquina": {"MC02":[(1,10,42.5),(1,10,42.5),(1,10,42.5)], "MC03":[(1,12,42.5),(1,10,50),(1,10,50)], "MC04":[(1,12,50),(1,10,50),(1,10,50)]},
        "Aperturas en Pec-Deck": {"MC02":[(1,12,42.5),(0,12,42.5),(0,12,42.5)], "MC03":[(1,12,42.5),(0,12,42.5),(0,12,42.5)], "MC04":[(1,12,42.5),(0,12,42.5),(0,12,42.5)]},
        "Elevaciones laterales con mancuerna": {"MC02":[(0,15,9),(0,15,9),(0,15,9)], "MC03":[(0,15,9),(0,15,9),(0,13,10)], "MC04":[(0,18,9),(0,16,9),(0,16,9)]},
        "Elevaciones laterales en polea baja": {"MC02":[(0,15,11.5),(0,15,11.5),(0,15,11.5)], "MC03":[(0,15,12.5),(0,15,12.5),(0,15,12.5)], "MC04":[(0,15,12.5),(0,15,12.5),(0,15,12.5)]},
        "Elevaciones laterales en polea media": {"MC02":[(0,15,15),(0,15,15),(0,15,15)], "MC03":[(0,15,20),(0,20,15),(0,15,20)], "MC04":[(0,15,20),(0,15,20),(0,15,20)]},
        "Extension de triceps en polea alta": {"MC02":[(0,12,20),(0,13,20),(0,13,20)], "MC03":[(0,12,25),(0,12,25),(0,12,25)], "MC04":[(0,12,25),(0,10,30),(0,10,30)]},
        "Extensiones Katana en polea": {"MC02":[(1,12,15),(0,10,15),(0,10,15)], "MC03":[(1,12,15),(0,12,15),(0,12,15)], "MC04":[(1,12,15),(0,12,15),(0,12,15)]},
        "Crunch abdominal en polea": {"MC02":[(0,16,57.5),(0,14,62.5),(0,14,57.5)], "MC03":[(0,16,57.5),(0,16,57.5),(0,16,57.5)], "MC04":[(0,16,57.5),(0,16,57.5),(0,16,57.5)]},
    },
    4: {
        "Peso muerto rumano con mancuernas": {"MC01":[(1,12,17.5),(1,12,17.5),(1,12,17.5)], "MC02":[(1,12,15),(1,12,15),(1,12,15)], "MC03":[(1,12,15),(1,12,15),(1,12,15)], "MC04":[(1,12,15),(1,12,15),(1,12,15)]},
        "Prensa de piernas inclinada": {"MC01":[(0,12,150),(0,10,150),(0,10,150)], "MC02":[(0,12,150),(0,9,150),(0,10,150)], "MC03":[(0,10,160),(0,10,160),(0,10,160)], "MC04":[(0,12,165),(0,10,185),(0,8,185)]},
        "Extension de cuadriceps en maquina": {"MC01":[(1,12,60),(0,12,60),(0,12,60)], "MC02":[(1,12,60),(0,12,60),(0,12,60)], "MC03":[(1,12,57.5),(0,12,57.5),(0,12,57.5)], "MC04":[(1,12,57.5),(0,12,57.5),(0,12,57.5)]},
        "Curl femoral sentado en maquina": {"MC01":[(1,13,47.5),(1,12,47.5),(0,12,47.5)], "MC02":[(1,12,47.5),(1,12,47.5),(0,12,47.5)], "MC03":[(1,12,42.5),(1,12,42.5),(0,12,42.5)], "MC04":[(1,12,42.5),(1,12,50),(0,12,50)]},
        "Aductores en maquina": {"MC01":[(0,15,35),(0,15,35),(0,13,35)], "MC02":[(0,15,35),(0,15,35),(0,15,35)], "MC03":[(0,12,35),(0,12,35),(0,12,35)], "MC04":[(0,12,42.5),(0,12,42.5),(0,12,42.5)]},
        "Gemelos en prensa": {"MC01":[(0,18,100),(0,18,100),(0,16,100)], "MC02":[(0,18,100),(0,18,100),(0,18,100)], "MC03":[(0,18,100),(0,18,100),(0,18,100)], "MC04":[(0,18,100),(0,18,100),(0,18,100)]},
        "Elevaciones de piernas tumbado": {"MC01":[(0,12,50),(0,12,50),(0,12,50)], "MC02":[(0,13,50),(0,13,50),(0,14,50)], "MC03":[(0,13,50),(0,13,50),(0,13,50)], "MC04":[(0,13,50),(0,13,50),(0,13,50)]},
    },
    5: {
        "Remo Gironda en polea baja": {"MC01":[(1,10,90),(1,12,80),(1,12,80)], "MC02":[(1,12,80),(1,12,70),(1,12,70)], "MC03":[(1,12,70),(1,12,70),(1,12,70)], "MC04":[(1,12,70),(1,12,70),(1,12,70)]},
        "Jalon al pecho con agarre neutro": {"MC01":[(1,12,70),(1,12,70),(0,12,70)], "MC02":[(1,12,70),(1,12,70),(0,12,70)], "MC03":[(1,12,70),(1,12,80),(0,10,80)], "MC04":[(1,12,70),(1,12,70),(0,12,70)]},
        "Remo unilateral en maquina": {"MC01":[(0,12,30),(0,12,30),(0,10,30)], "MC02":[(0,12,25),(0,12,25),(0,12,25)], "MC03":[(0,12,30),(0,12,30),(0,10,30)], "MC04":[(0,10,60),(0,10,60),(0,10,60)]},
        "Curl martillo con mancuernas": {"MC01":[(1,10,12.5),(0,10,12.5),(0,10,12.5)], "MC02":[(1,12,15),(0,12,15),(0,12,15)], "MC03":[(1,10,15),(0,10,15),(0,10,15)], "MC04":[(1,10,15),(0,10,15),(0,10,15)]},
        "Curl Bayesian en polea": {"MC01":[(0,10,20),(0,12,15),(0,12,15)], "MC02":[(0,15,15),(0,13,15),(0,12,15)], "MC03":[(0,13,20),(0,13,20),(0,12,20)], "MC04":[(0,15,20),(0,15,20),(0,15,20)]},
        "Plancha abdominal lastrada": {"MC01":[(0,12,50),(0,12,50),(0,12,50)], "MC02":[(0,12,50),(0,12,50),(0,12,50)], "MC03":[(0,12,50),(0,12,50),(0,12,50)], "MC04":[(0,12,50),(0,12,50),(0,12,50)]},
    },
    6: {
        "Elevaciones laterales con mancuerna": {"MC01":[(0,15,8),(0,15,8),(0,15,8)], "MC02":[(0,15,8),(0,15,8),(0,15,8)], "MC03":[(0,14,9.8),(0,14,9.8),(0,14,9.8)], "MC04":[(0,15,10),(0,15,10),(0,15,10)]},
        "Elevaciones laterales en polea baja": {"MC01":[(0,15,11.5),(0,15,11.5),(0,15,11.5)], "MC02":[(0,15,11.5),(0,15,11.5),(0,15,11.5)], "MC03":[(0,15,12),(0,15,12),(0,15,12)], "MC04":[(0,15,12),(0,15,12),(0,15,12)]},
        "Elevaciones laterales en polea media": {"MC01":[(0,15,20),(0,15,20),(0,15,20)], "MC02":[(0,15,15),(0,15,15),(0,15,15)], "MC03":[(0,16,15),(0,16,15),(0,16,15)], "MC04":[(0,16,15),(0,16,15),(0,16,15)]},
        "Press inclinado con mancuernas": {"MC01":[(0,10,20.7),(0,10,20.7),(0,10,20.7)], "MC02":[(0,10,20),(0,10,20),(0,10,20)], "MC03":[(0,10,22),(0,10,22),(0,10,22)], "MC04":[(0,10,22),(0,10,22),(0,10,22)]},
        "Press plano convergente en maquina": {"MC01":[(0,10,50),(0,10,50),(0,10,50)], "MC02":[(0,10,54),(0,10,54),(0,10,54)], "MC03":[(0,10,60),(0,10,60),(0,10,60)], "MC04":[(0,10,60),(0,10,60),(0,10,60)]},
        "Cruces en polea de alta a baja": {"MC01":[(0,15,30),(0,15,30),(0,15,30)], "MC02":[(0,10,25.3),(0,10,25.3),(0,10,25.3)], "MC03":[(0,15,20),(0,15,20),(0,15,20)], "MC04":[(0,15,20),(0,15,20),(0,15,20)]},
        "Aperturas en polea baja": {"MC01":[(0,12,15),(0,12,15),(0,12,15)], "MC02":[(0,12,15),(0,12,15),(0,12,15)], "MC03":[(0,12,20),(0,12,20),(0,12,20)], "MC04":[(0,12,20),(0,12,20),(0,12,20)]},
        "Fondos de triceps en maquina": {"MC01":[(0,15,80.9),(0,15,80.9),(0,15,80.9)], "MC02":[(0,15,93),(0,15,93),(0,15,93)], "MC03":[(0,12,77.5),(0,12,77.5),(0,12,77.5)], "MC04":[(0,12,77.5),(0,12,77.5),(0,12,77.5)]},
        "Extension de triceps a una mano en polea": {"MC01":[(0,12,20),(0,12,20),(0,12,20)], "MC02":[(0,12,21.1),(0,12,21.1),(0,12,21.1)], "MC03":[(0,12,23.9),(0,12,23.9),(0,12,23.9)], "MC04":[(0,12,25),(0,12,25),(0,12,25)]},
        "Crunch abdominal en polea": {"MC01":[(0,15,58.1),(0,15,58.1),(0,15,58.1)], "MC02":[(0,16,59.9),(0,16,59.9),(0,16,59.9)], "MC03":[(0,16,59.9),(0,16,59.9),(0,16,60.4)], "MC04":[(0,16,64.7),(0,16,64.7),(0,16,64.7)]},
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
    ("2026-03-27",53.9,11510,7.0,12.4,""), ("2026-03-28",54.0,0,8.0,12.6,"Res day"),
    ("2026-03-29",53.8,6319,7.0,12.2,""),  ("2026-03-30",52.9,12425,10.0,10.5,""),
    ("2026-03-31",52.6,6667,8.0,10.0,""),  ("2026-04-01",52.0,12433,8.0,8.8,""),
    ("2026-04-02",52.7,8827,10.0,10.1,""), ("2026-04-03",53.2,4649,8.0,11.1,""),
    ("2026-04-04",52.7,7953,6.0,10.1,""),  ("2026-04-05",53.2,5907,6.0,11.1,""),
    ("2026-04-06",53.4,6772,6.0,11.4,""),  ("2026-04-07",53.3,16689,3.59,11.3,""),
    ("2026-04-08",52.8,14624,7.11,10.3,""),("2026-04-09",53.2,15977,6.52,11.1,""),
    ("2026-04-10",52.9,9050,7.32,10.5,""), ("2026-04-11",53.3,14982,7.12,11.3,""),
    ("2026-04-12",53.3,10767,7.12,11.3,""),("2026-04-13",53.4,14982,7.48,11.4,""),
    ("2026-04-14",53.0,16791,6.5,10.7,""), ("2026-04-15",52.8,14303,6.58,10.3,""),
    ("2026-04-16",52.8,0,0,10.3,""), ("2026-04-17",52.8,0,0,10.3,""),
    ("2026-04-18",52.8,0,0,10.3,""), ("2026-04-19",52.8,0,0,10.3,""),
    ("2026-04-20",53.3,0,0,11.3,""), ("2026-04-21",53.4,0,0,11.4,""),
]

# ─────────────────────────────────────────────────────────────────────────────
# CSS INJECT (DARK MODE & UI TÉCNICA MINIMALISTA)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Gris Pizarra (#2F4F4F), Blanco Puro (#FFFFFF), Azul Acero (#4682B4) */
    :root {
        --bg-color: #121212;
        --panel-bg: #1A1A1A;
        --border-color: #2F4F4F;
        --text-color: #FFFFFF;
        --accent-color: #4682B4;
    }
    .stApp { background-color: var(--bg-color); color: var(--text-color); }
    [data-testid="stSidebar"] { background-color: var(--panel-bg); border-right: 1px solid var(--border-color); }
    [data-testid="stSidebar"] * { color: var(--text-color) !important; font-family: 'Courier New', Courier, monospace; }
    
    .stButton>button {
        width: 100%;
        background-color: var(--panel-bg);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { border-color: var(--accent-color); color: var(--accent-color); }
    .stExpander { border: 1px solid var(--border-color); border-radius: 4px; margin-bottom: 8px; background: var(--panel-bg); }
    .stMetric { background: var(--panel-bg); border: 1px solid var(--border-color); border-radius: 4px; padding: 12px; }
    div[data-baseweb="input"] > div { background-color: var(--bg-color); border: 1px solid var(--border-color); }
    
    /* Ocultar iconos nativos */
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_ { display: none !important; }
    
    h1, h2, h3 {
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE (SUPABASE)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def init_connection():
    return st.connection("supabase", type=SupabaseConnection, url=SUPABASE_URL, key=SUPABASE_KEY)

conn = init_connection()

def is_bootstrapped():
    res = conn.table("app_config").select("value").eq("key", "bootstrapped").execute()
    return len(res.data) > 0 and res.data[0]["value"] == "1"

def bootstrap():
    # Insertar Rutinas
    for day, exercises in ROUTINE_DATA.items():
        for idx, (name, reps_obj) in enumerate(exercises):
            conn.table("exercises").upsert({
                "day": day, "name": name, "reps_obj": reps_obj, "order_idx": idx, "active": 1
            }).execute()
            
    # Insertar Histórico de Sets
    for day, exercises in HIST.items():
        for ex_name, mc_data in exercises.items():
            # Buscar el ID del ejercicio
            res_ex = conn.table("exercises").select("id").eq("day", day).ilike("name", f"%{ex_name[:25]}%").execute()
            if res_ex.data:
                ex_id = res_ex.data[0]["id"]
            else:
                res_ins = conn.table("exercises").insert({"day": day, "name": ex_name, "reps_obj": "10-12", "order_idx": 99}).execute()
                ex_id = res_ins.data[0]["id"]
            
            for mc, sets in mc_data.items():
                for s_idx, (rir, reps, kg) in enumerate(sets):
                    conn.table("workout_sets").insert({
                        "exercise_id": ex_id, "microcycle": mc, "set_num": s_idx+1, "reps": reps, "kg": kg, "rir": rir
                    }).execute()

    # Insertar Histórico Macros
    for row in HIST_MACROS:
        conn.table("macros_log").upsert({
            "log_date": row[0], "kcal": row[1], "protein": row[2], "carbs": row[3], "fat": row[4]
        }).execute()
        
    # Insertar Histórico Métricas
    for row in HIST_METRICS:
        conn.table("body_metrics").upsert({
            "metric_date": row[0], "weight": row[1], "steps": row[2], "sleep": row[3], "bf_pct": row[4], "notes": row[5]
        }).execute()

    conn.table("app_config").upsert({"key": "bootstrapped", "value": "1"}).execute()

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_current_mc():
    res = conn.table("app_config").select("value").eq("key", "current_mc").execute()
    return res.data[0]["value"] if res.data else "MC05"

def set_current_mc(mc):
    conn.table("app_config").upsert({"key": "current_mc", "value": mc}).execute()

def get_exercises(day):
    res = conn.table("exercises").select("*").eq("day", day).eq("active", 1).order("order_idx").execute()
    return res.data

def get_sets(exercise_id, mc):
    res = conn.table("workout_sets").select("*").eq("exercise_id", exercise_id).eq("microcycle", mc).order("set_num").execute()
    return res.data

def calc_tonelaje(exercise_id, mc):
    res = conn.table("workout_sets").select("reps, kg").eq("exercise_id", exercise_id).eq("microcycle", mc).execute()
    return sum(row["reps"] * row["kg"] for row in res.data) if res.data else 0

def upsert_set(exercise_id, mc, set_num, reps, kg, rir):
    res = conn.table("workout_sets").select("id").eq("exercise_id", exercise_id).eq("microcycle", mc).eq("set_num", set_num).execute()
    if res.data:
        conn.table("workout_sets").update({"reps": reps, "kg": kg, "rir": rir}).eq("id", res.data[0]["id"]).execute()
    else:
        conn.table("workout_sets").insert({"exercise_id": exercise_id, "microcycle": mc, "set_num": set_num, "reps": reps, "kg": kg, "rir": rir}).execute()

def delete_set(exercise_id, mc, set_num):
    conn.table("workout_sets").delete().eq("exercise_id", exercise_id).eq("microcycle", mc).eq("set_num", set_num).execute()

def get_all_tonelaje_history(day):
    exs = get_exercises(day)
    ex_ids = [e["id"] for e in exs]
    if not ex_ids: return {}
    
    res = conn.table("workout_sets").select("exercise_id, microcycle, reps, kg").in_("exercise_id", ex_ids).execute()
    df = pd.DataFrame(res.data)
    if df.empty: return {}
    
    df["tonelaje"] = df["reps"] * df["kg"]
    grouped = df.groupby("microcycle")["tonelaje"].sum().to_dict()
    return grouped

def get_exercise_tonelaje_history(ex_id):
    res = conn.table("workout_sets").select("microcycle, reps, kg").eq("exercise_id", ex_id).execute()
    df = pd.DataFrame(res.data)
    if df.empty: return {}
    
    df["tonelaje"] = df["reps"] * df["kg"]
    grouped = df.groupby("microcycle")["tonelaje"].sum().to_dict()
    return grouped

# ─────────────────────────────────────────────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────
def macro_bar(label, current, target, color):
    pct = min(current / target, 1.0) if target > 0 else 0
    over = current > target
    bar_color = "#e74c3c" if over else color
    st.markdown(f"""
    <div style='margin-bottom:8px'>
      <div style='display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px;font-family:monospace'>
        <span><b>{label.upper()}</b></span>
        <span style='color:{"#e74c3c" if over else "var(--text-color)"}'>{current:.0f} / {target}</span>
      </div>
      <div style='background:var(--border-color);border-radius:4px;height:12px'>
        <div style='background:{bar_color};width:{pct*100:.1f}%;height:12px;border-radius:4px;transition:width 0.3s'></div>
      </div>
    </div>""", unsafe_allow_html=True)

def render_exercise_block(ex, current_mc):
    ex_id = ex["id"]
    ex_name = ex["name"].upper()
    sets = get_sets(ex_id, current_mc)
    tonelaje = calc_tonelaje(ex_id, current_mc)

    with st.expander(f"[ {ex_name} ] | {ex['reps_obj']} | VOLUMEN: {tonelaje:,.0f} KG"):
        cols = st.columns([0.3, 0.3, 0.2, 0.2, 0.1])
        cols[0].markdown("**RIR**")
        cols[1].markdown("**REPS**")
        cols[2].markdown("**KG**")
        cols[3].markdown("**TON**")
        cols[4].markdown("**ACT**")

        existing = {s["set_num"]: s for s in sets}
        n_sets = max(len(sets), 3)

        for sn in range(1, n_sets + 1):
            s = existing.get(sn, {})
            c0, c1, c2, c3, c4 = st.columns([0.3, 0.3, 0.2, 0.2, 0.1])
            key = f"{ex_id}_{current_mc}_{sn}"
            rir  = c0.number_input("", value=float(s.get("rir",1)), min_value=0.0, max_value=5.0, step=0.5, key=f"rir_{key}", label_visibility="collapsed")
            reps = c1.number_input("", value=float(s.get("reps",0)), min_value=0.0, step=1.0,  key=f"reps_{key}", label_visibility="collapsed")
            kg   = c2.number_input("", value=float(s.get("kg",0)),  min_value=0.0, step=2.5,  key=f"kg_{key}",   label_visibility="collapsed")
            c3.markdown(f"<div style='padding-top:8px;font-family:monospace'>{reps*kg:,.0f}</div>", unsafe_allow_html=True)
            if c4.button("DEL", key=f"del_{key}") and sn in existing:
                delete_set(ex_id, current_mc, sn)
                st.rerun()
            if reps > 0 and kg > 0:
                upsert_set(ex_id, current_mc, sn, reps, kg, rir)

        if st.button(f"REGISTRAR NUEVA SERIE", key=f"add_set_{ex_id}_{current_mc}"):
            upsert_set(ex_id, current_mc, n_sets + 1, 0, 0, 1)
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────────────────────────────────────
def page_dashboard():
    st.markdown("## RESUMEN DE SISTEMA")
    current_mc = get_current_mc()

    # ── KPIs de Hoy ──
    today_str = str(date.today())
    res_macros = conn.table("macros_log").select("*").eq("log_date", today_str).execute()
    cur = res_macros.data[0] if res_macros.data else {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0}

    k1, k2, k3, k4 = st.columns(4)
    def kpi(col, label, val, target, unit):
        delta = val - target
        col.metric(f"{label}", f"{val:.0f} {unit}", f"{delta:+.0f} vs target")
        
    kpi(k1, "CALORIAS", cur["kcal"], MACROS_TARGET["kcal"], "KCAL")
    kpi(k2, "PROTEINA", cur["protein"], MACROS_TARGET["protein"], "G")
    kpi(k3, "CARBOS", cur["carbs"], MACROS_TARGET["carbs"], "G")
    kpi(k4, "GRASA", cur["fat"], MACROS_TARGET["fat"], "G")

    st.markdown("---")
    
    col_bars, col_prog = st.columns([1, 1])
    with col_bars:
        st.markdown("### STATUS METABOLICO (HOY)")
        macro_bar("KCAL", cur["kcal"], MACROS_TARGET["kcal"], "#4682B4")
        macro_bar("PROT", cur["protein"], MACROS_TARGET["protein"], "#4682B4")
        macro_bar("CARB", cur["carbs"], MACROS_TARGET["carbs"], "#4682B4")
        macro_bar("GRAS", cur["fat"], MACROS_TARGET["fat"], "#4682B4")

    with col_prog:
        st.markdown("### VOLUMEN DE ENTRENAMIENTO (TONELAJE)")
        all_mcs = ["MC01","MC02","MC03","MC04","MC05","MC06","MC07","MC08"]
        rows = []
        for d in range(1, 7):
            ton_by_mc = get_all_tonelaje_history(d)
            for mc in all_mcs:
                rows.append({"DAY": f"D{d}", "MC": mc, "TON": ton_by_mc.get(mc, 0)})
        
        df_ton = pd.DataFrame(rows)
        df_nonzero = df_ton[df_ton["TON"] > 0]
        if not df_nonzero.empty:
            fig = px.bar(df_nonzero, x="MC", y="TON", color="DAY", barmode="group")
            fig.update_layout(
                height=250, margin=dict(t=10,b=10,l=10,r=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FFFFFF", family="Courier New")
            )
            st.plotly_chart(fig, use_container_width=True)

def page_entrenamiento():
    st.markdown("## REGISTRO DE ENTRENAMIENTO")
    current_mc = get_current_mc()
    
    selected_day = st.selectbox("SELECCIONAR MODULO DIARIO", options=list(DAY_LABELS.keys()), format_func=lambda x: DAY_LABELS[x])
    
    exercises = get_exercises(selected_day)
    session_ton = sum(calc_tonelaje(e["id"], current_mc) for e in exercises)
    
    st.markdown("---")
    col_t1, col_t2 = st.columns(2)
    col_t1.metric("VOLUMEN SESION", f"{session_ton:,.0f} KG")
    col_t2.metric("MICROCICLO ACTIVO", current_mc)
    st.markdown("---")

    for ex in exercises:
        render_exercise_block(ex, current_mc)

def page_nutricion():
    st.markdown("## MONITOREO METABOLICO Y ACTIVIDAD")
    
    log_date = st.date_input("FECHA DE REGISTRO", date.today())
    date_str = str(log_date)
    
    res = conn.table("macros_log").select("*").eq("log_date", date_str).execute()
    cur = res.data[0] if res.data else {"kcal": MACROS_TARGET["kcal"], "protein": MACROS_TARGET["protein"], "carbs": MACROS_TARGET["carbs"], "fat": MACROS_TARGET["fat"], "notes": ""}
    
    res_bio = conn.table("body_metrics").select("steps").eq("metric_date", date_str).execute()
    cur_steps = res_bio.data[0]["steps"] if res_bio.data and res_bio.data[0].get("steps") else 0
    
    day_of_week = log_date.weekday()
    target_steps = 10000 if day_of_week < 5 else 6000

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### INGESTA MACROS")
        kcal = st.number_input("KCAL", value=float(cur["kcal"]), step=10.0)
        protein = st.number_input("PROTEINA (G)", value=float(cur["protein"]), step=1.0)
        carbs = st.number_input("CARBOS (G)", value=float(cur["carbs"]), step=1.0)
        fat = st.number_input("GRASA (G)", value=float(cur["fat"]), step=0.5)
        
    with col2:
        st.markdown("### GASTO Y ACTIVIDAD")
        st.info(f"TARGET PASOS: {target_steps}")
        steps = st.number_input("PASOS TOTALES", value=float(cur_steps), min_value=0.0, step=500.0)
        notes = st.text_input("NOTAS DIARIAS", value=cur["notes"])
        
    if st.button("ACTUALIZAR DATOS METABOLICOS"):
        conn.table("macros_log").upsert({
            "log_date": date_str, "kcal": kcal, "protein": protein, "carbs": carbs, "fat": fat, "notes": notes
        }).execute()
        conn.table("body_metrics").upsert({
            "metric_date": date_str, "steps": steps
        }).execute()
        st.success("SISTEMA ACTUALIZADO.")

def page_biometria():
    st.markdown("## SEGUIMIENTO CORPORAL")
    
    col_input, col_chart = st.columns([1, 2])
    
    with col_input:
        log_date = st.date_input("FECHA", date.today(), key="bio_date")
        date_str = str(log_date)
        
        res = conn.table("body_metrics").select("*").eq("metric_date", date_str).execute()
        cur = res.data[0] if res.data else {"weight": 53.0, "bf_pct": 11.0, "sleep": 7.0}
        
        weight = st.number_input("PESO (KG)", value=float(cur.get("weight") or 53.0), step=0.1)
        bf = st.number_input("BF (%)", value=float(cur.get("bf_pct") or 11.0), step=0.1)
        sleep = st.number_input("SUEÑO (H)", value=float(cur.get("sleep") or 7.0), step=0.5)
        
        if st.button("ACTUALIZAR METRICAS"):
            conn.table("body_metrics").upsert({
                "metric_date": date_str, "weight": weight, "bf_pct": bf, "sleep": sleep
            }).execute()
            st.success("METRICAS GUARDADAS.")

    with col_chart:
        res_all = conn.table("body_metrics").select("metric_date, weight, bf_pct").not_.is_("weight", "null").order("metric_date").execute()
        bm = pd.DataFrame(res_all.data)
        if not bm.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=bm["metric_date"], y=bm["weight"], mode="lines+markers", name="PESO (KG)", line=dict(color="#4682B4")))
            fig.add_trace(go.Scatter(x=bm["metric_date"], y=bm["bf_pct"], mode="lines+markers", name="BF %", yaxis="y2", line=dict(color="#FFFFFF", dash="dot")))
            fig.update_layout(
                yaxis=dict(title="PESO (KG)", gridcolor="#2F4F4F"),
                yaxis2=dict(title="BF %", overlaying="y", side="right"),
                height=350, margin=dict(t=10,b=10,l=10,r=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FFFFFF", family="Courier New")
            )
            st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONTROL DE NAVEGACION Y ESTADO GLOBAL (CORREGIDO)
# ─────────────────────────────────────────────────────────────────────────────
# 1. INICIALIZACIÓN GLOBAL DEL ESTADO (Obligatorio antes del Sidebar)
if "page" not in st.session_state:
    st.session_state.page = "[ DASHBOARD ]"

# 2. BOOTSTRAP DE DATOS
if not is_bootstrapped():
    with st.spinner("INICIANDO BOOTSTRAP HACIA SUPABASE..."):
        bootstrap()
    st.rerun()

# 3. SIDEBAR Y CONTROLES LATERALES
with st.sidebar:
    st.markdown("### PANEL DE NAVEGACION")
    
    current_mc = get_current_mc()
    all_mcs = [f"MC{i:02d}" for i in range(1,9)]
    new_mc = st.selectbox("MICROCICLO ACTIVO", all_mcs, index=all_mcs.index(current_mc) if current_mc in all_mcs else 4)
    if new_mc != current_mc:
        set_current_mc(new_mc)
        st.rerun()
        
    st.markdown("---")
        
    SECTIONS = ["[ DASHBOARD ]", "[ ENTRENAMIENTO ]", "[ NUTRICION & PASOS ]", "[ BIOMETRIA ]"]
    
    for section in SECTIONS:
        if st.button(section, use_container_width=True):
            st.session_state.page = section
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ENRUTAMIENTO DE PÁGINAS
# ─────────────────────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "[ DASHBOARD ]": page_dashboard()
elif page == "[ ENTRENAMIENTO ]": page_entrenamiento()
elif page == "[ NUTRICION & PASOS ]": page_nutricion()
elif page == "[ BIOMETRIA ]": page_biometria()