"""
pages/dashboard.py — Dashboard: KPIs nutricionales, gráficos, registro rápido
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import pandas as pd
from utils.constants import COLORS, MACROS_TARGET
from utils import database as db
from utils import calculations as calc

def render():
    """Renderizar dashboard."""
    st.markdown("## DASHBOARD")
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 1: KPI METRICS
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Nutrición Diaria")
    
    macros_status = calc.get_macro_vs_target()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        kcal_status = "✓" if macros_status["kcal"]["status"] == "ok" else "⚠"
        st.metric(
            "Kcal",
            f"{macros_status['kcal']['current']:.0f}",
            f"{macros_status['kcal']['pct']:.0f}% de {MACROS_TARGET['kcal']}",
        )
    
    with col2:
        st.metric(
            "Proteína",
            f"{macros_status['protein']['current']:.0f}g",
            f"{macros_status['protein']['pct']:.0f}% de {MACROS_TARGET['protein']}g",
        )
    
    with col3:
        st.metric(
            "Carbos",
            f"{macros_status['carbs']['current']:.0f}g",
            f"{macros_status['carbs']['pct']:.0f}% de {MACROS_TARGET['carbs']}g",
        )
    
    with col4:
        st.metric(
            "Grasas",
            f"{macros_status['fat']['current']:.0f}g",
            f"{macros_status['fat']['pct']:.0f}% de {MACROS_TARGET['fat']}g",
        )
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 2: QUICK MACRO REGISTRATION
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Registrar Hoy")
    
    with st.expander("Cargar Macros Diarias", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            kcal_input = st.number_input("Kcal", min_value=0.0, step=10.0, key="kcal_input")
            protein_input = st.number_input("Proteína (g)", min_value=0.0, step=5.0, key="protein_input")
        
        with col2:
            carbs_input = st.number_input("Carbos (g)", min_value=0.0, step=5.0, key="carbs_input")
            fat_input = st.number_input("Grasas (g)", min_value=0.0, step=1.0, key="fat_input")
        
        notes_input = st.text_area("Notas", key="macro_notes", height=60)
        
        if st.button("Guardar Macros", use_container_width=True, type="primary"):
            is_valid, error_msg = calc.validate_macros_input(kcal_input, protein_input, carbs_input, fat_input)
            if is_valid:
                db.upsert_macros(str(date.today()), kcal_input, protein_input, carbs_input, fat_input, notes_input)
                st.success("Macros guardadas correctamente")
                st.rerun()
            else:
                st.error(f"Error: {error_msg}")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 3: WEIGHT & BF% TREND
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Tendencia Corporal (últimos 30 días)")
    
    weight_df = calc.get_weight_trend(30)
    bf_df = calc.get_bf_trend(30)
    
    if not weight_df.empty or not bf_df.empty:
        fig = go.Figure()
        
        if not weight_df.empty:
            fig.add_trace(go.Scatter(
                x=weight_df["metric_date"],
                y=weight_df["weight"],
                mode="lines+markers",
                name="Peso (kg)",
                line=dict(color=COLORS["steel_blue"], width=2),
                marker=dict(size=6),
                yaxis="y1"
            ))
        
        if not bf_df.empty:
            fig.add_trace(go.Scatter(
                x=bf_df["metric_date"],
                y=bf_df["bf_pct"],
                mode="lines+markers",
                name="BF %",
                line=dict(color=COLORS["accent_orange"], width=2, dash="dash"),
                marker=dict(size=6),
                yaxis="y2"
            ))
        
        fig.update_layout(
            title="Peso Corporal & Grasa Corporal",
            hovermode="x unified",
            template="plotly_dark",
            plot_bgcolor=COLORS["bg_darker"],
            paper_bgcolor=COLORS["bg_dark"],
            font=dict(color=COLORS["white_pure"]),
            yaxis=dict(title="Peso (kg)", titlefont=dict(color=COLORS["steel_blue"])),
            yaxis2=dict(
                title="BF %",
                titlefont=dict(color=COLORS["accent_orange"]),
                overlaying="y",
                side="right"
            ),
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de métricas corporales aún")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 4: MACRO HISTORY (last 7 days)
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Histórico Macros (últimos 7 días)")
    
    macros_df = calc.get_macros_range_trend(7)
    
    if not macros_df.empty:
        # Mostrar tabla
        display_df = macros_df[["log_date", "kcal", "protein", "carbs", "fat"]].copy()
        display_df.columns = ["Fecha", "Kcal", "Proteína (g)", "Carbos (g)", "Grasas (g)"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Gráfico barras
        fig = px.bar(
            macros_df,
            x="log_date",
            y="kcal",
            title="Kcal últimos 7 días vs Target",
            labels={"log_date": "Fecha", "kcal": "Kcal"},
            color="kcal",
            color_continuous_scale="Viridis",
        )
        
        # Agregar línea de target
        fig.add_hline(
            y=MACROS_TARGET["kcal"],
            line_dash="dash",
            line_color=COLORS["accent_green"],
            annotation_text="Target",
            annotation_position="right",
        )
        
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor=COLORS["bg_darker"],
            paper_bgcolor=COLORS["bg_dark"],
            font=dict(color=COLORS["white_pure"]),
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay histórico de macros aún")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 5: WEIGHT STATUS
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Estado Corporal")
    
    weight_change = calc.get_weight_change()
    bf_change = calc.get_bf_change()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Peso Actual",
            f"{weight_change['current']:.1f} kg",
            f"{weight_change['change']:+.1f} kg ({weight_change['pct_change']:+.1f}%)",
        )
    
    with col2:
        bf_status = calc.get_bf_status(bf_change["current"])
        st.metric(
            "Grasa Corporal",
            f"{bf_change['current']:.1f}%",
            f"{bf_change['change']:+.1f}%",
        )
