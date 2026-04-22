"""
sidebar.py — Navegación de 4 secciones principales (DASHBOARD, ENTRENAMIENTO, NUTRICIÓN & PASOS, BIOMETRÍA)
"""

import streamlit as st
from utils.constants import SECTIONS, SECTION_ORDER, MICROCYCLES
from utils import database as db

def render_sidebar():
    """Renderizar sidebar con 4 botones de navegación y footer de MC."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Navegación")
        st.markdown("---")
        
        # Inicializar session_state si no existe
        if "active_section" not in st.session_state:
            st.session_state.active_section = "dashboard"
        
        # Botones de navegación
        for section_key in SECTION_ORDER:
            section_label = SECTIONS[section_key]
            is_active = st.session_state.active_section == section_key
            
            # Botón personalizado con estilos
            button_style = "active" if is_active else ""
            if st.button(
                section_label,
                key=f"nav_{section_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.active_section = section_key
                st.rerun()
        
        st.markdown("---")
        
        # Footer: Microciclo selector
        st.markdown("### Configuración")
        current_mc = db.get_current_mc()
        new_mc = st.selectbox(
            "Microciclo Activo",
            MICROCYCLES,
            index=MICROCYCLES.index(current_mc),
            label_visibility="collapsed",
            key="mc_selector"
        )
        
        if new_mc != current_mc:
            db.set_current_mc(new_mc)
            st.success(f"Microciclo cambiado a {new_mc}")
            st.rerun()
        
        # Información de versión
        st.markdown("---")
        st.markdown(
            "<p style='text-align:center; color:#95a5a6; font-size:11px;'>"
            "v2.0 | Supabase | Dark Mode"
            "</p>",
            unsafe_allow_html=True
        )

def get_active_section():
    """Obtener sección activa desde session_state."""
    if "active_section" not in st.session_state:
        st.session_state.active_section = "dashboard"
    return st.session_state.active_section
