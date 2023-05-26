import networkx as nx
import matplotlib.pyplot as plt

graph_filename = '../data/graph.net'
modern_era_start = 2000
time_window = 2


def get_era(years):
    era = [0, 0, 0, 0, 0, 0, 0]
    for year in years:
        consecutive_year = year - 1950
        index = int(consecutive_year / 10)
        if index == 7:
            index = 6
        era[index] = era[index] + 1
    return era.index(max(era))


G = nx.read_pajek(graph_filename)
G = nx.Graph(G)

# gather star players
star_players = []
for (v, d) in G.nodes(data=True):
    if d['type'] == 'player' and d['star_player'] == 'True':
        star_players.append(v)

# transform all ppg weights to float
max_weight = ['', '', -1]
for (u, v, attr) in G.edges(data=True):
    if 'ppg' in attr.keys():
        attr['ppg'] = float(attr['ppg'])
        if attr['ppg'] > max_weight[2]:
            max_weight[0] = u
            max_weight[1] = v
            max_weight[2] = attr['ppg']
# get max ppg
max_ppg = max_weight[2]

edges = sorted(G.edges(data=True), key=lambda t: t[2].get('ppg', 1))
for edge in edges:
    print(edge)

# set each ppg as weight between 0 and 1
for (u, v, attr) in G.edges(data=True):
    attr['ppg'] = attr['ppg'] / max_ppg

nodes = G.nodes(data=True)

eigenvector_centrality = nx.eigenvector_centrality(G, weight='ppg', max_iter=10000)
# format = [on_team, on_team_count, not_on_team, not_on_team_count]
modern_era_count = [0, 0, 0, 0]
past_era_count = [0, 0, 0, 0]
modern_era_centrality = [0, 0, 0, 0]
past_era_centrality = [0, 0, 0, 0]
count_by_era_team = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
count_by_era_no_team = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
centrality_by_era_team = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
centrality_by_era_no_team = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
for player in star_players:
    print('calculating for', player)
    # find teams that a player played and their starting year
    teams_played = {}
    for (u, v, attr) in G.edges(player, data=True):
        if nodes[v]['type'] == 'team-season':
            split = v.split('-')
            team = split[0]
            year = int(split[1])
            if team not in teams_played.keys():
                teams_played[team] = []
            teams_played[team].append(year)
    # for each team a player played calculate centrality and count roster moves
    for team in teams_played:
        not_on_team_centrality = [0, 0]
        on_team_centrality = [0, 0]
        not_on_team_count = [0, 0]
        on_team_count = [0, 0]
        start = int(teams_played[team][0]) - time_window
        end = teams_played[team][len(teams_played[team]) - 1] + time_window
        classify_as_past_era = (end - time_window) < modern_era_start
        era_index = get_era(teams_played[team])
        for i in range(start, end + 1):
            # skip seasons that are not in the data
            if i < 1950 or i > 2022:
                continue
            key = team + '-' + str(i)
            if key not in nodes:
                continue
            # print('value for', key, centrality_on_updated[key])
            if i in teams_played[team]:
                on_team_centrality[0] = on_team_centrality[0] + eigenvector_centrality[key]
                on_team_centrality[1] = on_team_centrality[1] + 1
            else:
                not_on_team_centrality[0] = not_on_team_centrality[0] + eigenvector_centrality[key]
                not_on_team_centrality[1] = not_on_team_centrality[1] + 1
            previous_year = team + '-' + str(i - 1)
            # subtract common neighbor in team
            if previous_year not in nodes:
                # print('data for key', previous_year, 'not available')
                continue
            same = len(list(nx.common_neighbors(G, key, previous_year))) - 1
            if i in teams_played[team]:
                on_team_count[0] = on_team_count[0] + (same / (len(list(nx.neighbors(G, previous_year))) - 1))
                on_team_count[1] = on_team_count[1] + 1
            else:
                not_on_team_count[0] = not_on_team_count[0] + (same / (len(list(nx.neighbors(G, previous_year))) - 1))
                not_on_team_count[1] = not_on_team_count[1] + 1
        # average values over whole season
        on_team_centrality_result = on_team_centrality[0] / on_team_centrality[1]
        not_on_team_centrality_result = not_on_team_centrality[0] / not_on_team_centrality[1]
        on_team_counting_result = on_team_count[0] / on_team_count[1]
        not_on_team_counting_result = not_on_team_count[0] / not_on_team_count[1]
        # save result to correct era
        count_by_era_team[era_index * 2] = count_by_era_team[era_index * 2] + on_team_counting_result
        count_by_era_team[era_index * 2 + 1] = count_by_era_team[era_index * 2 + 1] + 1
        count_by_era_no_team[era_index * 2] = count_by_era_no_team[era_index * 2] + not_on_team_counting_result
        count_by_era_no_team[era_index * 2 + 1] = count_by_era_no_team[era_index * 2 + 1] + 1
        centrality_by_era_team[era_index * 2] = centrality_by_era_team[era_index * 2] + on_team_centrality_result
        centrality_by_era_team[era_index * 2 + 1] = centrality_by_era_team[era_index * 2 + 1] + 1
        centrality_by_era_no_team[era_index * 2] = centrality_by_era_no_team[era_index * 2] + not_on_team_centrality_result
        centrality_by_era_no_team[era_index * 2 + 1] = centrality_by_era_no_team[era_index * 2 + 1] + 1
        # save the result either to modern or past era,
        if classify_as_past_era:
            past_era_count[0] = past_era_count[0] + on_team_counting_result
            past_era_count[1] = past_era_count[1] + 1
            past_era_count[2] = past_era_count[2] + not_on_team_counting_result
            past_era_count[3] = past_era_count[3] + 1
            past_era_centrality[0] = past_era_centrality[0] + on_team_centrality_result
            past_era_centrality[1] = past_era_centrality[1] + 1
            past_era_centrality[2] = past_era_centrality[2] + not_on_team_centrality_result
            past_era_centrality[3] = past_era_centrality[3] + 1
        else:
            modern_era_count[0] = modern_era_count[0] + on_team_counting_result
            modern_era_count[1] = modern_era_count[1] + 1
            modern_era_count[2] = modern_era_count[2] + not_on_team_counting_result
            modern_era_count[3] = modern_era_count[3] + 1
            modern_era_centrality[0] = modern_era_centrality[0] + on_team_centrality_result
            modern_era_centrality[1] = modern_era_centrality[1] + 1
            modern_era_centrality[2] = modern_era_centrality[2] + not_on_team_centrality_result
            modern_era_centrality[3] = modern_era_centrality[3] + 1
