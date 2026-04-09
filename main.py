import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="EQ Presidency - Moraine Valley", layout="centered")

# 2. ESTILOS CSS REPARADOS (A prueba de Modo Oscuro/Claro)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital@0;1&family=Inter:wght@400;600&display=swap');
    
    /* Tipografía General */
    h1, h2, h3 { font-family: 'Libre Baskerville', serif; color: #003366; }
    
    /* Forzar diseño de la Tarjeta para que se lea siempre */
    .task-card {
        background-color: #ffffff;
        color: #1E1E1E;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        margin-bottom: 12px;
    }
    
    /* Etiqueta de la Categoría (Section) */
    .section-badge {
        font-size: 11px;
        text-transform: uppercase;
        color: #ffffff;
        background-color: #0056b3;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }

    /* Frase Inspiracional */
    .quote-container {
        font-family: 'Libre Baskerville', serif;
        font-style: italic;
        border-left: 4px solid #003366;
        padding: 15px 20px;
        background-color: #f8fafc;
        color: #334155;
        margin: 20px 0;
        border-radius: 0 8px 8px 0;
    }

    /* Arreglo para el botón 'Finalizar' (Forzar colores siempre) */
    div[data-testid="stButton"] > button {
        background-color: #0056b3 !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #004085 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. MANEJO DE HORA (ZONA HORARIA CHICAGO)
chicago_tz = pytz.timezone('America/Chicago')
now_chicago = datetime.now(chicago_tz)
fecha_display = now_chicago.strftime("%d de %B, %Y")
hora_display = now_chicago.strftime("%I:%M %p")

# 4. ENCABEZADO
st.title("Moraine Valley Ward")
st.markdown("### Elders Quorum Presidency Action Plan")

st.markdown(f"""
<div class='quote-container'>
    "Por tanto, no os canséis de hacer lo bueno, porque estáis poniendo los cimientos de una gran obra. Y de las cosas pequeñas proceden las grandes."<br>
    <span style='font-size: 0.9em; font-weight: bold; font-style: normal;'>— Doctrina y Convenios 64:33</span>
</div>
""", unsafe_allow_html=True)

st.caption(f"📍 **Chicago Time:** {fecha_display} | 🔄 **Sync:** {hora_display}")

# 5. CONEXIÓN A DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leer datos y limpiar valores nulos o vacíos
    df = conn.read(ttl=2)
    df = df.dropna(how='all') # Elimina filas completamente vacías
    
    # Asegurar que solo usamos las 4 columnas de tu tabla y limpiamos espacios
    df.columns = df.columns.str.strip()
    df['Status'] = df['Status'].astype(str).str.strip()
    df['Owner'] = df['Owner'].fillna('Unassigned').astype(str).str.strip()

    # --- FILTRO DE TAREAS ---
    pending_df = df[df['Status'] == 'Pending']
    done_df = df[df['Status'] == 'Done']

    # --- PESTAÑAS POR NOMBRE (OWNER) ---
    st.markdown("#### 📋 Action Items by Brother")
    
    # Obtenemos los nombres únicos ordenados alfabéticamente
    owners = sorted(pending_df['Owner'].unique())
    
    if not owners:
        st.success("¡Excelente trabajo! No hay tareas pendientes.")
    else:
        # Creamos las pestañas
        tabs = st.tabs(owners)
        
        for i, owner in enumerate(owners):
            with tabs[i]:
                # Filtrar tareas por persona
                person_tasks = pending_df[pending_df['Owner'] == owner]
                
                for idx, row in person_tasks.iterrows():
                    # Layout de tarjeta
                    st.markdown(f"""
                        <div class="task-card">
                            <div class="section-badge">{row['Section']}</div><br>
                            <strong>{row['Assignment']}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Botón alineado a la derecha
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button("Complete Task", key=f"done_{idx}", use_container_width=True):
                            df.at[idx, 'Status'] = 'Done'
                            conn.update(data=df)
                            st.toast(f"Tarea de {owner} completada", icon="✅")
                            st.rerun()
                    st.write("---") # Divisor sutil entre tareas

    # --- HISTORIAL ---
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(f"📚 Completed Tasks History ({len(done_df)})"):
        if done_df.empty:
            st.info("No completed tasks yet.")
        else:
            st.dataframe(
                done_df[['Owner', 'Assignment', 'Section']].tail(15),
                hide_index=True,
                use_container_width=True
            )

except Exception as e:
    st.error("Error connecting to the data. Please check your Google Sheet structure.")
    st.exception(e)
