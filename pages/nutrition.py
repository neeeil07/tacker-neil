"""
pages/nutrition.py — Nutrición & Pasos: tracking vs target, pasos diferenciado L-V vs S-D
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import pandas as pd
from utils.constants import COLORS, MACROS_TARGET, STEPS_TARGET
from utils import database as db
from utils import calculations as calc

def render():
    """Renderizar página de nutrición & pasos."""
    st.markdown("## NUTRICIÓN & PASOS")
    st.divider()
    
    col_nutrition, col_steps = st.columns(2)
    
    # ─────────────────────────────────────────────────────────────────────────
    # NUTRITION SECTION
    # ─────────────────────────────────────────────────────────────────────────
    with col_nutrition:
        st.markdown("### Nutrición")
        
        macros_status = calc.get_macro_vs_target()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Kcal",
                f"{macros_status['kcal']['current']:.0f}",
                f"{macros_status['kcal']['pct']:.0f}% Target",
                delta_color="normal" if macros_status['kcal']['status'] == 'ok' else 'inverse'
            )
            st.metric(
                "Proteína",
                f"{macros_status['protein']['current']:.0f}g",
                f"{macros_status['protein']['pct']:.0f}% Target",
            )
        
        with col2:
            st.metric(
                "Carbos",
                f"{macros_status['carbs']['current']:.0f}g",
                f"{macros_status['carbs']['pct']:.0f}% Target",
            )
            st.metric(
                "Grasas",
                f"{macros_status['fat']['current']:.0f}g",
                f"{macros_status['fat']['pct']:.0f}% Target",
            )
        
        st.divider()
        
        # Registro de macros
        with st.expander("Registrar Macros", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                kcal = st.number_input("Kcal", min_value=0.0, step=10.0, key="nut_kcal")
                protein = st.number_input("Proteína (g)", min_value=0.0, step=5.0, key="nut_protein")
            
            with col2:
                carbs = st.number_input("Carbos (g)", min_value=0.0, step=5.0, key="nut_carbs")
                fat = st.number_input("Grasas (g)", min_value=0.0, step=1.0, key="nut_fat")
            
            notes = st.text_area("Notas", key="nut_notes", height=50)
            
            if st.button("Guardar", use_container_width=True, type="primary", key="save_nut"):
                is_valid, error_msg = calc.validate_macros_input(kcal, protein, carbs, fat)
                if is_valid:
                    db.upsert_macros(str(date.today()), kcal, protein, carbs, fat, notes)
                    st.success("Macros guardadas")
                    st.rerun()
                else:
                    st.error(error_msg)
        
        st.divider()
        
        # Gráfico: Kcal últimos 14 días vs target
        st.markdown("### Kcal últimos 14 días")
        
        macros_df = calc.get_macros_range_trend(14)
        
        if not macros_df.empty:
            fig = px.bar(
                macros_df,
                x="log_date",
                y="kcal",
                color="kcal",
                color_continuous_scale="Teal",
                labels={"log_date": "Fecha", "kcal": "Kcal"},
            )
            
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
                showlegend=False,
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de macros")
    
    # ─────────────────────────────────────────────────────────────────────────
    # STEPS SECTION
    # ─────────────────────────────────────────────────────────────────────────
    with col_steps:
        st.markdown("### Pasos")
        
        steps_status = calc.get_steps_vs_target()
        day_type = "Fin de Semana" if steps_status["is_weekend"] else "Entre Semana"
        
        st.metric(
            "Pasos Hoy",
            f"{steps_status['current']:,.0f}",
            f"{steps_status['pct']:.0f}% Target | {day_type}",
        )
        
        st.divider()
        
        # Registro de pasos
        with st.expander("Registrar Pasos", expanded=False):
            steps_input = st.number_input("Pasos", min_value=0.0, step=100.0, key="steps_input")
            
            if st.button("Guardar", use_container_width=True, type="primary", key="save_steps"):
                is_valid, error_msg = calc.validate_steps_input(steps_input, steps_status["is_weekend"])
                if is_valid:
                    db.upsert_metrics(str(date.today()), steps=steps_input)
                    st.success("Pasos guardados")
                    st.rerun()
                else:
                    st.error(error_msg)
        
        st.divider()
        
        # Gráfico: Pasos últimos 7 días vs target
        st.markdown("### Pasos últimos 7 días")
        
        metrics_df = pd.DataFrame(db.get_metrics_range(
            str((date.today() - pd.Timedelta(days=7)).date()),
            str(date.today())
        )) if db.get_metrics_range(
            str((date.today() - pd.Timedelta(days=7)).date()),
            str(date.today())
        ) else pd.DataFrame()
        
        if not metrics_df.empty:
            metrics_df["metric_date"] = pd.to_datetime(metrics_df["metric_date"])
            metrics_df["day_of_week"] = metrics_df["metric_date"].dt.day_name()
            metrics_df["is_weekend"] = metrics_df["metric_date"].dt.weekday >= 4
            metrics_df["target"] = metrics_df["is_weekend"].apply(
                lambda x: STEPS_TARGET["weekend"] if x else STEPS_TARGET["weekday"]
            )
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=metrics_df["metric_date"],
                y=metrics_df["steps"],
                name="Pasos",
                marker=dict(color=COLORS["steel_blue"]),
            ))
            
            fig.add_trace(go.Scatter(
                x=metrics_df["metric_date"],
                y=metrics_df["target"],
                name="Target",
                mode="lines",
                line=dict(color=COLORS["accent_green"], dash="dash", width=2),
            ))
            
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor=COLORS["bg_darker"],
                paper_bgcolor=COLORS["bg_dark"],
                font=dict(color=COLORS["white_pure"]),
                hovermode="x unified",
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de pasos")
        
        st.divider()
        
        # Información de targets
        st.markdown("#### Target Pasos")
        st.markdown(f"- **Entre Semana (L-V)**: {STEPS_TARGET['weekday']:,} pasos")
        st.markdown(f"- **Fin de Semana (S-D)**: {STEPS_TARGET['weekend']:,} pasos")
