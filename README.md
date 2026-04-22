# CENTRO DE MANDO · NEIL
## Professional Performance Tracker | Supabase + Streamlit

---

## Overview

**Centro de Mando v2.0** es una aplicación de seguimiento de rendimiento deportivo de grado profesional. Migrada completamente de SQLite a **Supabase**, con tema **Dark Mode minimalista**, sin emojis, y optimizada para móvil y desktop.

### Características Clave

- **4 Secciones Principales**: DASHBOARD | ENTRENAMIENTO | NUTRICIÓN & PASOS | BIOMETRÍA
- **Dark Mode Profesional**: Paleta minimalista (Gris Pizarra, Blanco Puro, Azul Acero)
- **Persistencia en Supabase**: Todas las tablas conectadas a cloud database
- **Responsive Design**: Optimizado para desktop, tablet y móvil
- **Cálculos de Tonelaje**: Automático (Reps × Kg) con históricos por Microciclo
- **Tracking Nutricional**: Macros vs target diario + histórico 14 días
- **Métricas Corporales**: Peso + % Grasa con tendencias 90 días
- **Pasos Diferenciados**: Target 10k L-V | 6k S-D

---

## Setup & Instalación

### 1. Requisitos
- Python 3.9+
- pip o uv
- Credenciales Supabase (ya configuradas en `.streamlit/secrets.toml`)

### 2. Clonar/Descargar

```bash
cd /path/to/tacker-neil
```

### 3. Crear Entorno Virtual (opcional pero recomendado)

```bash
# Opción A: venv (nativo)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Opción B: conda
conda create -n neil-tracker python=3.11
conda activate neil-tracker
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar Supabase (Automático)

Las credenciales ya están en `.streamlit/secrets.toml`. Si necesitas cambiarlas:

```toml
[connections.supabase]
type = "SupabaseConnection"
url = "https://your-supabase-url.supabase.co"
key = "your-anon-key"
```

### 6. Ejecutar la Aplicación

```bash
streamlit run app.py
```

Abre automáticamente en `http://localhost:8501`

---

## Estructura del Proyecto

```
tacker-neil/
├── app.py                      # Orquestador principal
├── requirements.txt            # Dependencias Python
├── utils/
│   ├── __init__.py
│   ├── constants.py            # Paleta, macros target, estructura rutina
│   ├── database.py             # Wrapper Supabase (CRUD)
│   ├── calculations.py         # Lógica: tonelaje, validaciones, tendencias
│   └── excel_loader.py         # Bootstrap desde Excel si existe
├── components/
│   ├── __init__.py
│   ├── header.py               # Tema CSS + inyección de estilos
│   └── sidebar.py              # Navegación 4 secciones
├── pages/
│   ├── __init__.py
│   ├── dashboard.py            # KPIs, registro rápido, gráficos
│   ├── training.py             # Días 1-6, expanders ejercicios
│   ├── nutrition.py            # Nutrición + pasos con target diferenciado
│   └── biometrics.py           # Peso, BF%, histórico, tendencias
├── .streamlit/
│   └── secrets.toml            # Credenciales Supabase (GIT IGNORED)
├── Mesociclo Neil.xlsx         # (Opcional) Archivo para bootstrap
└── README.md                   # Este archivo
```

---

## Uso: Flujo Principal

### 1. **DASHBOARD** — Panel de Control Diario
- **KPIs Nutricionales**: Kcal, Proteína, Carbos, Grasas vs targets
- **Registro Rápido**: Formulario para guardar macros del día
- **Gráficos**: Peso + BF% últimos 30 días (dual-axis)
- **Histórico Macros**: Últimos 7 días en tabla

### 2. **ENTRENAMIENTO** — Rutina de Ejercicios
- **Selector Día**: 6 botones (DOM-VIE)
- **Métrica Tonelaje**: Suma total de la sesión en kg
- **Expanders por Ejercicio**: Tabla de sets con inputs (RIR | Reps | Kg | Tonelaje)
- **Agregar Sets**: Botón [+ Agregar Set] para nuevas series
- **Agregar Ejercicios**: Crear ejercicios custom por día

**Estructura Rutina Predefinida**:
- **DAY 1**: Pierna + Hombro + Core
- **DAY 2**: Espalda + Bíceps (incluye Tríada Jalones + Remos Unilaterales)
- **DAY 3**: Pecho + Hombro + Tríceps + Core (incluye Aperturas Polea)
- **DAY 4**: Pierna Compuesta + Core
- **DAY 5**: Espalda + Bíceps + Core (incluye Remos Unilaterales)
- **DAY 6**: Hombro + Pecho + Tríceps + Core (incluye Fondos)

