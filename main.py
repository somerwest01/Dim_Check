import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import math
import json
import os
from streamlit_plotly_events import plotly_events

st.set_page_config(page_title="AutoCAD Arneses Eléctricos", layout="wide")

# Inicializar estado de la aplicación
if "lines" not in st.session_state:
    st.session_state.lines = []
if "points" not in st.session_state:
    st.session_state.points = []
if "drawing_mode" not in st.session_state:
    st.session_state.drawing_mode = False
if "current_line" not in st.session_state:
    st.session_state.current_line = None
if "selected_point" not in st.session_state:
    st.session_state.selected_point = None
if "line_counter" not in st.session_state:
    st.session_state.line_counter = 1

# Funciones auxiliares
def calculate_distance(point1, point2):
    """Calcula la distancia entre dos puntos"""
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def find_nearest_point(click_pos, threshold=30):
    """Encuentra el punto más cercano al click dentro del umbral"""
    if not st.session_state.points:
        return None
    
    min_distance = float('inf')
    nearest_point = None
    
    for point in st.session_state.points:
        distance = calculate_distance(click_pos, (point['x'], point['y']))
        if distance < threshold and distance < min_distance:
            min_distance = distance
            nearest_point = point
    
    return nearest_point

def add_point(x, y, point_type, name):
    """Agregar un nuevo punto"""
    point = {
        'id': len(st.session_state.points),
        'x': x,
        'y': y,
        'type': point_type,
        'name': name
    }
    st.session_state.points.append(point)
    return point

def add_line(start_point, end_point, dimension):
    """Agregar una nueva línea"""
    line = {
        'id': st.session_state.line_counter,
        'start': start_point,
        'end': end_point,
        'dimension': dimension,
        'length': calculate_distance((start_point['x'], start_point['y']), (end_point['x'], end_point['y']))
    }
    st.session_state.lines.append(line)
    st.session_state.line_counter += 1
    return line

def get_connected_lines(point_id):
    """Obtiene todas las líneas conectadas a un punto"""
    connected = []
    for line in st.session_state.lines:
        if line['start']['id'] == point_id or line['end']['id'] == point_id:
            connected.append(line)
    return connected

def calculate_circuit_length(start_point_id):
    """Calcula la longitud total de un circuito"""
    visited = set()
    total_length = 0
    
    def dfs(point_id):
        nonlocal total_length
        if point_id in visited:
            return
        visited.add(point_id)
        
        connected_lines = get_connected_lines(point_id)
        for line in connected_lines:
            if line['id'] not in visited:
                total_length += line['dimension']
                next_point_id = line['end']['id'] if line['start']['id'] == point_id else line['start']['id']
                dfs(next_point_id)
    
    dfs(start_point_id)
    return total_length

