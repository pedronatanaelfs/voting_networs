import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import leidenalg as la
import igraph as ig
from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score
import csv
import html

# Variables
Year = 2023
threshold = 0.3

# Calculate Connections Similarity
def calculate_connections_similarity(votacao):
    """
    Calculates the connections between deputies based on common votes.

    Args:
    votacao (DataFrame): DataFrame with votes that want to build the connections.

    Returns:
    dict: Dictionary of normalized connections between deputies.
    """
    # Initialize an empty dictionary to store connections
    connections = {}

    # Iterate over each proposition
    for proposition_id, votes in votacao.groupby('id_votacao'):
        # Get the list of deputies who voted on this proposition
        deputies = votes['id_deputado'].unique()
        
        # Create connections between each pair of deputies who voted the same on this proposition
        for i, deputy_a in enumerate(deputies):
            for deputy_b in deputies[i+1:]:
                if (deputy_a, deputy_b) not in connections:
                    connections[(deputy_a, deputy_b)] = 0
                connections[(deputy_a, deputy_b)] += 1

    print("Established connections between deputies")
    print(f"Sample connections: {list(connections.items())[:5]}")

    # Get the maximum weight
    max_weight = max(connections.values())
    print(f"Maximum weight: {max_weight}")

    # Normalize the weights
    for key in connections:
        connections[key] /= max_weight

    print("Normalized the weights")
    print(f"Sample normalized connections: {list(connections.items())[:5]}")

    return connections

# Threshold Prune
def filter_connections(connections, threshold):
    """
    Filtra as conexões mais fracas com base em um threshold definido pelo usuário.
    Caso um nó fique sem nenhuma conexão devido ao corte, mantém a sua conexão mais forte.

    Args:
    connections (dict): Dicionário de conexões entre deputados com pesos normalizados.
    threshold (float): Valor do threshold para filtrar as conexões.

    Returns:
    dict: Novo dicionário de conexões filtradas.
    """
    # Filtrar conexões com peso maior ou igual ao threshold
    filtered_connections = {key: value for key, value in connections.items() if value >= threshold}
    
    print(f"Filtered connections with threshold {threshold}")

    # Verificar se algum nó ficou sem conexões
    nodes_with_connections = {node for edge in filtered_connections.keys() for node in edge}
    all_nodes = {node for edge in connections.keys() for node in edge}
    
    isolated_nodes = all_nodes - nodes_with_connections
    
    for node in isolated_nodes:
        # Encontrar a conexão mais forte para o nó isolado
        strongest_connection = None
        max_weight = 0
        for (deputy_a, deputy_b), weight in connections.items():
            if node in (deputy_a, deputy_b) and weight > max_weight:
                strongest_connection = (deputy_a, deputy_b)
                max_weight = weight
        
        # Adicionar a conexão mais forte ao dicionário filtrado
        if strongest_connection:
            filtered_connections[strongest_connection] = max_weight
    
    print(f"Ensured no isolated nodes. Final connection count: {len(filtered_connections)}")
    return filtered_connections

# Leiden Community Detection
def detect_communities_leiden(connections):
    """
    Detecta comunidades em um grafo usando o algoritmo de Leiden, considerando os pesos das conexões.

    Args:
    connections (dict): Dicionário de conexões entre deputados com pesos normalizados.

    Returns:
    tuple: Grafo do NetworkX com comunidades detectadas, layout do grafo.
    """
    # Create a graph
    G = nx.Graph()

    # Add edges to the graph with normalized weights
    for (deputy_a, deputy_b), weight in connections.items():
        G.add_edge(deputy_a, deputy_b, weight=weight)

    print("Created graph with connections")

    # Convert NetworkX graph to igraph, preserving weights
    edges_with_weights = [(deputy_a, deputy_b, weight) for (deputy_a, deputy_b), weight in connections.items()]
    ig_g = ig.Graph.TupleList(edges_with_weights, edge_attrs=['weight'], directed=False)

    # Detect communities using Leiden algorithm and pass weights
    partition = la.find_partition(
        ig_g,
        la.ModularityVertexPartition,
        weights=ig_g.es['weight'],  # Passing weights to the partition constructor
        n_iterations= -1,
        seed = 42 
    )

    # Add community information to the nodes
    community_dict = {node: community for community, nodes in enumerate(partition) for node in nodes}
    
    # Convert igraph node indices to original node labels
    mapping = {i: v for i, v in enumerate(G.nodes())}
    community_dict = {mapping[node]: community for node, community in community_dict.items()}

    nx.set_node_attributes(G, community_dict, 'community')

    # Generate position using spring layout
    pos = nx.spring_layout(G, seed=42)

    return G, pos, community_dict, partition

