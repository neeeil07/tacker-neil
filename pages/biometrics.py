"""
pages/biometrics.py — Biometría: peso, % grasa corporal, histórico, tendencias
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta
from utils.constants import COLORS
from utils import database as db
from utils import calculations as calc

def render():
    """Renderizar página de biometría."""
    st.markdown("## BIOMETRÍA")
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # METRICS CARDS
    # ─────────────────────────────────────────────────────────────────────────
    weight_change = calc.get_weight_change()
    bf_change = calc.get_bf_change()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Peso Actual",
            f"{weight_change['current']:.1f} kg",
            f"{weight_change['change']:+.1f} kg ({weight_change['pct_change']:+.1f}%)",
        )
    
    with col2:
        bf_status = calc.get_bf_status(bf_change["current"])
        color = "normal" if bf_status == "ok" else "off"
        st.metric(
            "Grasa Corporal",
            f"{bf_change['current']:.1f}%",
            f"{bf_change['change']:+.1f}%",
            delta_color=color,
        )
    
    with col3:
        st.metric(
            "Referencia Inicial",
            f"{bf_change['initial']:.1f}%",
            help="BF% al inicio del rastreo"
        )
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # REGISTRATION FORM
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Registrar Hoy")
    
    with st.expander("Cargar Métricas", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            weight_input = st.number_input("Peso (kg)", min_value=30.0, max_value=150.0, step=0.1, key="bio_weight")
            bf_input = st.number_input("Grasa Corporal (%)", min_value=5.0, max_value=50.0, step=0.1, key="bio_bf")
        
        with col2:
            sleep_input = st.number_input("Horas de Sueño", min_value=0.0, max_value=24.0, step=0.5, key="bio_sleep")
            notes_input = st.text_area("Notas", key="bio_notes", height=60)
        
        if st.button("Guardar Métricas", use_container_width=True, type="primary"):
            db.upsert_metrics(str(date.today()), weight=weight_input, bf_pct=bf_input, sleep=sleep_input, notes=notes_input)
            st.success("Métricas guardadas")
            st.rerun()
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # TREND GRAPHS (last 90 days)
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Tendencia Corporal (últimos 90 días)")
    
    weight_df = calc.get_weight_trend(90)
    bf_df = calc.get_bf_trend(90)
    
    if not weight_df.empty or not bf_df.empty:
        fig = go.Figure()
        
        # Peso
        if not weight_df.empty:
            fig.add_trace(go.Scatter(
                x=weight_df["metric_date"],
                y=weight_df["weight"],
                mode="lines+markers",
                name="Peso (kg)",
                line=dict(color=COLORS["steel_blue"], width=2),
                marker=dict(size=5),
                yaxis="y1"
            ))
        
        # BF%
        if not bf_df.empty:
            fig.add_trace(go.Scatter(
                x=bf_df["metric_date"],
                y=bf_df["bf_pct"],
                mode="lines+markers",
                name="BF %",
                line=dict(color=COLORS["accent_orange"], width=2),
                marker=dict(size=5),
                yaxis="y2"
            ))
            
            # Agregar bandas de referencia de BF%
            fig.add_hline(
                y=15,
                line_dash="dash",
                line_color=COLORS["accent_red"],
                annotation_text="Crítico (>15%)",
                yaxis="y2",
                annotation_position="right",
            )
            fig.add_hline(
                y=12,
                line_dash="dot",
                line_color=COLORS["accent_orange"],
                annotation_text="Meta (12%)",
                yaxis="y2",
                annotation_position="right",
            )
        
        fig.update_layout(
            title="Composición Corporal",
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
        st.info("No hay datos de tendencias aún")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # HISTORY TABLE (last 20 records)
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Histórico Completo")
    
    metrics = db.get_metrics_range("2000-01-01", str(date.today()))
    
    if metrics:
        metrics_list = list(reversed(metrics))[-20:]  # Últimas 20
        metrics_df = pd.DataFrame(metrics_list)
        
        if not metrics_df.empty:
            metrics_df["metric_date"] = pd.to_datetime(metrics_df["metric_date"])
            
            # Calcular cambios
            metrics_df = metrics_df.sort_values("metric_date")
            metrics_df["Peso Δ"] = metrics_df["weight"].diff().round(2)
            metrics_df["BF Δ"] = metrics_df["bf_pct"].diff().round(2)
            
            # Mostrar tabla
            display_df = metrics_df[[
                "metric_date", "weight", "Peso Δ", "bf_pct", "BF Δ", "sleep", "steps", "notes"
            ]].copy()
            
            display_df.columns = [
                "Fecha", "Peso (kg)", "Δ", "BF %", "Δ", "Sueño (h)", "Pasos", "Notas"
            ]
            
            # Formatear fechas
            display_df["Fecha"] = display_df["Fecha"].dt.strftime("%Y-%m-%d")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("Sin registros de biometría")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # BF% REFERENCE BANDS
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Rangos de Referencia - Grasa Corporal")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **✓ Óptimo (Verde)**  
        BF% < 12%
        """)
    
    with col2:
        st.markdown("""
        **⚠ Advertencia (Naranja)**  
        BF% 12-15%
        """)
    
    with col3:
        st.markdown("""
        **✗ Crítico (Rojo)**  
        BF% > 15%
        """)