# CSS personalizado
st.markdown("""
<style>
    .toolbar {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .drawing-area {
        border: 2px solid #ddd;
        border-radius: 10px;
        background-color: white;
    }
    .status-bar {
        background-color: #e1e5f2;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("🚗 AutoCAD - Diseño de Arneses Eléctricos")

# Crear layout principal
col_toolbar, col_drawing = st.columns([1, 3])

# Panel de herramientas (izquierda)
with col_toolbar:
    st.markdown('<div class="toolbar">', unsafe_allow_html=True)
    st.header("🛠️ Herramientas")
    
    # Botón principal para agregar línea
    if st.button("➕ Agregar Nueva Línea", use_container_width=True, type="primary"):
        st.session_state.drawing_mode = True
        st.session_state.current_line = {"step": "start"}
        st.rerun()
    
    # Estado actual
    if st.session_state.drawing_mode:
        if st.session_state.current_line["step"] == "start":
            st.info("🎯 **Paso 1:** Haz clic en el área de dibujo para definir el punto de inicio")
        elif st.session_state.current_line["step"] == "end":
            st.info("🎯 **Paso 2:** Haz clic para definir el punto final")
        elif st.session_state.current_line["step"] == "dimension":
            st.info("🎯 **Paso 3:** Ingresa la dimensión de la línea")
    else:
        st.success("✅ Listo para dibujar. Presiona 'Agregar Nueva Línea' para comenzar.")
    
    st.divider()
    
    # Formularios flotantes simulados
    if st.session_state.drawing_mode:
        if st.session_state.current_line["step"] == "start_type":
            st.subheader("🔍 Tipo de Punto de Inicio")
            start_type = st.selectbox("Selecciona el tipo:", ["Item", "BRK", "SPL"], key="start_type_select")
            start_name = st.text_input("Nombre del punto:", value=f"{start_type}_{len(st.session_state.points)+1}")
            
            if st.button("✅ Confirmar Inicio"):
                # Crear punto de inicio
                start_point = add_point(
                    st.session_state.current_line["start_x"],
                    st.session_state.current_line["start_y"],
                    start_type,
                    start_name
                )
                st.session_state.current_line["start_point"] = start_point
                st.session_state.current_line["step"] = "end"
                st.rerun()
        
        elif st.session_state.current_line["step"] == "end_type":
            st.subheader("🔍 Tipo de Punto Final")
            end_type = st.selectbox("Selecciona el tipo:", ["Item", "BRK", "SPL"], key="end_type_select")
            end_name = st.text_input("Nombre del punto:", value=f"{end_type}_{len(st.session_state.points)+1}")
            
            if st.button("✅ Confirmar Final"):
                # Crear punto final
                end_point = add_point(
                    st.session_state.current_line["end_x"],
                    st.session_state.current_line["end_y"],
                    end_type,
                    end_name
                )
                st.session_state.current_line["end_point"] = end_point
                st.session_state.current_line["step"] = "dimension"
                st.rerun()
        
        elif st.session_state.current_line["step"] == "dimension":
            st.subheader("📏 Dimensión de la Línea")
            
            # Calcular distancia automáticamente como sugerencia
            if "start_point" in st.session_state.current_line and "end_point" in st.session_state.current_line:
                auto_distance = calculate_distance(
                    (st.session_state.current_line["start_point"]["x"], st.session_state.current_line["start_point"]["y"]),
                    (st.session_state.current_line["end_point"]["x"], st.session_state.current_line["end_point"]["y"])
                )
                st.info(f"📐 Distancia calculada: {auto_distance:.1f} píxeles")
            
            dimension = st.number_input("Dimensión (mm):", min_value=0.1, value=100.0, step=0.1)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Crear Línea"):
                    # Crear la línea
                    line = add_line(
                        st.session_state.current_line["start_point"],
                        st.session_state.current_line["end_point"],
                        dimension
                    )
                    
                    # Resetear modo de dibujo
                    st.session_state.drawing_mode = False
                    st.session_state.current_line = None
                    st.success(f"✅ Línea creada: {dimension} mm")
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancelar"):
                    st.session_state.drawing_mode = False
                    st.session_state.current_line = None
                    st.rerun()
    
    st.divider()
    
    # Información del proyecto
    st.subheader("📊 Estadísticas del Proyecto")
    st.metric("Total de Líneas", len(st.session_state.lines))
    st.metric("Total de Puntos", len(st.session_state.points))
    
    if st.session_state.lines:
        total_length = sum(line['dimension'] for line in st.session_state.lines)
        st.metric("Longitud Total", f"{total_length:.1f} mm")
    
    # Lista de líneas
    if st.session_state.lines:
        st.subheader("📋 Lista de Líneas")
        for i, line in enumerate(st.session_state.lines):
            with st.expander(f"Línea {line['id']}: {line['dimension']} mm"):
                st.write(f"**Inicio:** {line['start']['name']} ({line['start']['type']})")
                st.write(f"**Final:** {line['end']['name']} ({line['end']['type']})")
                st.write(f"**Dimensión:** {line['dimension']} mm")
                
                if st.button(f"🗑️ Eliminar", key=f"delete_{line['id']}"):
                    st.session_state.lines = [l for l in st.session_state.lines if l['id'] != line['id']]
                    st.rerun()
    
    # Botones de acción
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Guardar", use_container_width=True):
            project_data = {
                'lines': st.session_state.lines,
                'points': st.session_state.points,
                'counter': st.session_state.line_counter
            }
            
            if not os.path.exists('projects'):
                os.makedirs('projects')
            
            with open('projects/current_project.json', 'w') as f:
                json.dump(project_data, f, indent=2)
            st.success("💾 Proyecto guardado")
    
    with col2:
        if st.button("📂 Cargar", use_container_width=True):
            try:
                with open('projects/current_project.json', 'r') as f:
                    project_data = json.load(f)
                
                st.session_state.lines = project_data.get('lines', [])
                st.session_state.points = project_data.get('points', [])
                st.session_state.line_counter = project_data.get('counter', 1)
                st.success("📂 Proyecto cargado")
                st.rerun()
            except:
                st.error("❌ No se pudo cargar el proyecto")
    
    if st.button("🗑️ Limpiar Todo", use_container_width=True):
        st.session_state.lines = []
        st.session_state.points = []
        st.session_state.line_counter = 1
        st.session_state.drawing_mode = False
        st.session_state.current_line = None
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Área de dibujo (derecha)
with col_drawing:
    st.markdown('<div class="drawing-area">', unsafe_allow_html=True)
    st.subheader("📐 Área de Dibujo")
    
    # Crear figura de Plotly
    fig = go.Figure()
    
    # Dibujar líneas existentes
    for line in st.session_state.lines:
        start_x, start_y = line['start']['x'], line['start']['y']
        end_x, end_y = line['end']['x'], line['end']['y']
        
        # Línea
        fig.add_trace(go.Scatter(
            x=[start_x, end_x],
            y=[start_y, end_y],
            mode='lines',
            line=dict(color='black', width=3),
            showlegend=False,
            hoverinfo='none'
        ))
        
        # Texto de dimensión en el medio de la línea
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        fig.add_trace(go.Scatter(
            x=[mid_x],
            y=[mid_y],
            mode='text',
            text=[f"{line['dimension']} mm"],
            textposition='middle center',
            textfont=dict(size=12, color='blue'),
            showlegend=False,
            hoverinfo='none'
        ))
    
    # Dibujar puntos
    for point in st.session_state.points:
        if point['type'] == 'Item':
            # Cuadrado
            symbol = 'square'
            color = 'blue'
        elif point['type'] == 'BRK':
            # Círculo relleno negro
            symbol = 'circle'
            color = 'black'
        elif point['type'] == 'SPL':
            # Triángulo
            symbol = 'triangle-up'
            color = 'green'
        
        fig.add_trace(go.Scatter(
            x=[point['x']],
            y=[point['y']],
            mode='markers+text',
            marker=dict(symbol=symbol, size=15, color=color),
            text=[point['name']],
            textposition='bottom center',
            textfont=dict(size=10),
            showlegend=False,
            hoverinfo='text',
            hovertext=f"{point['name']} ({point['type']})"
        ))
    
    # Configurar el layout
    fig.update_layout(
        width=800,
        height=600,
        xaxis=dict(
            range=[0, 1000],
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            title="X (mm)"
        ),
        yaxis=dict(
            range=[0, 600],
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            title="Y (mm)"
        ),
        plot_bgcolor='white',
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # Configurar interacciones según el modo
    if st.session_state.drawing_mode:
        fig.update_layout(
            dragmode='pan'
        )
        # Configurar la barra de herramientas
        config = {
            'displayModeBar': False,
            'scrollZoom': False,
            'doubleClick': False,
            'showTips': False
        }
    
    # Mostrar el gráfico con eventos de click reales
    if st.session_state.drawing_mode:
        selected_points = plotly_events(
            fig, 
            click_event=True, 
            hover_event=False,
            select_event=False,
            override_height=600,
            override_width="100%",
            key="drawing_canvas",
            config={'displayModeBar': False, 'scrollZoom': False}
        )
    else:
        selected_points = plotly_events(
            fig, 
            click_event=True, 
            hover_event=False,
            select_event=False,
            override_height=600,
            override_width="100%",
            key="drawing_canvas"
        )
    
    # Procesar clicks del mouse
    if selected_points and st.session_state.drawing_mode:
        # Obtener el último click válido
        for point_data in reversed(selected_points):
            if 'x' in point_data and 'y' in point_data:
                click_x = float(point_data['x'])
                click_y = float(point_data['y'])
                break
        else:
            click_x = click_y = None
        
        if click_x is not None and click_y is not None:
            if st.session_state.current_line["step"] == "start":
                # Verificar si hay un punto cercano
                nearest = find_nearest_point((click_x, click_y))
                if nearest:
                    st.session_state.current_line["start_point"] = nearest
                    st.session_state.current_line["step"] = "end"
                    st.success(f"✅ Conectado al punto existente: {nearest['name']}")
                    st.rerun()
                else:
                    st.session_state.current_line["start_x"] = click_x
                    st.session_state.current_line["start_y"] = click_y
                    st.session_state.current_line["step"] = "start_type"
                    st.rerun()
            
            elif st.session_state.current_line["step"] == "end":
                # Verificar si hay un punto cercano
                nearest = find_nearest_point((click_x, click_y))
                if nearest:
                    st.session_state.current_line["end_point"] = nearest
                    st.session_state.current_line["step"] = "dimension"
                    st.success(f"✅ Conectado al punto existente: {nearest['name']}")
                    st.rerun()
                else:
                    st.session_state.current_line["end_x"] = click_x
                    st.session_state.current_line["end_y"] = click_y
                    st.session_state.current_line["step"] = "end_type"
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mostrar información de clicks cuando estemos dibujando
    if st.session_state.drawing_mode:
        st.info("🖱️ **MODO DIBUJO ACTIVO** - Haz clic en el área del gráfico")
        if selected_points:
            try:
                click_data = selected_points[-1]
                if 'x' in click_data and 'y' in click_data:
                    st.success(f"✅ Click detectado en: X={click_data['x']:.1f}, Y={click_data['y']:.1f}")
            except:
                st.warning("⚠️ Click detectado pero con formato incorrecto")

# Barra de estado
st.markdown('<div class="status-bar">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    if st.session_state.drawing_mode:
        st.write("🟢 **Modo Dibujo Activo**")
    else:
        st.write("⚪ **Modo Vista**")

with col2:
    st.write(f"📏 **Líneas:** {len(st.session_state.lines)}")

with col3:
    if st.session_state.lines:
        total = sum(line['dimension'] for line in st.session_state.lines)
        st.write(f"📐 **Total:** {total:.1f} mm")

st.markdown('</div>', unsafe_allow_html=True)
