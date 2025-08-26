import streamlit as st
import plotly.graph_objects as go
import json
import os

st.set_page_config(layout="wide")
st.title("🛠️ Plano de Arneses Eléctricos")

# Espacio para barra de estado
status = st.empty()

# Datos temporales
if "ramales" not in st.session_state:
    st.session_state.ramales = []

if "editing_index" not in st.session_state:
    st.session_state.editing_index = None

# Funciones para guardar/cargar
def save_design(filename, ramales):
    designs_dir = "designs"
    if not os.path.exists(designs_dir):
        os.makedirs(designs_dir)
    
    with open(f"{designs_dir}/{filename}.json", "w") as f:
        json.dump(ramales, f, indent=2)

def load_design(filename):
    try:
        with open(f"designs/{filename}", "r") as f:
            return json.load(f)
    except:
        return []

def get_saved_designs():
    designs_dir = "designs"
    if not os.path.exists(designs_dir):
        return []
    return [f for f in os.listdir(designs_dir) if f.endswith('.json')]

# Barra lateral principal
with st.sidebar:
    st.header("🎛️ Panel de Control")
    
    # Sección de guardado/carga
    st.subheader("💾 Guardar/Cargar Diseño")
    
    col1, col2 = st.columns(2)
    with col1:
        save_name = st.text_input("Nombre del diseño", placeholder="mi_arnes")
        if st.button("💾 Guardar", use_container_width=True):
            if save_name:
                save_design(save_name, st.session_state.ramales)
                status.success(f"Diseño guardado como: {save_name}.json")
            else:
                status.error("Ingresa un nombre para el diseño")
    
    with col2:
        saved_designs = get_saved_designs()
        if saved_designs:
            selected_design = st.selectbox("Diseños guardados", saved_designs)
            if st.button("📂 Cargar", use_container_width=True):
                loaded_ramales = load_design(selected_design)
                st.session_state.ramales = loaded_ramales
                st.session_state.editing_index = None
                status.success(f"Diseño cargado: {selected_design}")
                st.rerun()

    if st.button("🗑️ Nuevo Diseño", use_container_width=True):
        st.session_state.ramales = []
        st.session_state.editing_index = None
        status.info("Nuevo diseño iniciado")
        st.rerun()

    st.divider()

    # Sección para agregar/editar ramal
    if st.session_state.editing_index is not None:
        st.subheader("✏️ Editar Ramal")
        ramal_actual = st.session_state.ramales[st.session_state.editing_index]
        
        origen = st.text_input("Nombre del Conector (origen)", value=ramal_actual["origen"])
        tipo_destino = st.selectbox("Tipo de destino", ["SPL", "BRK", "Conector"], 
                                   index=["SPL", "BRK", "Conector"].index(ramal_actual["tipo"]))
        nombre_destino = st.text_input("Nombre del destino", value=ramal_actual["destino"])
        x1 = st.number_input("X origen", value=ramal_actual["coords"][0][0])
        y1 = st.number_input("Y origen", value=ramal_actual["coords"][0][1])
        x2 = st.number_input("X destino", value=ramal_actual["coords"][1][0])
        y2 = st.number_input("Y destino", value=ramal_actual["coords"][1][1])
        dimension = st.number_input("Dimensión (mm)", value=ramal_actual["dimension"])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Guardar cambios", use_container_width=True):
                st.session_state.ramales[st.session_state.editing_index] = {
                    "origen": origen,
                    "destino": nombre_destino if tipo_destino != "BRK" else "BRK",
                    "tipo": tipo_destino,
                    "dimension": dimension,
                    "coords": [(x1, y1), (x2, y2)]
                }
                st.session_state.editing_index = None
                status.success("Ramal actualizado correctamente")
                st.rerun()
        
        with col2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.editing_index = None
                st.rerun()
    
    else:
        st.subheader("➕ Agregar Ramal")
        origen = st.text_input("Nombre del Conector (origen)", "C1")
        tipo_destino = st.selectbox("Tipo de destino", ["SPL", "BRK", "Conector"])
        nombre_destino = st.text_input("Nombre del destino", "SPL1" if tipo_destino == "SPL" else "C2")
        x1 = st.number_input("X origen", value=100)
        y1 = st.number_input("Y origen", value=300)
        x2 = st.number_input("X destino", value=300)
        y2 = st.number_input("Y destino", value=300)
        dimension = st.number_input("Dimensión (mm)", value=100)

        if st.button("➕ Agregar línea", use_container_width=True):
            st.session_state.ramales.append({
                "origen": origen,
                "destino": nombre_destino if tipo_destino != "BRK" else "BRK",
                "tipo": tipo_destino,
                "dimension": dimension,
                "coords": [(x1, y1), (x2, y2)]
            })
            status.success(f"Línea agregada: {origen} → {nombre_destino} ({dimension} mm)")
            st.rerun()

