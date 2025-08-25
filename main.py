import streamlit as st
import plotly.graph_objects as go
import math

st.set_page_config(layout="wide")
st.title("🛠️ Plano Interactivo de Arneses Eléctricos")

# Inicializar estado
if "nodos" not in st.session_state:
    st.session_state.nodos = []  # Lista de dicts: {"nombre", "tipo", "x", "y"}
if "ramales" not in st.session_state:
    st.session_state.ramales = []  # Lista de dicts: {"origen", "destino", "dimension"}
if "conector_origen" not in st.session_state:
    st.session_state.conector_origen = None

# Parámetros de entrada
with st.sidebar:
    st.header("➕ Configurar Ramal")
    tipo_destino = st.selectbox("Tipo de destino", ["SPL", "BRK", "Conector"])
    nombre_destino = st.text_input("Nombre del destino", "SPL1" if tipo_destino == "SPL" else "C2")
    dimension = st.number_input("Dimensión (mm)", value=100)

# Función para encontrar nodo más cercano
def encontrar_nodo_cercano(x, y, radio=30):
    for nodo in st.session_state.nodos:
        dist = math.hypot(nodo["x"] - x, nodo["y"] - y)
        if dist <= radio:
            return nodo
    return None

# Captura de clic
clicked_point = st.experimental_data_editor({"x": [], "y": []}, num_rows="dynamic", use_container_width=True)

if clicked_point["x"] and clicked_point["y"]:
    x = clicked_point["x"][-1]
    y = clicked_point["y"][-1]

    if st.session_state.conector_origen is None:
        # Primer clic: crear Conector origen
        st.session_state.conector_origen = "C1"
        st.session_state.nodos.append({"nombre": "C1", "tipo": "Conector", "x": x, "y": y})
        st.success("Conector origen 'C1' creado")
    else:
        # Buscar nodo cercano como origen
        nodo_origen = encontrar_nodo_cercano(x, y)
        if nodo_origen:
            # Crear destino
            nombre = nombre_destino if tipo_destino != "BRK" else "BRK"
            st.session_state.nodos.append({"nombre": nombre, "tipo": tipo_destino, "x": x, "y": y})
            st.session_state.ramales.append({
                "origen": nodo_origen["nombre"],
                "destino": nombre,
                "dimension": dimension
            })
            st.success(f"Línea creada: {nodo_origen['nombre']} → {nombre} ({dimension} mm)")
        else:
            st.warning("Haz clic cerca de un nodo existente para conectar")

# Dibujo del plano
fig = go.Figure()

# Dibujar ramales
for ramal in st.session_state.ramales:
    origen = next(n for n in st.session_state.nodos if n["nombre"] == ramal["origen"])
    destino = next(n for n in st.session_state.nodos if n["nombre"] == ramal["destino"])
    x1, y1 = origen["x"], origen["y"]
    x2, y2 = destino["x"], destino["y"]

    # Punto medio para la dimensión
    xm = (x1 + x2) / 2
    ym = (y1 + y2) / 2

    fig.add_trace(go.Scatter(
        x=[x1, x2], y=[y1, y2],
        mode="lines",
        line=dict(color="gray", width=2),
        hoverinfo="none"
    ))

    fig.add_trace(go.Scatter(
        x=[xm], y=[ym],
        mode="text",
        text=[f'{ramal["dimension"]} mm'],
        textposition="top center",
        hoverinfo="none"
    ))

# Dibujar nodos
for nodo in st.session_state.nodos:
    simbolo = {"Conector": "square", "SPL": "triangle-up", "BRK": "circle"}[nodo["tipo"]]
    color = {"Conector": "blue", "SPL": "green", "BRK": "black"}[nodo["tipo"]]
    fig.add_trace(go.Scatter(
        x=[nodo["x"]], y=[nodo["y"]],
        mode="markers+text",
        marker=dict(symbol=simbolo, size=14, color=color),
        text=[nodo["nombre"] if nodo["tipo"] != "BRK" else ""],
        textposition="bottom center"
    ))

fig.update_layout(
    width=1200,
    height=700,
    margin=dict(t=50, b=50),
    showlegend=False,
    xaxis=dict(visible=False),
    yaxis=dict(visible=False)
)

st.plotly_chart(fig, use_container_width=True)