# Evaluate Communities
def evaluate_communities(G, community_dict, partition):
    """
    Avalia a qualidade das comunidades detectadas usando diferentes métricas.

    Args:
    G (networkx.Graph): Grafo do NetworkX.
    community_dict (dict): Dicionário com as comunidades detectadas.
    partition (list): Partição das comunidades.

    Returns:
    dict: Dicionário com as métricas de avaliação.
    """
    # Calcular modularidade
    modularity = partition.modularity

    # Preparar dados para NMI e ARI
    labels_true = [community_dict[node] for node in G.nodes()]
    labels_pred = [partition.membership[list(G.nodes()).index(node)] for node in G.nodes()]

    # Calcular NMI
    nmi = normalized_mutual_info_score(labels_true, labels_pred)

    # Calcular ARI
    ari = adjusted_rand_score(labels_true, labels_pred)

    return {'modularity': modularity, 'nmi': nmi, 'ari': ari}

# Save graph to .gml file
def save_graph_to_gml(G, community_dict, vot_par, file_name='output_with_names.gml'):
    """
    Salva um grafo no formato GML, substituindo o ID dos nós pelo nome do deputado,
    e adicionando labels com o nome do deputado, sigla do partido e sigla da UF.

    Args:
    G (networkx.Graph): Grafo do NetworkX com as conexões.
    community_dict (dict): Dicionário com as comunidades detectadas.
    votacao_parlamentar (pd.DataFrame): DataFrame contendo os nomes dos deputados, sigla do partido e sigla da UF.
    file_name (str): Nome do arquivo .gml a ser salvo.
    """
    # Criar dicionários para mapear o ID do deputado para nome, sigla_partido e sigla_uf
    id_to_name = vot_par.set_index('id_deputado')['nome'].to_dict()
    id_to_partido = vot_par.set_index('id_deputado')['sigla_partido'].to_dict()
    id_to_uf = vot_par.set_index('id_deputado')['sigla_uf'].to_dict()
    
    # Criar um novo grafo com os nomes dos deputados como IDs
    G_with_names = nx.Graph()

    for node in G.nodes():
        node_name = id_to_name.get(node, f"Deputado {node}")
        node_partido = id_to_partido.get(node, "Unknown")
        node_uf = id_to_uf.get(node, "Unknown")
        
        # Adiciona os nós ao novo grafo com os nomes dos deputados como IDs
        G_with_names.add_node(node_name)
        G_with_names.nodes[node_name]['label'] = node_name  # Agora o 'label' e o 'id' serão o nome do deputado
        G_with_names.nodes[node_name]['name'] = node_name
        G_with_names.nodes[node_name]['community'] = str(community_dict.get(node, 'Unknown'))
        G_with_names.nodes[node_name]['sigla_partido'] = node_partido
        G_with_names.nodes[node_name]['sigla_uf'] = node_uf

    # Adicionar as arestas ao novo grafo, mapeando os nós antigos para os novos IDs (nomes)
    for u, v, data in G.edges(data=True):
        G_with_names.add_edge(id_to_name.get(u, f"Deputado {u}"), id_to_name.get(v, f"Deputado {v}"), **data)

    # Salva o novo grafo no formato GML
    nx.write_gml(G_with_names, file_name)
    print(f"Grafo salvo em {file_name}")

# Replace id with label
def replace_id_with_label_in_gml(input_file, output_file):
    """
    Substitui os IDs numéricos pelos labels (nomes dos deputados) em um arquivo GML, tanto nos nodes quanto nos edges.
    Também decodifica entidades HTML para caracteres legíveis.

    Args:
    input_file (str): Caminho para o arquivo GML original.
    output_file (str): Caminho para salvar o novo arquivo GML com IDs substituídos.
    """
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    id_to_label = {}
    new_lines = []

    for line in lines:
        if line.strip().startswith('id'):
            current_id = line.strip().split()[1]
        elif line.strip().startswith('label'):
            label = line.strip().split(' ', 1)[1].strip('"')
            # Decodifica a label de entidades HTML para caracteres normais
            label = html.unescape(label)
            id_to_label[current_id] = label

    for line in lines:
        if line.strip().startswith('id'):
            current_id = line.strip().split()[1]
            new_line = f'  id "{id_to_label.get(current_id, current_id)}"\n'
            new_lines.append(new_line)
        elif line.strip().startswith('source'):
            source_id = line.strip().split()[1]
            new_line = f'    source "{id_to_label.get(source_id, source_id)}"\n'
            new_lines.append(new_line)
        elif line.strip().startswith('target'):
            target_id = line.strip().split()[1]
            new_line = f'    target "{id_to_label.get(target_id, target_id)}"\n'
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)

    print(f"Novo arquivo GML salvo como {output_file}")

