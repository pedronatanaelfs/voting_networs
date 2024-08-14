import streamlit as st
import networkx as nx
import csv
import igraph as ig
import leidenalg as la
import streamlit.components.v1 as components  # Importar componentes do Streamlit

# Função para carregar as conexões a partir de um arquivo CSV
def load_connections_from_csv(file_path):
    connections = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            deputy_a = row['deputado_a']
            deputy_b = row['deputado_b']
            weight = float(row['peso'])
            connections[(deputy_a, deputy_b)] = weight
    return connections

# Função para detectar comunidades usando o algoritmo de Leiden
def detect_communities_leiden(connections):
    G = nx.Graph()
    for (deputy_a, deputy_b), weight in connections.items():
        G.add_edge(deputy_a, deputy_b, weight=weight)
    
    nx_g = nx.Graph(G)
    ig_g = ig.Graph.TupleList(nx_g.edges(), directed=False)
    partition = la.find_partition(ig_g, la.ModularityVertexPartition)
    
    community_dict = {node: community for community, nodes in enumerate(partition) for node in nodes}
    mapping = {i: v for i, v in enumerate(nx_g.nodes())}
    community_dict = {mapping[node]: community for node, community in community_dict.items()}
    nx.set_node_attributes(G, community_dict, 'community')

    pos = nx.spring_layout(G, seed=42)
    return G

# Carregar conexões do arquivo CSV
connections_csv_path = 'data/connections.csv'
connections = load_connections_from_csv(connections_csv_path)

# Detectar comunidades e obter o grafo G
G = detect_communities_leiden(connections)

# Função para preparar os dados do grafo para visualização
def prepare_graph_data(G, node_size, color_by_community=True):
    nodes = [{"id": str(node), "group": G.nodes[node].get('community', 1), "size": node_size} for node in G.nodes()]
    links = [{"source": str(u), "target": str(v)} for u, v in G.edges()]
    if color_by_community:
        for node in nodes:
            node['color'] = node['group']  # Colorir por comunidade
    return {"nodes": nodes, "links": links}

# Interface com Streamlit para ajustes de visualização
st.title("Graph Visualization with Leiden Communities")

# Configurações de tamanho do nó
node_size = st.slider("Node Size", min_value=1, max_value=20, value=10)

# Opção para colorir por comunidade
color_by_community = st.checkbox("Color by Community", value=True)

# Preparar os dados do grafo para visualização
graph_data = prepare_graph_data(G, node_size, color_by_community)

# Gerar o HTML para D3.js
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>D3.js Graph</title>
    <script src="https://d3js.org/d3.v6.min.js"></script>
</head>
<body>
    <div id="graph"></div>
    <script>
        var graph = {graph_data};  // Passando os dados do grafo aqui

        var width = 960,
            height = 500;

        var svg = d3.select("#graph").append("svg")
            .attr("width", width)
            .attr("height", height);

        var simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(function(d) {{ return d.id; }}))
            .force("charge", d3.forceManyBody())
            .force("center", d3.forceCenter(width / 2, height / 2));

        var link = svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(graph.links)
            .enter().append("line")
            .attr("stroke-width", function(d) {{ return Math.sqrt(d.value); }});

        var node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(graph.nodes)
            .enter().append("circle")
            .attr("r", function(d) {{ return d.size; }})  // Aplicar o tamanho dos nós
            .attr("fill", function(d) {{ return d.color || "blue"; }});  // Aplicar cor por comunidade ou padrão

        simulation
            .nodes(graph.nodes)
            .on("tick", ticked);

        simulation.force("link")
            .links(graph.links);

        function ticked() {{
            link
                .attr("x1", function(d) {{ return d.source.x; }})
                .attr("y1", function(d) {{ return d.source.y; }})
                .attr("x2", function(d) {{ return d.target.x; }})
                .attr("y2", function(d) {{ return d.target.y; }});

            node
                .attr("cx", function(d) {{ return d.x; }})
                .attr("cy", function(d) {{ return d.y; }});
        }}
    </script>
</body>
</html>
"""

# Renderizar o HTML com Streamlit
components.html(html_content, height=600)