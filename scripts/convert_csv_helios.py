import networkx as nx
import pandas as pd

# Carregar o arquivo CSV
df = pd.read_csv('data/filtered_connections.csv')

# Criar o grafo
G = nx.Graph()

# Adicionar nós e arestas
for _, row in df.iterrows():
    G.add_edge(row['deputado_a'], row['deputado_b'], weight=row['peso'])

# Salvar o grafo em formato GML
nx.write_gml(G, 'data/filtered_graph.gml')

# Se precisar em formato XNET
# nx.write_edgelist(G, 'graph.xnet', data=False)

# Se precisar em formato GEXF
# nx.write_gexf(G, 'graph.gexf')