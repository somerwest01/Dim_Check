
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import math

st.set_page_config(page_title="Plano de Arnés Eléctrico", layout="wide")

if "lines" not in st.session_state:
    st.session_state.lines = []
if "clicks" not in st.session_state:
    st.session_state.clicks = []

st.sidebar.title("Herramientas")
add_line = st.sidebar.checkbox("Modo dibujo de línea")

st.title("Plano de Arnés Eléctrico Automotriz")
st.write("Haz dos clics en el área para definir una línea recta entre dos puntos.")

canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0.3)",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#ffffff",
    update_streamlit=True,
    height=600,
    width=1000,
    drawing_mode="transform",
    key="canvas",
)

# Captura de clics
if add_line and canvas_result.json_data is not None:
    objects = canvas_result.json_data.get("objects", [])
    if len(objects) > len(st.session_state.lines):
        last_obj = objects[-1]
        if last_obj["type"] == "circle":
            x = last_obj["left"] + last_obj["radius"]
            y = last_obj["top"] + last_obj["radius"]
            st.session_state.clicks.append((x, y))

# Si hay dos clics, pedir datos y dibujar línea
if len(st.session_state.clicks) == 2:
    x1, y1 = st.session_state.clicks[0]
    x2, y2 = st.session_state.clicks[1]

    st.subheader("Datos de la línea")
    tipo_inicio = st.selectbox("Tipo de objeto de inicio", ["Item", "BRK", "SPL"], key="inicio")
    tipo_fin = st.selectbox("Tipo de objeto de destino", ["Item", "BRK", "SPL"], key="fin")
    dimension = st.text_input("Dimensión de la línea (ej. 25cm)", key="dim")

    if st.button("Confirmar línea"):
        xm = (x1 + x2) / 2
        ym = (y1 + y2) / 2

        st.session_state.lines.append({
            "inicio": (x1, y1),
            "fin": (x2, y2),
            "tipo_inicio": tipo_inicio,
            "tipo_fin": tipo_fin,
            "dimension": dimension
        })

        st.success("Línea agregada correctamente")
        st.write(f"[1mLínea recta de ({x1:.1f}, {y1:.1f}) a ({x2:.1f}, {y2:.1f}) con dimensión {dimension}")
        st.write(f"Símbolo inicio: {tipo_inicio} en ({x1:.1f}, {y1:.1f})")
        st.write(f"Símbolo destino: {tipo_fin} en ({x2:.1f}, {y2:.1f})")
        st.write(f"Texto de dimensión en ({xm:.1f}, {ym:.1f})")

        st.session_state.clicks = []

# Mostrar todas las líneas
if st.session_state.lines:
    st.subheader("Líneas dibujadas")
    for i, line in enumerate(st.session_state.lines):
        st.write(f"{i+1}. De {line['inicio']} a {line['fin']} | Dimensión: {line['dimension']} | Inicio: {line['tipo_inicio']} | Fin: {line['tipo_fin']}")

