# Dash-board-EQMVW

📋 Documentación del Proyecto: Elders Quorum Presidency Dashboard
Organización: Moraine Valley Ward
Tipo de Aplicación: Web App Interactiva (Dashboard de Tareas)
Estado Actual: Producción (v1.0)

1. Resumen del Proyecto
Aplicación web diseñada para la Presidencia del Quórum de Élderes. Permite visualizar, gestionar y completar asignaciones ("Action Items") extraídas en tiempo real desde una hoja de cálculo de Google Sheets. Utiliza un diseño centrado en el usuario (UX) agrupando tareas por líder y permitiendo la actualización de la base de datos desde la misma interfaz.

2. Stack Tecnológico (Herramientas)
Lenguaje: Python 3.x

Framework Frontend/Backend: Streamlit

Base de Datos: Google Sheets

Conector de Datos: st-gsheets-connection (Librería oficial de Streamlit para GSheets)

Manejo de Datos: pandas

Manejo de Tiempo: pytz (Zonas horarias) y datetime

3. Estructura de la Base de Datos (Google Sheets)
La aplicación depende estrictamente de una hoja de cálculo que debe contener exactamente estas 4 columnas en la primera fila (Headers). El código distingue mayúsculas de minúsculas:

Section: Categoría de la tarea (Ej: Ministering, Family History).

Owner: Nombre del hermano responsable (Ej: Adam, Marcos, Ben).

Assignment: Descripción detallada de la tarea.

Status: Estado actual. Solo reconoce dos valores operativos: Pending y Done.

4. Archivos Críticos del Proyecto
Para que la aplicación funcione en la nube, el repositorio de GitHub debe tener obligatoriamente estos tres componentes:

A) app.py (o main.py)
Contiene la lógica principal, la interfaz de usuario (UI) y las conexiones.

B) requirements.txt
Es el archivo de dependencias. Instruye al servidor de la nube qué librerías instalar. Debe contener exactamente esto:

Plaintext
streamlit
st-gsheets-connection
pandas
pytz
(Nota histórica: Nunca usar streamlit-gsheets aquí, el nombre correcto en PyPI es st-gsheets-connection).

C) Configuración de Secretos (secrets.toml)
Ubicado en la configuración de Streamlit Cloud (Settings > Secrets). Contiene el enlace a la hoja de Google Sheets para que la app tenga permiso de leer y escribir.

Ini, TOML
[connections.gsheets]
spreadsheet = "URL_DE_TU_GOOGLE_SHEET_AQUI"
5. Arquitectura de la Interfaz y UX (Directrices de Diseño)
Si un nuevo desarrollador altera la interfaz, debe respetar estas decisiones de diseño:

Modo Oscuro/Claro: El CSS de la app (st.markdown(<style>...) usa la etiqueta !important para forzar fondos blancos, letras oscuras y botones azules (#0056b3). Esto previene que la app se desconfigure visualmente si el usuario tiene su teléfono en "Dark Mode".

Agrupación Funcional (Tabs): Las tareas pendientes siempre deben filtrarse por Owner usando pestañas (st.tabs). Esto minimiza la carga cognitiva del usuario.

Manejo de Nulos (NaN): El código contiene una lógica estricta (df.dropna y .replace(['nan', 'None'], '')) para limpiar celdas vacías de Google Sheets y evitar que la palabra "nan" contamine la interfaz.

Zona Horaria Forzada: El reloj de la aplicación está anclado a America/Chicago. No utiliza la hora local del servidor en la nube ni la del dispositivo del usuario para garantizar consistencia. El formato es estadounidense (Mes Día, Año).

6. Lógica de Escritura (Write-Back)
El botón "Complete Task" no solo cambia el estado en la pantalla, sino que ejecuta una escritura bidireccional.
El flujo es:

Localiza el índice (idx) de la tarea en el DataFrame de Pandas.

Cambia la columna 'Status' de Pending a Done.

Usa conn.update(data=df) para empujar el cambio entero a Google Sheets.

Llama a st.rerun() para refrescar la pantalla instantáneamente.

7. Próximos Pasos Sugeridos (Para futuras versiones)
Filtros por Fecha: Añadir una columna de "Due Date" (Fecha límite) en Sheets para ordenar las tareas de la más urgente a la menos urgente.

Autenticación Simple: Añadir una contraseña de entrada para que solo los miembros de la presidencia puedan acceder al link.
