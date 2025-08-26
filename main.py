import streamlit as st
import plotly.graph_objects as go
from math import sqrt

# Clase para representar una línea eléctrica
class Linea:
    def __init__(self, punto1, punto2, objeto1, objeto2):
        self.punto1 = punto1
        self.punto2 = punto2
        self.objeto1 = objeto1
        self.objeto2 = objeto2
        self.longitud = self.calcular_longitud()

    def calcular_longitud(self):
        x1, y1 = self.punto1
        x2, y2 = self.punto2
        return round(sqrt((x2 - x1)**2 + (y2 - y1)**2), 2)

# Función para calcular distancia entre dos puntos
def distancia(p1, p2):
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Buscar extremo cercano para conectar
def encontrar_extremo_mas_cercano(punto, lineas, umbral=30):
    extremos = [linea.punto1 for linea in lineas] + [linea.punto2 for linea in lineas]
    for extremo in extremos:
        if distancia(punto, extremo) < umbral:
            return extremo
    return punto

# Inicializar sesión
if 'lineas' not in st.session_state:
    st.session_state.lineas = []
if 'punto_temp' not in st.session_state:
    st.session_state.punto_temp = None

st.sidebar.title("Herramientas")
objeto1 = st.sidebar.selectbox("Objeto extremo 1", ['Conector', 'BRK', 'SPL'])
objeto2 = st.sidebar.selectbox("Objeto extremo 2", ['Conector', 'BRK', 'SPL'])

st.title("Plano eléctrico interactivo")

# Crear figura Plotly
fig = go.Figure()
fig.update_layout(
    clickmode='event+select',
    dragmode='drawopenpath',
    margin=dict(l=20, r=20, t=20, b=20),
    width=700,
    height=500
)

# Dibujar líneas existentes
for linea in st.session_state.lineas:
    x1, y1 = linea.punto1
    x2, y2 = linea.punto2
    fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', line=dict(width=3)))
    # Mostrar longitud en el centro
    xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
    fig.add_trace(go.Scatter(x=[xm], y=[ym], mode='text', text=[f"{linea.longitud} px"], textposition="top center"))

# Mostrar figura y capturar clics
st.plotly_chart(fig)

# Capturar clics manualmente (simulado para ejemplo)
clicked_x = st.number_input("X del clic", min_value=0, max_value=700, step=1)
clicked_y = st.number_input("Y del clic", min_value=0, max_value=500, step=1)
if st.button("Agregar punto"):
    nuevo_punto = (clicked_x, clicked_y)
    nuevo_punto = encontrar_extremo_mas_cercano(nuevo_punto, st.session_state.lineas)
    if st.session_state.punto_temp is None:
        st.session_state.punto_temp = nuevo_punto
    else:
        nueva_linea = Linea(st.session_state.punto_temp, nuevo_punto, objeto1, objeto2)
        st.session_state.lineas.append(nueva_linea)
        st.session_state.punto_temp = None

# Mostrar tabla de líneas
st.subheader("Líneas dibujadas")
for i, linea in enumerate(st.session_state.lineas):
    st.text(f"Línea {i+1}: {linea.punto1} -> {linea.punto2}, {linea.objeto1}-{linea.objeto2}, {linea.longitud} px")
