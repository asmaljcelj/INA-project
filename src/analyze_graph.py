import networkx as nx

graph_filename = '../data/graph.net'

G = nx.read_pajek(graph_filename)

centrality = nx.betweenness_centrality(G)
print(centrality)

