import networkx as nx

graph_filename = '../data/graph.net'

G = nx.read_pajek(graph_filename)
G = nx.DiGraph(G)

# gather star players
star_players = []
for (v, d) in G.nodes(data=True):
    if d['type'] == 'player' and d['star_player'] == 'True':
        star_players.append(v)


# transform all ppg weights to float
for (u, v, attr) in G.edges(data=True):
    attr['ppg'] = float(attr['ppg'])
# get max ppg
max_weight = max(G.edges(data='ppg'), key=lambda x: x[2])
max_ppg = max_weight[2]

for (u, v, attr) in G.edges(data=True):
    attr['weight'] = attr['ppg'] / max_ppg

# print('calculating centrality')
centrality = nx.eigenvector_centrality(G)
# centrality = nx.pagerank(G, weight='ppg')
# centrality = nx.eigenvector_centrality(G, weight='weight', max_iter=1000000)
print('sorting')
sorted_c = dict(sorted(centrality.items(), key=lambda x: x[1], reverse=True))
# printing teams
# print(centrality)
nodes = G.nodes(data=True)
max = 40
for key in sorted_c.keys():
    if max == 0:
        break
    if nodes[key]['type'] == 'team-season':
        print(key, sorted_c[key])
        max = max - 1

# ------------------------- STAR PLAYERS ---------------------------------------------
# star_players = ['LeBron James', 'Kevin Durant', 'Dwyane Wade', 'Michael Jordan', 'Larry Bird', 'Magic Johnson']
# time_window = 2
# for player in star_players:
#     print('displaying for', player, '-----------------------------')
#     # find teams that a player played and their starting year
#     teams_played = {}
#     for (u, v, attr) in G.edges(player, data=True):
#         if nodes[v]['type'] == 'team-season':
#             split = v.split('-')
#             team = split[0]
#             year = int(split[1])
#             if team not in teams_played.keys():
#                 teams_played[team] = []
#             teams_played[team].append(year)
#     print(teams_played)
#     for team in teams_played:
#         print('showing for team', team)
#         start = int(teams_played[team][0]) - time_window
#         end = teams_played[team][len(teams_played[team]) - 1] + time_window
#         for i in range(start, end + 1):
#             key = team + '-' + str(i)
#             if key in G.nodes():
#                 print('value for', key, centrality[key])
#             else:
#                 print(key, 'not in network')

