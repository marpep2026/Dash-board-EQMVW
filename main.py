import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="EQ Dashboard - Moraine Valley", layout="centered")

# 2. ESTILOS CSS PERSONALIZADOS (Estética limpia, Azul Institucional)
st.markdown("""
    <style>
    /* Importar fuentes limpias y formales */
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital@0;1&family=Open+Sans:wght@400;600&display=swap');
    
    /* Forzar fondo claro general */
    .stApp {
        background-color: #F8F9FA;
        color: #2b2b2b;
        font-family: 'Open Sans', sans-serif;
    }
    
    /* Títulos con fuente más tradicional */
    h1, h2, h3 { 
        font-family: 'Libre Baskerville', serif; 
        color: #003366; /* Azul Marino Institucional */
    }
    
    /* Botón 'Mark as Done' */
    .stButton>button { 
        background-color: #0056b3; /* Azul sereno */
        color: white; 
        border-radius: 6px; 
        width: 100%;
        height: 2.8em;
        border: none;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background-color: #004085; /* Azul más oscuro al pasar el mouse */
        color: white; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Etiqueta del Responsable (Owner) */
    .owner-label {
        color: #4a5568;
        background-color: #e2e8f0;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.75rem;
        display: inline-block;
        margin-bottom: 8px;
    }
    
    /* Contenedor de la frase motivacional */
    .quote-box {
        font-family: 'Libre Baskerville', serif;
        font-style: italic;
        color: #2c3e50;
        background-color: #ffffff;
        padding: 20px;
        border-left: 5px solid #003366;
        margin-bottom: 25px;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO Y TÍTULO
st.title("Moraine Valley Ward")
st.subheader("Elders Quorum Presidency Dashboard")

# --- AQUÍ VA TU FRASE MOTIVACIONAL ---
# Puedes cambiar el texto entre las comillas triples por la escritura o cita que desees.
st.markdown("""
<div class='quote-box'>
    "Por tanto, no os canséis de hacer lo bueno, porque estáis poniendo los cimientos de una gran obra. Y de las cosas pequeñas proceden las grandes."<br>
    <strong>— Doctrina y Convenios 64:33</strong>
</div>
""", unsafe_allow_html=True)

# 4. FECHA Y HORA ACTUAL
fecha_actual = datetime.now().strftime("%A, %B %d, %Y")
hora_actual = datetime.now().strftime("%I:%M %p")
st.caption(f"📅 **Today:** {fecha_actual} | 🔄 **Last Data Sync:** {hora_actual}")
st.divider()

# 5. CONEXIÓN A DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leer datos con caché
    df = conn.read(ttl=5)
    
    # Limpieza de datos preventiva
    df.columns = df.columns.str.strip()
    df['Status'] = df['Status'].astype(str).str.strip()

    if 'Notes' not in df.columns:
        df['Notes'] = None

    # --- TAREAS COMPLETADAS ---
    done_tasks = df[df['Status'] == 'Done']
    
    with st.expander(f"✅ SHOW COMPLETED TASKS ({len(done_tasks)})", expanded=False):
        if done_tasks.empty:
            st.write("No tasks completed yet.")
        else:
            for _, row in done_tasks.tail(20).iterrows():
                st.write(f"✔️ **{row['Assignment']}** | {row['Owner']} ({row['Section']})")

    st.divider()

    # --- TAREAS PENDIENTES ---
    sections = df['Section'].dropna().unique()

    for sec in sections:
        pending = df[(df['Section'] == sec) & (df['Status'] == 'Pending')]
        
        if not pending.empty:
            st.markdown(f"### 📁 {sec}")
            
            for idx, row in pending.iterrows():
                # Diseño de tarjeta para cada tarea
                with st.container():
                    c1, c2 = st.columns([3, 1])
                    
                    with c1:
                        st.markdown(f"<div class='owner-label'>👤 {row['Owner']}</div>", unsafe_allow_html=True)
                        st.write(f"**{row['Assignment']}**")
                        
                        nota = row['Notes']
                        if pd.notna(nota) and str(nota).strip() != "":
                            st.caption(f"📝 {nota}")
                    
                    with c2:
                        st.write("") # Espaciador para centrar el botón verticalmente
                        if st.button("Mark as Done", key=f"btn_{idx}"):
                            df.at[idx, 'Status'] = 'Done'
                            conn.update(data=df)
                            st.toast("Task marked as Done! 🎉") # Mensaje flotante en lugar de globos gigantes
                            st.rerun()
            
            st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; opacity: 0.2;'>", unsafe_allow_html=True)

except Exception as e:
    st.error("Error al conectar o leer los datos. Revisa tu conexión.")
    st.exception(e)
