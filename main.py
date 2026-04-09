import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="EQ Presidency - Moraine Valley", layout="centered")

# 2. ESTILOS CSS PROFESIONALES
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital@0;1&family=Inter:wght@400;600&display=swap');
    
    .stApp { background-color: #F4F7F9; color: #1E1E1E; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Libre Baskerville', serif; color: #002E5D; }
    
    /* Tarjeta de Tarea */
    .task-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E0E4E8;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* Badge de Sección */
    .section-badge {
        font-size: 10px;
        text-transform: uppercase;
        color: #002E5D;
        background-color: #E7F0F7;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }

    /* Frase Inspiracional */
    .quote-container {
        font-family: 'Libre Baskerville', serif;
        font-style: italic;
        border-left: 4px solid #002E5D;
        padding: 15px 25px;
        background-color: white;
        margin: 20px 0;
        border-radius: 0 8px 8px 0;
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
    # Leer datos sin caché para pruebas, o ttl corto
    df = conn.read(ttl=2)
    df.columns = df.columns.str.strip()
    df['Status'] = df['Status'].astype(str).str.strip()
    if 'Notes' not in df.columns: df['Notes'] = ""

    # --- FILTRO DE TAREAS ---
    pending_df = df[df['Status'] == 'Pending']
    done_df = df[df['Status'] == 'Done']

    # --- PESTAÑAS POR NOMBRE (OWNER) ---
    st.markdown("#### 📋 Tareas por Responsable")
    
    # Obtenemos los nombres únicos de quienes tienen tareas pendientes
    owners = sorted(pending_df['Owner'].dropna().unique())
    
    if not owners:
        st.success("¡Excelente trabajo! No hay tareas pendientes.")
    else:
        # Creamos una pestaña para cada hermano
        tabs = st.tabs(owners)
        
        for i, owner in enumerate(owners):
            with tabs[i]:
                person_tasks = pending_df[pending_df['Owner'] == owner]
                
                for idx, row in person_tasks.iterrows():
                    # Contenedor visual de "Tarjeta"
                    with st.container():
                        col_text, col_btn = st.columns([4, 1])
                        
                        with col_text:
                            st.markdown(f"<span class='section-badge'>{row['Section']}</span>", unsafe_allow_html=True)
                            st.markdown(f"**{row['Assignment']}**")
                            if row['Notes']:
                                st.caption(f"📝 {row['Notes']}")
                        
                        with col_btn:
                            # Botón optimizado
                            st.write("") # Espaciador
                            if st.button("Finalizar", key=f"done_{idx}", use_container_width=True):
                                df.at[idx, 'Status'] = 'Done'
                                conn.update(data=df)
                                st.toast(f"Tarea de {owner} completada", icon="✅")
                                st.rerun()
                    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    # --- HISTORIAL (DENTRO DE UN EXPANDER PARA NO ESTORBAR) ---
    st.divider()
    with st.expander(f"📚 Ver Historial de Completadas ({len(done_df)})"):
        if done_df.empty:
            st.info("Aún no hay tareas marcadas como listas.")
        else:
            # Mostrar tabla simple para el historial
            st.table(done_df[['Owner', 'Assignment', 'Section']].tail(10))

except Exception as e:
    st.error("Error al cargar los datos.")
    st.info("Asegúrate de que la hoja de Google Sheets tenga las columnas: Section, Owner, Assignment, Status")
