import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🛠️ Plano de Arneses Eléctricos")

# Espacio para barra de estado
status = st.empty()

# Datos temporales
if "ramales" not in st.session_state:
    st.session_state.ramales = []

# Formulario para agregar ramal
with st.sidebar:
    st.header("➕ Agregar Ramal")
    origen = st.text_input("Nombre del Conector (origen)", "C1")
    tipo_destino = st.selectbox("Tipo de destino", ["SPL", "BRK", "Conector"])
    nombre_destino = st.text_input("Nombre del destino", "SPL1" if tipo_destino == "SPL" else "C2")
    x1 = st.number_input("X origen", value=100)
    y1 = st.number_input("Y origen", value=300)
    x2 = st.number_input("X destino", value=300)
    y2 = st.number_input("Y destino", value=300)
    dimension = st.number_input("Dimensión (mm)", value=100)

    if st.button("Agregar línea"):
        st.session_state.ramales.append({
            "origen": origen,
            "destino": nombre_destino if tipo_destino != "BRK" else "BRK",
            "tipo": tipo_destino,
            "dimension": dimension,
            "coords": [(x1, y1), (x2, y2)]
        })
        status.success(f"Línea agregada: {origen} → {nombre_destino} ({dimension} mm)")

# Dibujo del plano
fig = go.Figure()

# Dibujar cada ramal
for ramal in st.session_state.ramales:
    x1, y1 = ramal["coords"][0]
    x2, y2 = ramal["coords"][1]

    # Línea
    fig.add_trace(go.Scatter(
        x=[x1, x2], y=[y1, y2],
        mode="lines+text",
        line=dict(color="gray", width=2),
        text=[None, f'{ramal["dimension"]} mm'],
        textposition="top center",
        hoverinfo="none"
    ))

    # Nodo destino
    if ramal["tipo"] == "Conector":
        fig.add_trace(go.Scatter(
            x=[x2], y=[y2],
            mode="markers+text",
            marker=dict(symbol="square", size=14, color="blue"),
            text=[ramal["destino"]],
            textposition="bottom center"
        ))
    elif ramal["tipo"] == "SPL":
        fig.add_trace(go.Scatter(
            x=[x2], y=[y2],
            mode="markers+text",
            marker=dict(symbol="triangle-up", size=14, color="green"),
            text=[ramal["destino"]],
            textposition="bottom center"
        ))
    elif ramal["tipo"] == "BRK":
        fig.add_trace(go.Scatter(
            x=[x2], y=[y2],
            mode="markers",
            marker=dict(symbol="circle", size=14, color="black")
        ))

# Nodo origen (siempre Conector)
for ramal in st.session_state.ramales:
    x1, y1 = ramal["coords"][0]
    fig.add_trace(go.Scatter(
        x=[x1], y=[y1],
        mode="markers+text",
        marker=dict(symbol="square", size=14, color="blue"),
        text=[ramal["origen"]],
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