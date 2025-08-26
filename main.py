import streamlit as st
from streamlit_drawable_canvas import st_canvas
import math

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
    if objects:
        last_obj = objects[-1]
        if last_obj["type"] == "line":
            x1, y1 = last_obj["x1"], last_obj["y1"]
            x2, y2 = last_obj["x2"], last_obj["y2"]

            # Buscar extremo más cercano
            min_dist = float("inf")
            closest_point = None
            for line in st.session_state.line_objects:
                for pt in [line["start"], line["end"]]:
                    d1 = distance((x1, y1), pt)
                    d2 = distance((x2, y2), pt)
                    if d1 < min_dist:
                        min_dist = d1
                        closest_point = pt
                        connect_start = True
                    if d2 < min_dist:
                        min_dist = d2
                        closest_point = pt
                        connect_start = False

            # Ajustar punto de conexión si hay uno cercano
            threshold = 20
            if min_dist < threshold:
                if connect_start:
                    x1, y1 = closest_point
                else:
                    x2, y2 = closest_point

            # Crear objeto línea con propiedades
            line_id = len(st.session_state.line_objects)
            dimension = st.sidebar.text_input("Dimensión de la línea (mm)", key=f"dim_{line_id}")
            tipo_inicio = st.sidebar.selectbox("Tipo de objeto de inicio", ["Item", "BRK", "SPL"], key=f"tipo_inicio_{line_id}")
            tipo_fin = st.sidebar.selectbox("Tipo de objeto de destino", ["Item", "BRK", "SPL"], key=f"tipo_fin_{line_id}")

            new_line = {
                "id": line_id,
                "start": (x1, y1),
                "end": (x2, y2),
                "dimension": dimension,
                "tipo_inicio": tipo_inicio,
                "tipo_fin": tipo_fin
            }

            # Agregar línea al estado
            st.session_state.line_objects.append(new_line)
