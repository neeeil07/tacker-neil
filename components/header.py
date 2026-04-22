"""
header.py — Inyectar tema CSS global, dark mode y estilos para tablas compactas
"""

import streamlit as st
from utils.constants import COLORS, CSS_DARK_THEME

def apply_theme():
    """Aplicar tema oscuro y CSS global."""
    st.set_page_config(
        page_title="CENTRO DE MANDO · NEIL",
        page_icon="⚙️",  # Sin emoji visual (solo en tab)
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Inyectar CSS
    st.markdown(CSS_DARK_THEME, unsafe_allow_html=True)
    
    # Estilos adicionales para componentes específicos
    st.markdown("""
    <style>
        /* HEADER TITLE */
        h1 {
            color: #ffffff;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 2rem;
        }
        
        h2 {
            color: #34495e;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            border-bottom: 2px solid #34495e;
            padding-bottom: 0.5rem;
        }
        
        h3 {
            color: #95a5a6;
            font-weight: 500;
            font-size: 14px;
        }
        
        /* METRIC CARDS */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            border-radius: 8px;
            padding: 16px;
            border: 1px solid #34495e;
        }
        
        /* EXPANDERS */
        .streamlit-expanderHeader {
            background-color: #34495e !important;
            color: #ffffff !important;
            border: 1px solid #34495e;
            border-radius: 4px;
            padding: 8px 12px !important;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #3d5467 !important;
        }
        
        /* DIVIDER */
        .streamlit-container > hr {
            margin: 1rem 0;
            border: 1px solid #34495e;
        }
        
        /* SELECTBOX / MULTISELECT */
        [data-testid="selectbox"] div div:first-child {
            background-color: #2c3e50;
            color: #ffffff;
        }
        
        /* DATEINPUT */
        [data-testid="dateinput"] input {
            background-color: #121212;
            color: #ffffff;
        }
        
        /* SUCCESS/ERROR MESSAGES */
        .stSuccess {
            background-color: #1a3d3a;
            border: 1px solid #27ae60;
            color: #27ae60;
            border-radius: 4px;
            padding: 12px;
        }
        
        .stError {
            background-color: #3d1a1a;
            border: 1px solid #e74c3c;
            color: #e74c3c;
            border-radius: 4px;
            padding: 12px;
        }
        
        .stWarning {
            background-color: #3d2f1a;
            border: 1px solid #e67e22;
            color: #e67e22;
            border-radius: 4px;
            padding: 12px;
        }
        
        /* SIDEBAR NAVIGATION BUTTONS */
        .nav-button {
            display: block;
            width: 100%;
            padding: 12px 16px;
            margin: 4px 0;
            background-color: #2c3e50;
            color: #95a5a6;
            border: 1px solid #34495e;
            border-radius: 4px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .nav-button:hover {
            background-color: #34495e;
            color: #ffffff;
            border-color: #34495e;
        }
        
        .nav-button.active {
            background-color: #34495e;
            color: #ffffff;
            border: 2px solid #27ae60;
        }
        
        /* COMPACT TABLES */
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            background-color: #1e1e1e;
        }
        
        table thead {
            background-color: #2c3e50;
            color: #ffffff;
            font-weight: 600;
        }
        
        table th {
            padding: 6px 8px;
            text-align: left;
            border: 1px solid #34495e;
        }
        
        table td {
            padding: 6px 8px;
            border: 1px solid #34495e;
            color: #ffffff;
        }
        
        table tbody tr:nth-child(odd) {
            background-color: #1e1e1e;
        }
        
        table tbody tr:nth-child(even) {
            background-color: #252525;
        }
        
        table tbody tr:hover {
            background-color: #2c3e50;
        }
        
        /* INPUT FOCUS */
        input:focus, select:focus, textarea:focus {
            background-color: #2c3e50 !important;
            color: #ffffff !important;
            border: 1px solid #34495e !important;
            outline: none;
        }
        
        /* PROGRESS BARS */
        .stProgress > div > div > div {
            background-color: #34495e;
        }
        
        /* MOBILE RESPONSIVE */
        @media (max-width: 768px) {
            h1 {
                font-size: 20px;
            }
            
            h2 {
                font-size: 16px;
            }
            
            [data-testid="metric-container"] {
                padding: 12px;
                font-size: 14px;
            }
            
            table {
                font-size: 11px;
            }
            
            table th, table td {
                padding: 4px;
            }
            
            .nav-button {
                padding: 8px 12px;
                font-size: 13px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def render_title():
    """Renderizar título principal sin emoji."""
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("### CENTRO DE MANDO")
    with col2:
        st.markdown("<p style='text-align:right; color:#95a5a6; font-size:12px;'>Neil Mesociclo | Professional Grade</p>", unsafe_allow_html=True)
    st.markdown("---")