# Load the dataset
votacao_parlamentar = pd.read_csv('data/votacao_parlamentar.csv')
print("votacao_parlamentar loaded")

proposicao_tema = pd.read_csv('data/proposicao_tema.csv')
print("proposicao_tema loaded")

orgao_deputado = pd.read_csv('data/orgao_deputado.csv')
print("orgao_deputado loaded")

proposicao_microdados = pd.read_csv('data/proposicao_microdados.csv')
print("proposicao_microdados loaded")

votacao = pd.read_csv('data/votacao.csv')
print("votacao loaded")

votacao_objeto = pd.read_csv('data/votacao_objeto.csv')
print("votacao_objeto loaded")

# Feature Sellection
votacao_objeto['data'] = pd.to_datetime(votacao_objeto['data'])
votacao_objeto = votacao_objeto[votacao_objeto['data'].dt.year == Year]
votacao_objeto = votacao_objeto[['id_votacao', 'id_proposicao', 'data', 'sigla_tipo']]

proposicao_tema = proposicao_tema[proposicao_tema['ano'] == Year]
proposicao_tema = proposicao_tema[['id_proposicao', 'tema', 'relevancia']]

votacao_parlamentar['data'] = pd.to_datetime(votacao_parlamentar['data'])
votacao_parlamentar = votacao_parlamentar[votacao_parlamentar['data'].dt.year == Year]
votacao_parlamentar = votacao_parlamentar[['id_votacao', 'id_deputado', 'voto', 'nome', 'sigla_partido', 'sigla_uf']]

votacao['data'] = pd.to_datetime(votacao['data'])
votacao = votacao[votacao['data'].dt.year == Year]
votacao = votacao[['id_votacao', 'id_orgao', 'sigla_orgao', 'aprovacao']]

orgao_deputado = orgao_deputado.drop_duplicates(subset='id_orgao')
orgao_deputado = orgao_deputado[['id_orgao', 'nome']]
orgao_deputado = orgao_deputado.rename(columns={'nome': 'nome_orgao'})

proposicao_microdados['data'] = pd.to_datetime(proposicao_microdados['data'])
proposicao_microdados = proposicao_microdados[proposicao_microdados['data'].dt.year == Year]
proposicao_microdados = proposicao_microdados[['id_proposicao', 'tipo']]

merged_df = pd.merge(votacao_objeto, proposicao_tema, on='id_proposicao', how='left')
merged_df = pd.merge(merged_df, proposicao_microdados, on='id_proposicao', how='left')
merged_df = pd.merge(merged_df, votacao_parlamentar, on='id_votacao', how='left')
merged_df = pd.merge(merged_df, votacao, on='id_votacao', how='left')
merged_df = pd.merge(merged_df, orgao_deputado, on='id_orgao', how='left')

# Convert the "data" column to datetime
merged_df['data'] = pd.to_datetime(merged_df['data'])
print("Converted 'data' column to datetime")

# Extract the year from the "data" column
merged_df['year'] = merged_df['data'].dt.year
print("Extracted year from 'data' column")

merged_df = merged_df.dropna(subset=['voto'])

# Count the number of votes for each proposition
votes_per_proposition = merged_df['id_votacao'].value_counts()
print("Counted number of votes for each proposition")
print(votes_per_proposition.head())

# Filter propositions with more than 200 votes
propositions_with_more_than_200_votes = votes_per_proposition[votes_per_proposition > 200].index
print(f"Filtered propositions with more than 200 votes: {len(propositions_with_more_than_200_votes)} propositions")

# Filter the dataset to include only these propositions
votacao_ano = merged_df[merged_df['id_votacao'].isin(propositions_with_more_than_200_votes)]
print(f"Filtered dataset to include only propositions with more than 200 votes: {len(votacao_ano)} rows")

votacao_plenario = votacao_ano.loc[votacao_ano['nome_orgao'] == 'Plenário']

# Create Connections
connections = calculate_connections_similarity(votacao_plenario)
filtered_connections = filter_connections(connections, threshold)

# Detect Community
G, pos, community_dict, partition = detect_communities_leiden(filtered_connections)

# Save to GML
save_graph_to_gml(G, community_dict, votacao_parlamentar, 'data/graph_03.gml')

# Replace id with label
replace_id_with_label_in_gml('data/graph_03.gml', 'data/graph_03_with_labels.gml')