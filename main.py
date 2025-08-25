import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

st.title("🛠️ Calculador de rutas para arneses eléctricos")

# Crear grafo vacío
G = nx.Graph()

# Añadir conectores y ramales manualmente
ramales = {
    ("A", "B"): 120,
    ("B", "C"): 80,
    ("C", "D"): 100,
    ("A", "D"): 150
}

# Construir grafo
for (n1, n2), distancia in ramales.items():
    G.add_edge(n1, n2, weight=distancia)

# Dibujar grafo
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1000)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
st.pyplot(plt)

# Subir archivo Excel
archivo = st.file_uploader("📥 Cargar archivo Excel con circuitos", type=["xlsx"])
if archivo:
    df = pd.read_excel(archivo)
    st.write("📋 Circuitos cargados:")
    st.dataframe(df)

    resultados = []
    for _, row in df.iterrows():
        origen = row["Conector_origen"]
        destino = row["Conector_destino"]
        try:
            ruta = nx.shortest_path(G, origen, destino, weight='weight')
            longitud = sum(G[u][v]['weight'] for u, v in zip(ruta[:-1], ruta[1:]))
            resultados.append({
                "Circuito": f"{origen} → {destino}",
                "Ruta": " → ".join(ruta),
                "Longitud (mm)": longitud
            })
        except:
            resultados.append({
                "Circuito": f"{origen} → {destino}",
                "Ruta": "No encontrada",
                "Longitud (mm)": "Error"
            })

    st.write("📏 Resultados de cálculo:")
    st.dataframe(pd.DataFrame(resultados))