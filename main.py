import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuración de marca
st.set_page_config(page_title="GoPolitics | Control de Asignaciones", layout="wide")

st.markdown("""
    <style>
    h1, h2, h3 { color: #002366; font-family: 'Montserrat', sans-serif; }
    .stButton>button { 
        background-color: #CC0000; 
        color: white; 
        border-radius: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Panel de Control de Asignaciones")

# Conexión con la hoja
conn = st.connection("gsheets", type=GSheetsConnection)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1jsKCk1FO9MCNtwdT2C56EWQVTQDI5akF7hCX0njGkCc/edit?usp=sharing" # Reemplazaremos esto en la Fase 4
df = conn.read(spreadsheet=URL_SHEET, ttl=0)

def marcar_hecho(index):
    df.at[index, 'Status'] = 'Realizada'
    conn.update(spreadsheet=URL_SHEET, data=df)
    st.rerun()

# Filtrado por tus columnas reales
sections = df['Section'].unique()
cols = st.columns(len(sections))

for i, sec in enumerate(sections):
    with cols[i]:
        st.subheader(f"📂 {sec}")
        # Filtro de pendientes para este segmento
        pendientes = df[(df['Section'] == sec) & (df['Status'] == 'Pendiente')]
        
        for idx, row in pendientes.iterrows():
            with st.expander(f"📌 {row['Assignment']}"):
                st.write(f"**Responsable:** {row['Owner']}")
                st.write(f"**Notas:** {row['Notes']}")
                if st.button("Marcar como Realizada", key=f"btn_{idx}"):
                    marcar_hecho(idx)

        st.divider()
        # Historial
        realizadas = df[(df['Section'] == sec) & (df['Status'] == 'Realizada')]
        st.caption(f"Terminadas: {len(realizadas)}")
