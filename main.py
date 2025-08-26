
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# Configuración de la página
st.set_page_config(page_title="Plano de Arnés Eléctrico", layout="wide")

# Panel lateral vacío
st.sidebar.title("Panel de Herramientas")

# Área principal con canvas interactivo
st.title("Área de Dibujo")

canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0.3)",  # Color de relleno
    stroke_width=2,                   # Grosor de línea
    stroke_color="#000000",         # Color de línea
    background_color="#ffffff",     # Fondo blanco
    update_streamlit=True,
    height=600,
    width=1000,
    drawing_mode="line",             # Modo de dibujo: línea recta
    key="canvas",
)
