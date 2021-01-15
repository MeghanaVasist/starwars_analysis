import json
import os
from operator import itemgetter
import networkx as nx
import matplotlib.pyplot as plt
import random


def task_2_hyp1():
    """
    Predicts whether a character is light or dark based on a central character
    :return: None
        Prints the predictions
    """
    light = ['OBI-WAN', 'ANAKIN', 'OBI-WAN', 'LUKE', 'LUKE', 'HAN', 'FINN', 'R2-D2']
    path = "data/Interactions/"
    files = os.listdir(path)
    file_no = 0
    prediction = []
    for file in files:
        f = open(path + file)
        data = json.load(f)
        index_light = get_index(data['nodes'], light[file_no])
        character_interactions = get_character_interactions(data['links'], index_light)
        pred = get_type_of_character(character_interactions, data['nodes'])
        prediction.append(pred)
        file_no += 1
        print("Predictions -> " + str(pred))


def task_2_hyp2():
    """
    Calculates betweenness and degree centrality of each character in all episodes
    :return: None
        Prints the betweenness and degree centrality
    """
    path = "data/Interactions/"
    files = os.listdir(path)
    betweeness = []
    deg_centrality = []
    for file in files:
        f = open(path + file)
        data = json.load(f)
        names = [node['name'] for node in data['nodes']]
        edges = [(names[node['source']], names[node['target']]) for node in data['links']]
        betweeness.append(get_betweeness(names, edges))
        deg_centrality.append(get_degree_centrality(data['nodes'], data['links']))
        print("Betweenness -> " + str(betweeness[-1]))
        print("Degree Centrality -> " + str(deg_centrality[-1]))
        print("\n")


def task_3_part_1():
    """
    Calculates clustering coefficients of all nodes in all the episode graphs
    Calculates the average path length of a graph
    :return: None
        Prints the clustering coefficients and average path lengths
    """
    path = "data/Interactions/"
    files = os.listdir(path)
    clusters = []
    path_lengths = []
    for file in files:
        f = open(path + file)
        data = json.load(f)
        names = [node['name'] for node in data['nodes']]
        edges = [(names[node['source']], names[node['target']]) for node in data['links']]
        graph = nx.Graph()
        graph.add_nodes_from(names)
        graph.add_edges_from(edges)
        clusters.append(nx.clustering(graph))
        try:
            path_lengths.append(nx.algorithms.shortest_paths.average_shortest_path_length(graph, method='bellman'))
        except Exception as e:
            s = []
            for C in (graph.subgraph(c).copy() for c in nx.connected_components(graph)):
                s.append(nx.average_shortest_path_length(C))
            path_lengths.append(sum(s) / len(s))
        print("Clustering Coefficients -> " + str(clusters[-1]))
        print("Path lengths -> " + str(path_lengths[-1]))
        print("\n")


def task_3_part_2():
    """
    Randomizes the social graph of all the episodes and calculates the average clustering
    before and after randomization
    :return: None
        Prints the average clustering coefficients before and after randomization
    """
    path = "data/Interactions/"
    files = os.listdir(path)
    clustering = {}
    for file in files:
        i = 1
        f = open(path + file)
        data = json.load(f)
        names = [node['name'] for node in data['nodes']]
        edges = [(names[node['source']], names[node['target']]) for node in data['links']]
        graph = nx.Graph()
        graph.add_nodes_from(names)
        graph.add_edges_from(edges)
        clustering['original'] = nx.algorithms.cluster.average_clustering(graph)
        g = randomize_graph(graph, 0.6)
        clustering['randomized'] = nx.algorithms.cluster.average_clustering(g)
        plt.figure(figsize=(25, 10))
        nx.draw(graph, with_labels=True)
        plt.savefig("original_graph" + str(i) + ".png")
        plt.figure(figsize=(25, 10))
        nx.draw(g, with_labels=True)
        plt.savefig("random_graph" + str(i) + ".png")
        i += 1
        print("Average clustering -> " + str(clustering))


def task_4():
    """
    Calculates the weak ties in the networks
    :return: None
        Prints the top 10 weak ties for each episode
    """
    path = "data/Interactions/"
    files = os.listdir(path)
    weak_ties = []
    for file in files:
        f = open(path + file)
        data = json.load(f)
        nodes = data['nodes']
        links = data['links']
        interactions = get_interactions(links, nodes)
        scenes = get_scenes(nodes)
        total = {}
        for i in range(len(scenes)):
            total[i] = scenes[i] + interactions[i]
        weak_ties.append(get_weak_ties(nodes, total))
        print("Weak ties -> " + str(weak_ties[-1]))


def task_5():
    """
    Calculates the (interactions + scenes appeared) for all networks
    :return: None
        Prints the count for all episodes
    """
    path = "data/Interactions/"
    files = os.listdir(path)
    for file in files:
        f = open(path + file)
        data = json.load(f)
        nodes = data['nodes']
        links = data['links']
        interactions = get_interactions(links, nodes)
        scenes = get_scenes(nodes)
        total = {}
        for i in range(len(scenes)):
            total[i] = scenes[i] + interactions[i]
        count = {}
        for i in range(len(total)):
            count[nodes[i]['name']] = total[i]
        lists = sorted(count.items())
        x, y = zip(*lists)
        plt.figure(figsize=(20, 10))
        plt.plot(x, y)
        plt.xticks(x, x, rotation='vertical')
        plt.margins(0.0)
        plt.subplots_adjust(bottom=0.15)
        plt.savefig(file + ".png", orientation='landscape')
        plt.close()
        print("Interactions + scenes -> " + str(count))


