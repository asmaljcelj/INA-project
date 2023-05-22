import networkx as nx
import matplotlib.pyplot as plt

# visualize subgraph
graph_filename = '../data/graph.net'

G = nx.read_pajek(graph_filename)

player = 'LeBron James'
G.nodes()[player]['subset'] = 1

nodes_that_stay = [player]
for (u, v) in G.edges(player):
    if u != player:
        nodes_that_stay.append(u)
        G.nodes()[u]['subset'] = 2
        for (u1, v1) in G.edges(u):
            if G.nodes()[v1]['type'] == 'team':
                if u1 != u:
                    if u1 not in nodes_that_stay:
                        nodes_that_stay.append(u1)
                        G.nodes()[u1]['subset'] = 3
                else:
                    if v1 not in nodes_that_stay:
                        nodes_that_stay.append(v1)
                        G.nodes()[v1]['subset'] = 3
    else:
        G.nodes()[v]['subset'] = 2
        nodes_that_stay.append(v)
        for (u1, v1) in G.edges(v):
            if G.nodes()[v1]['type'] == 'team':
                if u1 != u:
                    if u1 not in nodes_that_stay:
                        nodes_that_stay.append(u1)
                        G.nodes()[u1]['subset'] = 3
                    else:
                        if v1 not in nodes_that_stay:
                            nodes_that_stay.append(v1)
                            G.nodes()[v1]['subset'] = 3
print(nodes_that_stay)
deleted_nodes = []
for node in G.nodes():
    if node not in nodes_that_stay:
        deleted_nodes.append(node)

G.remove_nodes_from(deleted_nodes)

nx.draw(G, pos=nx.multipartite_layout(G), with_labels=True)
plt.draw()
plt.show()
