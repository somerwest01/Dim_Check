import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🛠️ Plano de Arneses Eléctricos")

# 🧭 Panel lateral de herramientas
with st.sidebar:
    st.header("🔧 Herramientas")
    zoom_activo = st.checkbox("Activar herramientas de zoom", value=False)

# 🖼️ Área de dibujo
fig = go.Figure()

# Configuración del gráfico
fig.update_layout(
    width=1200,
    height=700,
    margin=dict(t=50, b=50),
    showlegend=False,
    dragmode="zoom" if zoom_activo else False,
    xaxis=dict(range=[0, 1000], visible=False),
    yaxis=dict(range=[0, 700], visible=False),
    modebar=dict(remove=[] if zoom_activo else ["zoom", "pan", "select", "lasso"])
)

# Mostrar gráfico
st.plotly_chart(fig, use_container_width=True)
