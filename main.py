import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="GoPolitics Control", layout="wide")

st.title("📊 Panel de Control de Asignaciones")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)
URL_SHEET = st.secrets["connections"]["gsheets"]["spreadsheet"]

# Forzamos la lectura fresca (ttl=0)
try:
    df = conn.read(spreadsheet=URL_SHEET, ttl=0)
    
    # Limpiamos espacios en blanco en los nombres de las columnas por si acaso
    df.columns = df.columns.str.strip()

    if 'Status' not in df.columns:
        st.error(f"Error: No encontré la columna 'Status'. Columnas detectadas: {list(df.columns)}")
    else:
        # Poner todo en una lista vertical para que se vea mejor (ya que tienes muchas secciones)
        sections = df['Section'].unique()
        
        for sec in sections:
            st.markdown(f"### 📂 {sec}")
            # Filtramos ignorando mayúsculas/minúsculas en el contenido de la celda
            pendientes = df[(df['Section'] == sec) & (df['Status'].str.strip() == 'Pendiente')]
            
            if pendientes.empty:
                st.info(f"Sin pendientes en {sec}")
            else:
                for idx, row in pendientes.iterrows():
                    col_t, col_b = st.columns([4, 1])
                    col_t.write(f"**{row['Assignment']}** ({row['Owner']})")
                    if col_b.button("Hecho", key=f"btn_{idx}"):
                        df.at[idx, 'Status'] = 'Realizada'
                        conn.update(spreadsheet=URL_SHEET, data=df)
                        st.success("¡Actualizado!")
                        st.rerun()
            st.divider()

except Exception as e:
    st.error(f"Hubo un problema al conectar: {e}")
