import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import math

st.set_page_config(layout="wide")
st.title("🛠️ Plano Interactivo de Arneses Eléctricos")

# Estado inicial
if "nodos" not in st.session_state:
    st.session_state.nodos = []
if "ramales" not in st.session_state:
    st.session_state.ramales = []
if "conector_origen" not in st.session_state:
    st.session_state.conector_origen = None
if "ultimo_nodo" not in st.session_state:
    st.session_state.ultimo_nodo = None

# Parámetros de entrada
with st.sidebar:
    st.header("➕ Configurar Ramal")
    tipo_destino = st.selectbox("Tipo de destino", ["SPL", "BRK", "Conector"])
    nombre_destino = st.text_input("Nombre del destino", "SPL1" if tipo_destino == "SPL" else "C2")
    dimension = st.number_input("Dimensión (mm)", value=100)

# Función para encontrar nodo cercano
def encontrar_nodo_cercano(x, y, radio=30):
    for nodo in st.session_state.nodos:
        dist = math.hypot(nodo["x"] - x, nodo["y"] - y)
        if dist <= radio:
            return nodo
    return None

# Crear gráfico base
fig = go.Figure()
fig.update_layout(
    width=1200,
    height=700,
    margin=dict(t=50, b=50),
    showlegend=False,
    xaxis=dict(range=[0, 1000], visible=False),
    yaxis=dict(range=[0, 700], visible=False)
)

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

# Dibujar ramales
for ramal in st.session_state.ramales:
    origen = next(n for n in st.session_state.nodos if n["nombre"] == ramal["origen"])
    destino = next(n for n in st.session_state.nodos if n["nombre"] == ramal["destino"])
    x1, y1 = origen["x"], origen["y"]
    x2, y2 = destino["x"], destino["y"]
    xm, ym = (x1 + x2) / 2, (y1 + y2) / 2

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

# Capturar clic
st.subheader("🖱️ Haz clic en el plano para colocar nodos")
selected_points = plotly_events(fig, click_event=True, hover_event=False)

if selected_points:
    x = selected_points[0]["x"]
    y = selected_points[0]["y"]

    if st.session_state.conector_origen is None:
        # Primer nodo: Conector origen
        st.session_state.conector_origen = "C1"
        st.session_state.nodos.append({"nombre": "C1", "tipo": "Conector", "x": x, "y": y})
        st.session_state.ultimo_nodo = "C1"
        st.success("Conector origen 'C1' creado")
    else:
        nodo_origen = encontrar_nodo_cercano(x, y)
        if nodo_origen:
            # Conectar desde nodo cercano
            nombre = nombre_destino if tipo_destino != "BRK" else f"BRK{len(st.session_state.nodos)}"
            st.session_state.nodos.append({"nombre": nombre, "tipo": tipo_destino, "x": x, "y": y})
            st.session_state.ramales.append({
                "origen": nodo_origen["nombre"],
                "destino": nombre,
                "dimension": dimension
            })
            st.success(f"Línea creada: {nodo_origen['nombre']} → {nombre} ({dimension} mm)")
        else:
            st.warning("Haz clic cerca de un nodo existente para conectar")