### 3. **NUTRICIÓN & PASOS** — Tracking vs Target
- **Nutrición**:
  - 4 métricas (Kcal 1,850 | Proteína 135g | Carbos 235g | Grasas 40g)
  - Formulario registro diario
  - Gráfico barras últimos 14 días vs target
- **Pasos**:
  - Target diferenciado (10k L-V, 6k S-D)
  - Registro formulario
  - Gráfico últimos 7 días con línea de target

### 4. **BIOMETRÍA** — Composición Corporal
- **Métricas Actuales**: Peso, BF%, referencia inicial
- **Registro Hoy**: Formulario (Peso, %BF, Sueño, Notas)
- **Gráfico Tendencia**: Peso + BF% últimos 90 días (dual-axis con bandas de referencia)
- **Histórico**: Tabla últimos 20 registros con deltas

**Bandas de Referencia BF%**:
- 🟢 **Óptimo**: < 12%
- 🟠 **Advertencia**: 12-15%
- 🔴 **Crítico**: > 15%

---

## Datos & Bootstrap

### Primera Ejecución
- Automáticamente carga **ROUTINE_DATA** (6 días × 40+ ejercicios)
- Intenta leer `Mesociclo Neil.xlsx` si existe
- Si no existe Excel, usa datos hardcodeados
- Carga históricos (HIST, HIST_MACROS, HIST_METRICS) en Supabase
- **Una sola vez**: Marcar "bootstrapped" = true en app_config

### Microciclos
Selector en sidebar: **MC01–MC08**
- Cambiar MC automáticamente actualiza contexto de sets registrados
- Históricos completos disponibles para comparación

---

## Personalización

### Modificar Targets Nutricionales
Editar en `utils/constants.py`:
```python
MACROS_TARGET = {
    "kcal": 1850,
    "protein": 135,
    "fat": 40,
    "carbs": 235,
}
```

### Modificar Targets Pasos
```python
STEPS_TARGET = {
    "weekday": 10000,  # Lunes-Viernes
    "weekend": 6000,   # Sábado-Domingo
}
```

### Cambiar Tema (Colores)
Editar en `utils/constants.py` → `COLORS` dict
```python
COLORS = {
    "bg_dark": "#1e1e1e",      # Fondo oscuro
    "steel_blue": "#34495e",   # Acentos (métricas)
    "accent_red": "#e74c3c",   # Alertas
    ...
}
```

### Agregar Ejercicios Personalizados
En la UI: **ENTRENAMIENTO** → [Agregar Ejercicio] → Nombre + Reps Objetivo

---

## Troubleshooting

### Error: "Connection refused" / Supabase no responde
- Verificar internet
- Revisar `.streamlit/secrets.toml` (URL y KEY correctas)
- Probar credenciales en [Supabase Dashboard](https://app.supabase.com)

### Error: "Table 'exercises' does not exist"
- Supabase requiere tablas preexistentes:
  - `exercises` (id, day, name, reps_obj, order_idx, active)
  - `workout_sets` (id, exercise_id, microcycle, set_num, reps, kg, rir)
  - `macros_log` (id, log_date, kcal, protein, carbs, fat, notes)
  - `body_metrics` (id, metric_date, weight, steps, sleep, bf_pct, notes)
  - `app_config` (key, value)

### Error: "ModuleNotFoundError: No module named 'utils'"
```bash
# Asegurar que estás en la raíz del proyecto
cd /path/to/tacker-neil
streamlit run app.py
```

---

## Performance

- **Queries**: Optimizadas con índices en Supabase
- **Caching**: `@st.cache_resource` para ejercicios frecuentes
- **Gráficos Plotly**: Render < 1s (últimos 90 días)
- **Mobile**: Tested en Safari/Chrome 320px – 1920px

---

## Roadmap (Futuro)

- [ ] Exportar a CSV/Excel
- [ ] Multi-usuario con autenticación Supabase
- [ ] Notificaciones/Reminders
- [ ] Mobile app nativa (React Native)
- [ ] API REST para integraciones

---

## Soporte & Docs

- **Streamlit Docs**: https://docs.streamlit.io
- **Supabase Docs**: https://supabase.com/docs
- **Plotly Docs**: https://plotly.com/python

---

## License

Uso personal. © 2026 Neil Mesociclo.

---

## Changelog

### v2.0 (2026-04-22)
- ✅ Migración SQLite → Supabase
- ✅ Dark Mode profesional (sin emojis)
- ✅ Refactorización modular (utils, components, pages)
- ✅ 4 Secciones navegación
- ✅ Responsive design (mobile-first)
- ✅ Bootstrap automático de históricos

### v1.0 (2026-03-01)
- SQLite local
- Interfaz con emojis
- Monolítica (app.py único)
