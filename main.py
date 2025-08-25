import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import math

st.set_page_config(layout="wide")
st.title("🛠️ Plano de Arneses Eléctricos")

# Estado inicial
if "modo_dibujo" not in st.session_state:
    st.session_state.modo_dibujo = False
if "fase_dibujo" not in st.session_state:
    st.session_state.fase_dibujo = "esperando_origen"
if "nodos" not in st.session_state:
    st.session_state.nodos = []
if "ramales" not in st.session_state:
    st.session_state.ramales = []
if "temp_origen" not in st.session_state:
    st.session_state.temp_origen = {}

# 🧭 Panel lateral
with st.sidebar:
    st.header("🔧 Herramientas")
    st.session_state.modo_dibujo = st.checkbox("Activar modo dibujo", value=st.session_state.modo_dibujo)

    if st.session_state.modo_dibujo and st.session_state.fase_dibujo == "origen_tipo":
        tipo = st.selectbox("Tipo de objeto origen", ["Conector", "SPL", "BRK"])
        st.session_state.temp_origen["tipo"] = tipo
        if st.button("Confirmar origen"):
            st.session_state.nodos.append({
                "nombre": f"{tipo}{len(st.session_state.nodos)+1}",
                "tipo": tipo,
                "x": st.session_state.temp_origen["x"],
                "y": st.session_state.temp_origen["y"]
            })
            st.session_state.temp_origen["nombre"] = st.session_state.nodos[-1]["nombre"]
            st.session_state.fase_dibujo = "esperando_destino"

    elif st.session_state.modo_dibujo and st.session_state.fase_dibujo == "destino_tipo":
        tipo = st.selectbox("Tipo de objeto destino", ["Conector", "SPL", "BRK"])
        dimension = st.number_input("Dimensión (mm)", value=100)
        st.session_state.temp_origen["destino_tipo"] = tipo
        st.session_state.temp_origen["dimension"] = dimension
        if st.button("Confirmar destino"):
            st.session_state.nodos.append({
                "nombre": f"{tipo}{len(st.session_state.nodos)+1}",
                "tipo": tipo,
                "x": st.session_state.temp_origen["dest_x"],
                "y": st.session_state.temp_origen["dest_y"]
            })
            st.session_state.ramales.append({
                "origen": st.session_state.temp_origen["nombre"],
                "destino": st.session_state.nodos[-1]["nombre"],
                "dimension": dimension
            })
            st.session_state.fase_dibujo = "esperando_origen"
            st.success("Línea dibujada correctamente")

# 🖼️ Área de dibujo
fig = go.Figure()

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

# Configuración del gráfico
fig.update_layout(
    width=1200,
    height=700,
    margin=dict(t=50, b=50),
    showlegend=False,
    dragmode=False,
    xaxis=dict(range=[0, 1000], visible=False),
    yaxis=dict(range=[0, 700], visible=False),
    modebar=dict(remove=["zoom", "pan", "select", "lasso"])
)

# Capturar clic
if st.session_state.modo_dibujo:
    st.subheader("🖱️ Haz clic en el plano para colocar nodos")
    selected = plotly_events(fig, click_event=True, override_height=700)

    if selected:
        x = selected[0]["x"]
        y = selected[0]["y"]
        if st.session_state.fase_dibujo == "esperando_origen":
            st.session_state.temp_origen = {"x": x, "y": y}
            st.session_state.fase_dibujo = "origen_tipo"
        elif st.session_state.fase_dibujo == "esperando_destino":
            st.session_state.temp_origen["dest_x"] = x
            st.session_state.temp_origen["dest_y"] = y
            st.session_state.fase_dibujo = "destino_tipo"

# Mostrar gráfico
st.plotly_chart(fig, use_container_width=True)
