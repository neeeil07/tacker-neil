"""
pages/training.py — Entrenamiento: DAY 1-6 selector, expanders de ejercicios, registro de sets
"""

import streamlit as st
import pandas as pd
from utils.constants import COLORS, DAY_LABELS, ROUTINE_DATA
from utils import database as db
from utils import calculations as calc

def render():
    """Renderizar página de entrenamiento."""
    st.markdown("## ENTRENAMIENTO")
    st.divider()
    
    # Inicializar session_state para day selector
    if "selected_day" not in st.session_state:
        st.session_state.selected_day = 1
    
    # ─────────────────────────────────────────────────────────────────────────
    # DAY SELECTOR
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Seleccionar Día")
    
    col_days = st.columns(6)
    for day_num in range(1, 7):
        with col_days[day_num - 1]:
            day_abbr = DAY_LABELS[day_num][0]
            if st.button(day_abbr, use_container_width=True, type="primary" if st.session_state.selected_day == day_num else "secondary"):
                st.session_state.selected_day = day_num
                st.rerun()
    
    st.divider()
    
    selected_day = st.session_state.selected_day
    day_label = DAY_LABELS[selected_day]
    current_mc = db.get_current_mc()
    
    # ─────────────────────────────────────────────────────────────────────────
    # SESSION TONELAJE METRIC
    # ─────────────────────────────────────────────────────────────────────────
    try:
        tonelaje_total = calc.calc_session_tonelaje(selected_day, current_mc)
        st.metric(
            "Tonelaje Total Sesión",
            f"{tonelaje_total:,.0f} kg",
            f"Día {selected_day} - {day_label[0]} | {day_label[1]} | MC: {current_mc}",
        )
    except Exception as e:
        st.warning(f"Error calculando tonelaje: {str(e)}")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # EXERCISE LIST & INPUTS
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(f"### Ejercicios - Día {selected_day}")
    
    try:
        exercises = db.get_exercises(selected_day)
        
        if not exercises:
            st.warning(f"No hay ejercicios registrados para el Día {selected_day}")
        else:
            for exercise in exercises:
                render_exercise_block(exercise, current_mc)
    
    except Exception as e:
        st.error(f"Error cargando ejercicios: {str(e)}")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # ADD NEW EXERCISE
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Agregar Ejercicio")
    
    with st.expander("Nuevo Ejercicio", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            exercise_name = st.text_input("Nombre del Ejercicio", key="new_exercise_name")
        
        with col2:
            exercise_reps = st.text_input("Reps Objetivo (ej: 8-12)", key="new_exercise_reps", value="8-12")
        
        if st.button("Agregar", use_container_width=True, type="primary"):
            if exercise_name and exercise_reps:
                db.add_exercise(selected_day, exercise_name, exercise_reps)
                st.success(f"Ejercicio '{exercise_name}' agregado")
                st.rerun()
            else:
                st.error("Completa todos los campos")

def render_exercise_block(exercise, microcycle):
    """Renderizar expander de un ejercicio con tabla de sets."""
    exercise_id = exercise["id"]
    exercise_name = exercise["name"]
    reps_obj = exercise["reps_obj"]
    
    with st.expander(f"{exercise_name} ({reps_obj})", expanded=False):
        try:
            # Obtener sets del ejercicio
            sets = db.get_workout_sets(exercise_id, microcycle)
            
            # Calcular tonelaje del ejercicio
            exercise_tonelaje = sum(s["reps"] * s["kg"] for s in sets)
            
            st.markdown(f"**Tonelaje: {exercise_tonelaje:,.0f} kg**")
            st.divider()
            
            # Tabla de sets (sin usar st.dataframe para mejor control)
            st.markdown("| RIR | Reps | Kg | Tonelaje | Acción |")
            st.markdown("|-----|------|-----|----------|--------|")
            
            for s in sets:
                set_id = s["id"]
                set_num = s["set_num"]
                rir = s["rir"]
                reps = s["reps"]
                kg = s["kg"]
                tonelaje = reps * kg
                
                # Inputs en columnas
                cols = st.columns([1, 1.2, 1.2, 1.2, 0.8])
                
                with cols[0]:
                    new_rir = st.number_input(f"RIR {set_num}", value=rir, min_value=-5.0, max_value=5.0, step=0.5, key=f"rir_{set_id}")
                
                with cols[1]:
                    new_reps = st.number_input(f"Reps {set_num}", value=reps, min_value=0.0, step=0.5, key=f"reps_{set_id}")
                
                with cols[2]:
                    new_kg = st.number_input(f"Kg {set_num}", value=kg, min_value=0.0, step=0.5, key=f"kg_{set_id}")
                
                with cols[3]:
                    st.text(f"{new_reps * new_kg:.0f} kg")
                
                with cols[4]:
                    if st.button("×", key=f"del_{set_id}", use_container_width=True):
                        db.delete_set(set_id)
                        st.success("Set eliminado")
                        st.rerun()
                
                # Guardar si hay cambios
                if new_rir != rir or new_reps != reps or new_kg != kg:
                    is_valid, error_msg = calc.validate_set_input(new_reps, new_kg, new_rir)
                    if is_valid:
                        db.upsert_set(exercise_id, microcycle, set_num, new_reps, new_kg, new_rir)
                        st.success("Set guardado")
            
            st.divider()
            
            # Agregar set
            if st.button(f"+ Agregar Set", use_container_width=True, key=f"add_set_{exercise_id}"):
                next_set_num = len(sets) + 1
                db.upsert_set(exercise_id, microcycle, next_set_num, 0, 0, 0)
                st.success(f"Set {next_set_num} creado")
                st.rerun()
        
        except Exception as e:
            st.error(f"Error en ejercicio: {str(e)}")