# Panel principal con dos columnas
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📐 Plano del Arnés")
    
    # Dibujo del plano
    fig = go.Figure()

    # Dibujar cada ramal
    for i, ramal in enumerate(st.session_state.ramales):
        x1, y1 = ramal["coords"][0]
        x2, y2 = ramal["coords"][1]

        # Color de línea diferente si está siendo editado
        line_color = "red" if i == st.session_state.editing_index else "gray"
        line_width = 3 if i == st.session_state.editing_index else 2

        # Línea
        fig.add_trace(go.Scatter(
            x=[x1, x2], y=[y1, y2],
            mode="lines+text",
            line=dict(color=line_color, width=line_width),
            text=[None, f'{ramal["dimension"]} mm'],
            textposition="top center",
            hoverinfo="none",
            showlegend=False
        ))

        # Nodo destino
        if ramal["tipo"] == "Conector":
            fig.add_trace(go.Scatter(
                x=[x2], y=[y2],
                mode="markers+text",
                marker=dict(symbol="square", size=14, color="blue"),
                text=[ramal["destino"]],
                textposition="bottom center",
                showlegend=False
            ))
        elif ramal["tipo"] == "SPL":
            fig.add_trace(go.Scatter(
                x=[x2], y=[y2],
                mode="markers+text",
                marker=dict(symbol="triangle-up", size=14, color="green"),
                text=[ramal["destino"]],
                textposition="bottom center",
                showlegend=False
            ))
        elif ramal["tipo"] == "BRK":
            fig.add_trace(go.Scatter(
                x=[x2], y=[y2],
                mode="markers",
                marker=dict(symbol="circle", size=14, color="black"),
                showlegend=False
            ))

        # Nodo origen (siempre Conector)
        fig.add_trace(go.Scatter(
            x=[x1], y=[y1],
            mode="markers+text",
            marker=dict(symbol="square", size=14, color="blue"),
            text=[ramal["origen"]],
            textposition="bottom center",
            showlegend=False
        ))

    fig.update_layout(
        width=800,
        height=600,
        margin=dict(t=20, b=20),
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📋 Lista de Ramales")
    
    if st.session_state.ramales:
        for i, ramal in enumerate(st.session_state.ramales):
            with st.container():
                # Indicador visual si está siendo editado
                if i == st.session_state.editing_index:
                    st.markdown("🔴 **EDITANDO**")
                
                st.write(f"**{i+1}.** {ramal['origen']} → {ramal['destino']}")
                st.write(f"📏 {ramal['dimension']} mm | 🔧 {ramal['tipo']}")
                
                col_edit, col_delete = st.columns(2)
                
                with col_edit:
                    if st.button("✏️", key=f"edit_{i}", help="Editar", use_container_width=True):
                        st.session_state.editing_index = i
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️", key=f"delete_{i}", help="Eliminar", use_container_width=True):
                        st.session_state.ramales.pop(i)
                        if st.session_state.editing_index == i:
                            st.session_state.editing_index = None
                        elif st.session_state.editing_index is not None and st.session_state.editing_index > i:
                            st.session_state.editing_index -= 1
                        status.warning(f"Ramal eliminado")
                        st.rerun()
                
                st.divider()
    else:
        st.info("No hay ramales agregados aún")

# Información del diseño
if st.session_state.ramales:
    st.info(f"💡 **Resumen:** {len(st.session_state.ramales)} ramales | "
            f"Total: {sum(r['dimension'] for r in st.session_state.ramales)} mm")
