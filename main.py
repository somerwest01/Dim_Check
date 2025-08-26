import streamlit as st
from streamlit_drawable_canvas import st_canvas
import math
import uuid

# Configuración de la página
st.set_page_config(page_title="Plano de Arnés Eléctrico", layout="wide")

# Panel lateral
st.sidebar.title("Panel de Herramientas")

# Inicializar almacenamiento de líneas como objetos con propiedades
if "line_objects" not in st.session_state:
    st.session_state.line_objects = []

# Área principal
st.title("Área de Dibujo")

# Canvas interactivo
canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0.3)",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#ffffff",
    update_streamlit=True,
    height=600,
    width=1000,
    drawing_mode="line",
    key="canvas",
)

# Función para calcular distancia entre dos puntos
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Procesar líneas dibujadas
if canvas_result.json_data is not None:
    objects = canvas_result.json_data.get("objects", [])
    new_lines = []
    for obj in objects:
        if obj["type"] == "line":
            x1, y1 = obj["x1"], obj["y1"]
            x2, y2 = obj["x2"], obj["y2"]

            # Buscar extremo más cercano
            min_dist = float("inf")
            closest_point = None
            connect_point = None
            for line in st.session_state.line_objects:
                for pt in [line["start"], line["end"]]:
                    d1 = distance((x1, y1), pt)
                    if d1 < min_dist:
                        min_dist = d1
                        closest_point = pt
                        connect_point = "start"
                    d2 = distance((x2, y2), pt)
                    if d2 < min_dist:
                        min_dist = d2
                        closest_point = pt
                        connect_point = "end"

            # Ajustar punto de conexión si hay uno cercano
            threshold = 20
            if min_dist < threshold:
                if connect_point == "start":
                    x1, y1 = closest_point
                elif connect_point == "end":
                    x2, y2 = closest_point

            # Generar clave única para widgets
            unique_key = str(uuid.uuid4())
            dimension = st.sidebar.text_input("Dimensión de la línea (mm)", key=f"dim_{unique_key}")

            new_line = {
                "id": unique_key,
                "start": (x1, y1),
                "end": (x2, y2),
                "dimension": dimension
            }

            new_lines.append(new_line)

    # Actualizar estado con nuevas líneas
    st.session_state.line_objects = new_lines
print("Archivo main.py corregido para evitar claves duplicadas en widgets.")

