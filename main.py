import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de marca GoPolitics
st.set_page_config(page_title="GoPolitics | Assignments", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Roboto&display=swap');
    h1, h2, h3 { font-family: 'Montserrat', sans-serif; color: #002366; }
    .stButton>button { 
        background-color: #CC0000; 
        color: white; 
        border-radius: 8px; 
        width: 100%;
        border: none;
    }
    .stButton>button:hover { background-color: #8B0000; border: 1px solid white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Assignment Dashboard")

# 2. Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
URL_SHEET = st.secrets["connections"]["gsheets"]["spreadsheet"]

try:
    # Leer datos frescos
    df = conn.read(spreadsheet=URL_SHEET, ttl=0)
    
    # Limpiar nombres de columnas por si hay espacios invisibles
    df.columns = df.columns.str.strip()

    # 3. Lógica de Secciones
    # Solo tomamos las secciones que tengan tareas "Pending"
    sections = df['Section'].unique()

    for sec in sections:
        # Filtrar tareas pendientes para esta sección
        # Usamos .str.strip() para evitar errores por espacios accidentales en el Excel
        pending_tasks = df[(df['Section'] == sec) & (df['Status'].str.strip() == 'Pending')]
        
        # Solo mostrar la sección si tiene algo pendiente
        if not pending_tasks.empty:
            st.markdown(f"### 📂 {sec}")
            
            for idx, row in pending_tasks.iterrows():
                with st.container():
                    col_info, col_btn = st.columns([3, 1])
                    
                    with col_info:
                        st.write(f"**{row['Assignment']}**")
                        st.caption(f"👤 {row['Owner']} | 📝 {row['Notes'] if pd.notna(row['Notes']) else ''}")
                    
                    with col_btn:
                        # Al presionar, cambia Status a 'Done'
                        if st.button("Done", key=f"btn_{idx}"):
                            df.at[idx, 'Status'] = 'Done'
                            conn.update(spreadsheet=URL_SHEET, data=df)
                            st.toast(f"Task from {sec} completed!")
                            st.rerun()
            st.divider()

    # Mostrar resumen de tareas completadas al final
    with st.expander("Show Completed Tasks (Done)"):
        done_tasks = df[df['Status'].str.strip() == 'Done']
        if done_tasks.empty:
            st.write("No tasks completed yet.")
        else:
            for _, row in done_tasks.tail(10).iterrows():
                st.write(f"✅ {row['Assignment']} ({row['Section']})")

except Exception as e:
    st.error(f"Please check your Google Sheet structure. Error: {e}")
