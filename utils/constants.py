"""
constants.py — Constantes globales: paleta de colores, etiquetas, macros objetivo
"""

# ─────────────────────────────────────────────────────────────────────────────
# THEME COLORS — Dark Mode Minimalista
# ─────────────────────────────────────────────────────────────────────────────
COLORS = {
    "bg_dark": "#1e1e1e",          # Fondo principal (gris muy oscuro)
    "bg_darker": "#121212",        # Fondo secundario (casi negro)
    "slate_gray": "#2c3e50",       # Gris Pizarra (acentos)
    "white_pure": "#ffffff",       # Blanco puro (texto principal)
    "steel_blue": "#34495e",       # Azul Acero (métricas, highlights)
    "accent_green": "#27ae60",     # Verde (OK, éxito)
    "accent_red": "#e74c3c",       # Rojo (alerta, exceso)
    "accent_orange": "#e67e22",    # Naranja (advertencia)
    "border_light": "#34495e",     # Bordes (azul acero)
    "text_muted": "#95a5a6",       # Texto secundario (gris medio)
}

# ─────────────────────────────────────────────────────────────────────────────
# MACROS & TARGETS
# ─────────────────────────────────────────────────────────────────────────────
MACROS_TARGET = {
    "kcal": 1850,
    "protein": 135,  # gramos
    "fat": 40,       # gramos
    "carbs": 235,    # gramos
}

STEPS_TARGET = {
    "weekday": 10000,  # Lunes-Viernes
    "weekend": 6000,   # Sábado-Domingo
}

# ─────────────────────────────────────────────────────────────────────────────
# TRAINING STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────
DAY_LABELS = {
    1: ("DOM", "Pierna + Hombro + Core"),
    2: ("LUN", "Espalda + Bíceps"),
    3: ("MAR", "Pecho + Hombro + Tríceps + Core"),
    4: ("MIÉ", "Pierna Compuesta + Core"),
    5: ("JUE", "Espalda + Bíceps + Core"),
    6: ("VIE", "Hombro + Pecho + Tríceps + Core"),
}

MICROCYCLES = ["MC01", "MC02", "MC03", "MC04", "MC05", "MC06", "MC07", "MC08"]

# ─────────────────────────────────────────────────────────────────────────────
# ROUTINE DATA — Bootstrap (copiado del app.py original)
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

# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────
SECTIONS = {
    "dashboard": "[DASHBOARD]",
    "training": "[ENTRENAMIENTO]",
    "nutrition": "[NUTRICIÓN & PASOS]",
    "biometrics": "[BIOMETRÍA]",
}

SECTION_ORDER = ["dashboard", "training", "nutrition", "biometrics"]

# ─────────────────────────────────────────────────────────────────────────────
# CSS THEME (será inyectado en components/header.py)
# ─────────────────────────────────────────────────────────────────────────────
CSS_DARK_THEME = """
<style>
    /* GLOBAL THEME */
    :root {
        --bg-dark: #1e1e1e;
        --bg-darker: #121212;
        --slate-gray: #2c3e50;
        --white-pure: #ffffff;
        --steel-blue: #34495e;
        --accent-green: #27ae60;
        --accent-red: #e74c3c;
        --accent-orange: #e67e22;
    }
    
    /* MAIN CONTAINER */
    .main {
        background-color: var(--bg-dark);
        color: var(--white-pure);
    }
    
    /* SIDEBAR */
    .sidebar .sidebar-content {
        background-color: var(--bg-darker);
    }
    
    /* TEXT */
    body, p, span, label, div {
        color: var(--white-pure) !important;
    }
    
    /* BUTTONS */
    .stButton > button {
        background-color: var(--steel-blue);
        color: var(--white-pure);
        border: 1px solid var(--slate-gray);
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: var(--accent-green);
        border-color: var(--accent-green);
    }
    
    /* FULL WIDTH BUTTONS (mobile-friendly) */
    .full-width-btn > button {
        width: 100% !important;
    }
    
    /* INPUT FIELDS */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        background-color: var(--bg-darker);
        color: var(--white-pure);
        border: 1px solid var(--slate-gray);
        border-radius: 4px;
        padding: 8px 12px;
    }
    
    /* TABLES - COMPACT */
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }
    
    th {
        background-color: var(--slate-gray);
        color: var(--white-pure);
        padding: 4px;
        text-align: left;
        font-weight: 600;
    }
    
    td {
        background-color: var(--bg-darker);
        color: var(--white-pure);
        padding: 4px;
        border-bottom: 1px solid var(--steel-blue);
    }
    
    tr:nth-child(even) td {
        background-color: #252525;
    }
    
    /* DIVIDERS */
    hr {
        border-color: var(--steel-blue) !important;
    }
    
    /* EXPANDERS */
    .streamlit-expanderHeader {
        background-color: var(--slate-gray);
        color: var(--white-pure);
    }
    
    /* METRICS */
    [data-testid="metric-container"] {
        background-color: var(--steel-blue);
        border-radius: 8px;
        padding: 12px;
    }
    
    [data-testid="metric-container"] label {
        color: var(--text-muted);
        font-size: 12px;
    }
    
    [data-testid="metric-container"] div {
        color: var(--white-pure);
        font-size: 24px;
        font-weight: 700;
    }
    
    /* MOBILE RESPONSIVE */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            margin: 4px 0;
        }
        
        table {
            font-size: 11px;
        }
        
        th, td {
            padding: 3px;
        }
    }
</style>
"""
