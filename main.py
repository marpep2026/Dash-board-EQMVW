import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página con estética GoPolitics
st.set_page_config(page_title="GoPolitics Dashboard", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Roboto&display=swap');
    h1, h2, h3 { font-family: 'Montserrat', sans-serif; color: #002366; }
    
    /* Botón 'Mark as Done' en Rojo Intenso */
    .stButton>button { 
        background-color: #CC0000; 
        color: white; 
        border-radius: 8px; 
        width: 100%;
        height: 3em;
        border: none;
        font-weight: bold;
        font-size: 16px;
    }
    .stButton>button:hover { background-color: #8B0000; color: white; border: 1px solid white; }
    
    /* Tag de Owner */
    .owner-label {
        color: #CC0000;
        font-weight: bold;
        font-size: 0.85rem;
        margin-bottom: -10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Assignment Dashboard")

# Conexión Segura con Service Account
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leer datos sin caché para ver cambios inmediatos
    df = conn.read(ttl=0)
    df.columns = df.columns.str.strip()

    # --- SECCIÓN SUPERIOR: COMPLETED TASKS (BOTÓN VERDE EXPANDIBLE) ---
    done_tasks = df[df['Status'].str.strip() == 'Done']
    
    # Estética de botón verde para el historial
    with st.expander(f"🟢 SHOW COMPLETED TASKS ({len(done_tasks)})", expanded=False):
        if done_tasks.empty:
            st.write("No tasks completed yet.")
        else:
            # Mostramos las últimas 20 realizadas
            for _, row in done_tasks.tail(20).iterrows():
                st.write(f"✅ **{row['Assignment']}** | {row['Owner']} ({row['Section']})")

    st.divider()

    # --- SECCIÓN MEDIA: PENDING TASKS POR CATEGORÍA ---
    sections = df['Section'].unique()

    for sec in sections:
        pending = df[(df['Section'] == sec) & (df['Status'].str.strip() == 'Pending')]
        
        if not pending.empty:
            st.markdown(f"### 📂 {sec}")
            
            for idx, row in pending.iterrows():
                with st.container():
                    c1, c2 = st.columns([3, 1.2])
                    
                    with c1:
                        st.markdown(f"<div class='owner-label'>{row['Owner']}</div>", unsafe_allow_html=True)
                        st.write(f"**{row['Assignment']}**")
                        if pd.notna(row['Notes']) and str(row['Notes']).strip() != "":
                            st.caption(f"Note: {row['Notes']}")
                    
                    with c2:
                        # Acción: Actualizar Status a 'Done'
                        if st.button("Mark as Done", key=f"btn_{idx}"):
                            df.at[idx, 'Status'] = 'Done'
                            conn.update(data=df)
                            st.balloons()
                            st.rerun()
            st.divider()

except Exception as e:
    st.error(f"Waiting for connection or data update... Error: {e}")
    st.info("Ensure the Service Account email is added as 'Editor' in your Google Sheet.")
