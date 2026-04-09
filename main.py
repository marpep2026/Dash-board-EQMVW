import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE PÁGINA (Arquitectura base)
st.set_page_config(page_title="EQ Presidency - Moraine Valley", layout="centered")

# 2. ESTILOS CSS AVANZADOS (UI/UX)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital@0;1&family=Inter:wght@400;600&display=swap');
    
    h1, h2, h3, h4 { font-family: 'Libre Baskerville', serif; color: #003366; }
    
    /* Tarjetas de Tarea */
    .task-card {
        background-color: #ffffff;
        color: #1E1E1E;
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .section-badge {
        font-size: 10px;
        text-transform: uppercase;
        color: #ffffff;
        background-color: #0056b3;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: 700;
        margin-bottom: 5px;
        display: inline-block;
    }

    /* Caja de Escritura */
    .quote-container {
        font-family: 'Libre Baskerville', serif;
        font-style: italic;
        border-left: 5px solid #003366;
        padding: 15px 20px;
        background-color: #f1f5f9;
        color: #1e293b;
        margin: 20px 0;
        border-radius: 0 8px 8px 0;
    }

    /* BOTÓN PRIMARIO: Finalizar (Sólido) */
    div[data-testid="stButton"] > button {
        background-color: #0056b3 !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        height: 2.5em !important;
        border: none !important;
    }
    
    /* BOTÓN SECUNDARIO: Historial (Popover / Contorno) */
    div[data-testid="stPopover"] > button {
        background-color: transparent !important;
        color: #003366 !important;
        border: 2px solid #003366 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        height: 2.5em !important;
    }
    div[data-testid="stPopover"] > button:hover {
        background-color: #f8fafc !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. RELOJ DE CHICAGO (Formato US: Mes, Día, Año)
chicago_tz = pytz.timezone('America/Chicago')
now_chicago = datetime.now(chicago_tz)
fecha_display = now_chicago.strftime("%B %d, %Y")
hora_display = now_chicago.strftime("%I:%M %p")

# 4. ENCABEZADO
st.title("Moraine Valley Ward")
st.markdown("### Elders Quorum Presidency Dashboard")

st.markdown(f"""
<div class='quote-container'>
    "Por tanto, no os canséis de hacer lo bueno, porque estáis poniendo los cimientos de una gran obra. Y de las cosas pequeñas proceden las grandes."<br>
    <span style='font-size: 0.9em; font-weight: bold; font-style: normal;'>— Doctrina y Convenios 64:33</span>
</div>
""", unsafe_allow_html=True)

st.caption(f"📍 **Chicago:** {fecha_display} | 🔄 **Sync:** {hora_display}")
st.divider()

# 5. CONEXIÓN Y LIMPIEZA
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leer y limpiar datos
    df = conn.read(ttl=2)
    df = df.dropna(subset=['Assignment', 'Owner'])
    
    # Estandarizar textos
    for col in df.columns:
        df[col] = df[col].astype(str).replace(['nan', 'None', 'NaN'], '')

    # Filtros
    pending_df = df[df['Status'].str.contains('Pending', case=False)]
    done_count = len(df[df['Status'].str.contains('Done', case=False)])

    # --- HEADER ALINEADO (DISEÑO UX PROFESIONAL) ---
    col_titulo, col_historial = st.columns([5, 3])
    
    with col_titulo:
        # Alineado con HTML para que empate perfecto con el botón de la derecha
        st.markdown("<h4 style='margin-top: 5px;'>📋 Action Items</h4>", unsafe_allow_html=True)
        
    with col_historial:
        # Ventana Emergente (Popover) alineada a la derecha
        with st.popover(f"📚 Historial ({done_count})", use_container_width=True):
            st.markdown("**Tareas Completadas Recientemente**")
            historial = df[df['Status'].str.contains('Done', case=False)]
            if not historial.empty:
                st.dataframe(historial[['Owner', 'Assignment', 'Section']].tail(15), hide_index=True)
            else:
                st.info("Aún no hay tareas completadas.")

    # --- PESTAÑAS (TABS) ---
    owners = sorted(pending_df['Owner'].unique())
    
    if not owners:
        st.success("🎉 ¡Todas las tareas han sido completadas!")
    else:
        # Etiquetas dinámicas con contador
        tab_labels = []
        for o in owners:
            count = len(pending_df[pending_df['Owner'] == o])
            tab_labels.append(f"{o} ({count})")
        
        tabs = st.tabs(tab_labels)
        
        for i, owner in enumerate(owners):
            with tabs[i]:
                person_tasks = pending_df[pending_df['Owner'] == owner]
                
                for idx, row in person_tasks.iterrows():
                    with st.container():
                        st.markdown(f"""
                            <div class="task-card">
                                <div class="section-badge">{row['Section']}</div><br>
                                <strong>{row['Assignment']}</strong>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns([3, 1])
                        with c2:
                            if st.button("Finalizar", key=f"btn_{idx}", use_container_width=True):
                                df.at[idx, 'Status'] = 'Done'
                                conn.update(data=df)
                                st.toast(f"¡Tarea de {owner} completada!", icon="✅")
                                st.rerun()
                        st.write("") 

except Exception as e:
    st.error("Hubo un problema al cargar los datos. Revisa la conexión.")
    st.info("Asegúrate de que tu Google Sheet tenga las columnas: Section, Owner, Assignment, Status")
