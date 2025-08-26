
import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Plano de Arnés Eléctrico", layout="wide")

if "lines" not in st.session_state:
    st.session_state.lines = []

st.sidebar.title("Herramientas")
add_line = st.sidebar.button("Agregar nueva línea")

st.title("Plano de Arnés Eléctrico Automotriz")
st.write("Haz clic en el área para definir los puntos de la línea.")

canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0.3)",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#ffffff",
    update_streamlit=True,
    height=600,
    width=1000,
    drawing_mode="freedraw" if add_line else "transform",
    key="canvas",
)

def draw_symbol(x, y, tipo):
    if tipo == "Item":
        st.write(f"🟥 Cuadrado en ({x}, {y})")
    elif tipo == "BRK":
        st.write(f"⚫ Círculo negro en ({x}, {y})")
    elif tipo == "SPL":
        st.write(f"🔺 Triángulo en ({x}, {y})")

if add_line:
    st.subheader("Paso 1: Selecciona el punto de partida")
    x1 = st.number_input("X del punto de partida", min_value=0, max_value=1000, value=100)
    y1 = st.number_input("Y del punto de partida", min_value=0, max_value=600, value=100)
    tipo_inicio = st.selectbox("Tipo de objeto de inicio", ["Item", "BRK", "SPL"])

    st.subheader("Paso 2: Selecciona el punto destino")
    x2 = st.number_input("X del punto destino", min_value=0, max_value=1000, value=400)
    y2 = st.number_input("Y del punto destino", min_value=0, max_value=600, value=300)
    dimension = st.text_input("Dimensión de la línea (ej. 25cm)")
    tipo_fin = st.selectbox("Tipo de objeto de destino", ["Item", "BRK", "SPL"])

    if st.button("Dibujar línea"):
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
        st.write(f"🔹 Línea de ({x1}, {y1}) a ({x2}, {y2}) con dimensión {dimension}")
        draw_symbol(x1, y1, tipo_inicio)
        draw_symbol(x2, y2, tipo_fin)
        st.write(f"📏 Dimensión mostrada en ({xm}, {ym})")

if st.session_state.lines:
    st.subheader("Líneas dibujadas")
    for i, line in enumerate(st.session_state.lines):
        st.write(f"{i+1}. De {line['inicio']} a {line['fin']} | Dimensión: {line['dimension']} | Inicio: {line['tipo_inicio']} | Fin: {line['tipo_fin']}")