# final result
final_result_count_past_team = past_era_count[0] / past_era_count[1]
final_result_count_past_not_team = past_era_count[2] / past_era_count[3]
final_result_centrality_past_team = past_era_centrality[0] / past_era_centrality[1]
final_result_centrality_past_not_team = past_era_centrality[2] / past_era_centrality[3]
final_result_count_modern_team = modern_era_count[0] / modern_era_count[1]
final_result_count_modern_not_team = modern_era_count[2] / modern_era_count[3]
final_result_centrality_modern_team = modern_era_centrality[0] / modern_era_centrality[1]
final_result_centrality_modern_not_team = modern_era_centrality[2] / modern_era_centrality[3]
print('past-centrality (team-not_team):', final_result_centrality_past_team, '-', final_result_centrality_past_not_team)
print('past-counting (team-not_team):', final_result_count_past_team, '-', final_result_count_past_not_team)
print('modern-centrality (team-not_team):', final_result_centrality_modern_team, '-', final_result_centrality_modern_not_team)
print('modern-counting (team-not_team):', final_result_count_modern_team, '-', final_result_count_modern_not_team)

# plot the by decades
labels = ['1950-59', '1960-69', '1970-79', '1980-89', '1990-99', '2000-09', '2010-22']
count_team = [count_by_era_team[0] / count_by_era_team[1], count_by_era_team[2] / count_by_era_team[3],
              count_by_era_team[4] / count_by_era_team[5], count_by_era_team[6] / count_by_era_team[7],
              count_by_era_team[8] / count_by_era_team[9], count_by_era_team[10] / count_by_era_team[11],
              count_by_era_team[12] / count_by_era_team[13]]
count_no_team = [count_by_era_no_team[0] / count_by_era_no_team[1], count_by_era_no_team[2] / count_by_era_no_team[3],
                 count_by_era_no_team[4] / count_by_era_no_team[5], count_by_era_no_team[6] / count_by_era_no_team[7],
                 count_by_era_no_team[8] / count_by_era_no_team[9], count_by_era_no_team[10] / count_by_era_no_team[11],
                 count_by_era_no_team[12] / count_by_era_no_team[13]]
centrality_team = [centrality_by_era_team[0] / centrality_by_era_team[1], centrality_by_era_team[2] / centrality_by_era_team[3],
                   centrality_by_era_team[4] / centrality_by_era_team[5], centrality_by_era_team[6] / centrality_by_era_team[7],
                   centrality_by_era_team[8] / centrality_by_era_team[9], centrality_by_era_team[10] / centrality_by_era_team[11],
                   centrality_by_era_team[12] / centrality_by_era_team[13]]
centrality_no_team = [centrality_by_era_no_team[0] / centrality_by_era_no_team[1], centrality_by_era_no_team[2] / centrality_by_era_no_team[3],
                      centrality_by_era_no_team[4] / centrality_by_era_no_team[5], centrality_by_era_no_team[6] / centrality_by_era_no_team[7],
                      centrality_by_era_no_team[8] / centrality_by_era_no_team[9], centrality_by_era_no_team[10] / centrality_by_era_no_team[11],
                      centrality_by_era_no_team[12] / centrality_by_era_no_team[13]]

plt.plot(labels, count_team, 'o', color='blue', label='Count in team')
plt.plot(labels, count_no_team, 'o', color='red', label='Count not in team')
plt.legend()
plt.xlabel('Era')
plt.ylabel('Count value')
plt.title('Count metric')
plt.show()

plt.plot(labels, centrality_team, 'o', color='blue', label='Centrality in team')
plt.plot(labels, centrality_no_team, 'o', color='red', label='Centrality not in team')
plt.yscale('log')
plt.legend()
plt.xlabel('Era')
plt.ylabel('Centrality value')
plt.title('Centrality metric')
plt.show()