def get_interactions(links, nodes):
    """
    Gets the interactions count for all nodes in the social network
    :param links: List of all links in the network
    :param nodes: List of all nodes in the network
    :return: Dict
        A dictionary of the form {character: number of interactions}
    """
    interactions = {}
    for i in range(len(nodes)):
        interactions[i] = 0
    for link in links:
        interactions[link['source']] += 1
        interactions[link['target']] += 1
    return interactions


def get_scenes(nodes):
    """
    Gets the total number of scenes for all nodes
    :param nodes: List of all nodes in the network
    :return: Dict
        A dictionary of the form {character: number of scenes}
    """
    scenes = {}
    for i in range(len(nodes)):
        scenes[i] = nodes[i]['value']
    return scenes


def get_weak_ties(nodes, total):
    """
    Gets the top 10 weak ties in the network
    :param nodes: List of all nodes in the network
    :param total: Dict of all nodes with format {character: (interactions + scenes)}
    :return: List of the top 10 weak ties
    """
    total = sorted(total.items(), key=itemgetter(1))
    least_ten = total[:10]
    weak = []
    for i in least_ten:
        weak.append((nodes[i[0]]['name'], i[1]))
    return weak


def get_betweeness(names, edges):
    """
    Gets the betweenness value for all the nodes in the graph
    :param names: List of nodes
    :param edges: List of edges
    :return: List of top 5 betweenness values with character names
    """
    graph = nx.Graph()
    graph.add_nodes_from(names)
    graph.add_edges_from(edges)
    b = nx.algorithms.centrality.betweenness_centrality(graph)
    max_5_betweeness = sorted(b.items(), key=itemgetter(1), reverse=True)[:5]
    return max_5_betweeness


def get_degree_centrality(nodes, links):
    """
    Gets the degree centrality value for all the nodes in the graph
    :param nodes: List of all nodes in the network
    :param links: List of all links in the network
    :return: List of top 5 degree centrality values with character names
    """
    interactions = get_interactions(links, nodes)
    interactions = sorted(interactions.items(), key=itemgetter(1), reverse=True)[:5]
    max_5_interactions = []
    for i in interactions:
        max_5_interactions.append((nodes[i[0]]['name'], i[1]))
    return max_5_interactions


def get_index(nodes, name):
    """
    Gets the index of the character based on name
    :param nodes: List of all character nodes
    :param name: Character name to get the index of
    :return: (int) index of the character name in nodes
    """
    index = 0
    for node in nodes:
        if node['name'] == name:
            return index
        index += 1
    return index


def get_character_interactions(links, main_ch):
    """
    Gets the interactions of all characters with the main character
    :param links: List of all links in the network
    :param main_ch: The assumes main character name
    :return: Dictionary of all characters and their interactions with the main character
    """
    character_interactions = {}
    for link in links:
        if link['source'] == main_ch:
            character_interactions[link['target']] = link['value']
        elif link['target'] == main_ch:
            if link['source'] in character_interactions.keys():
                character_interactions[link['source']] += link['value']
            else:
                character_interactions[link['source']] = link['value']
    return character_interactions


def get_type_of_character(character_interactions, nodes):
    """
    Classifies each character as light or dark based on the number of interactions
    with the main character
    :param character_interactions: Dictionary of all characters and their interactions
    with the main character
    :param nodes: List of all nodes in the network
    :return: Dictionary of characters with the prediction as light or dark
    """
    pred = {}
    threshold = sum(character_interactions.values()) // len(character_interactions.values())
    for character in character_interactions.keys():
        if character_interactions[character] >= threshold:
            pred[nodes[character]['name']] = 'light'
        else:
            pred[nodes[character]['name']] = 'dark'
    return pred


def randomize_graph(graph, p):
    """
    Randomizes a given graph with rewiring probability p
    :param graph: Initial networkx graph
    :param p: Probability of rewiring
    :return: Randomized graph
    """
    nodes = graph.nodes()
    edges = graph.edges()
    for i in range(len(nodes) // 2):
        if random.uniform(0, 1) < p:
            u, v = random.choice(list(edges))
            w = v
            while (u, w) in edges:
                w = random.choice(list(nodes))
            graph.remove_edge(u, v)
            graph.add_edge(u, w)
    return graph


print("Task 2: Hypothesis 1")
task_2_hyp1()
print("-----------------------")
print("Task 2: Hypothesis 2")
task_2_hyp2()
print("-----------------------")
print("Task 3: Clustering and path lengths")
task_3_part_1()
print("-----------------------")
print("Task 3: Randomizing graphs")
task_3_part_2()
print("-----------------------")
print("Task 4: Weak ties (last ten characters)")
task_4()
print("-----------------------")
print("Task 5: Number of interactions + number of scenes appeared in")
task_5()
print("-----------------------")
