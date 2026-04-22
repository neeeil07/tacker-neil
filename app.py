"""
app.py — Centro de Mando · Neil
Orquestador principal: Supabase, tema oscuro, navegación 4 secciones
"""

import streamlit as st
from components.header import apply_theme, render_title
from components.sidebar import render_sidebar, get_active_section
from pages import dashboard, training, nutrition, biometrics
from utils import excel_loader

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & THEME
# ─────────────────────────────────────────────────────────────────────────────
apply_theme()

# ─────────────────────────────────────────────────────────────────────────────
# BOOTSTRAP (one-time data load)
# ─────────────────────────────────────────────────────────────────────────────
if "bootstrap_done" not in st.session_state:
    with st.spinner("Inicializando aplicación..."):
        try:
            excel_loader.load_excel_if_exists()
            st.session_state.bootstrap_done = True
        except Exception as e:
            st.error(f"Error en bootstrap: {str(e)}")
            st.session_state.bootstrap_done = False

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

# Sidebar navigation
render_sidebar()

# Header
render_title()

# Main content based on active section
active_section = get_active_section()

try:
    if active_section == "dashboard":
        dashboard.render()
    elif active_section == "training":
        training.render()
    elif active_section == "nutrition":
        nutrition.render()
    elif active_section == "biometrics":
        biometrics.render()
    else:
        st.error(f"Sección desconocida: {active_section}")

except Exception as e:
    st.error(f"Error en la aplicación: {str(e)}")
    st.error("Por favor, recarga la página o contacta soporte.")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#95a5a6; font-size:10px;'>"
    "Centro de Mando v2.0 | Supabase | Dark Mode Professional | © 2026"
    "</p>",
    unsafe_allow_html=True
)
