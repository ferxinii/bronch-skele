"""Extracts the main information from graphml: generation, lobe, distance_to_trachea, ..."""
import networkx as nx
import numpy as np
import math
from functools import cache


def find_node_closest_to_point(point, graph):
    # FIND NODE CLOSEST TO TRAQUEA
    pos_nodes = {}
    for node in graph.nodes():
        pos_nodes[node] = graph._node[node]

    id_pos = np.zeros((len(pos_nodes), 4))
    ii = 0
    for node, value in pos_nodes.items():
        id_pos[ii, 0] = node
        id_pos[ii, 1] = value['x']
        id_pos[ii, 2] = value['y']
        id_pos[ii, 3] = value['z']
        ii += 1

    dij = [math.sqrt(np.sum(np.square(xyz - list(point)))) for xyz in id_pos[:, 1:4]]
    traquea_id = np.argmin(dij)

    return str(int(id_pos[traquea_id, 0]))


def initial_node_of_branch(node_id, graph):
    """Inputs any node of a DIRECTED GRAPH. Return the node_id of the node starting the branch."""
    list_predecessors = nx.predecessor(graph, node_id)
    degree_predecessor = 0
    while degree_predecessor != 3:
        prev = list(graph.pred[node_id])
        if len(prev) == 0:
            return node_id
        elif len(prev) == 1:
            predecessor = prev
        node_id = predecessor[0]
        degree_predecessor = graph.degree(predecessor[0])

    return predecessor[0]


@cache
def generation(node, graph):
    branch_node = initial_node_of_branch(node, graph)
    if branch_node == node:
        return 0
    else:
        return generation(branch_node, graph) + 1


def main_code(path_input_graphml: str, POS_TRACHEA: tuple[float, float, float],
                              dictionary_propagate_lobes, path_output_csv: str):
    # FIND NODE CLOSEST TO TRACHEA
    graph = nx.read_graphml(path_input_graphml)
    initial_node = find_node_closest_to_point(POS_TRACHEA, graph)

    # Remove any unconnected components...
    subgraph = nx.empty_graph(1)
    for connected_component in nx.connected_components(graph):
        subgraph_aux = graph.subgraph(connected_component)
        if len(subgraph_aux.nodes) > len(subgraph.nodes):
            subgraph = subgraph_aux
    graph = subgraph

    # UPDATE PARENT_ID STARTING AT TRACHEA
    bfs_tree = nx.dfs_tree(graph, initial_node)
    node_id = []
    predecessor = {}
    for node in bfs_tree.nodes():
        node_id.append(node)
        pred = []
        for parent in bfs_tree.predecessors(node):
            pred.append(parent)
        if len(pred) == 1:
            predecessor[node] = pred[0]
        else:
            predecessor[node] = "-1"

    # COMPUTE GENERATION
    print("Now computing generation...")
    oriented_graph = nx.dfs_tree(graph, source=initial_node)
    gen = {}
    ii = 0
    for node in bfs_tree:
        ii += 1
        print(f"\r{ii / len(bfs_tree.nodes()) * 100:.4} / 100%", end='', flush=True)
        gen[node] = generation(node, oriented_graph)

    # PROPAGATE LUNG LOBES
    if dictionary_propagate_lobes != None:
        print("Now propagating lung lobes...")
        names_lobes = ["RS", "RM", "RI", "LS", "LI"]
        number_lobes = {"RS": 2, "RM": 3, "RI": 4, "LS": 6, "LI": 5}
        lobe = {}
        path_to_trachea = {}
        for ii in range(len(names_lobes)):
            shortest_path_ii = []
            for jj in range(len(dictionary_propagate_lobes[names_lobes[ii]])):
                starting_terminal = find_node_closest_to_point(dictionary_propagate_lobes[names_lobes[ii]][jj], graph)
                shortest_path_ii.append(nx.shortest_path(graph, source=starting_terminal, target=initial_node))
            path_to_trachea[ii] = shortest_path_ii

        for ii in range(len(names_lobes)):
            intersection_ij = {}
            for path_ii in path_to_trachea[ii]:
                for jj in range(len(names_lobes)):
                    # intersection_ij[jj] = None
                    if ii != jj:
                        intersection_path_jj_arr = []
                        for path_jj in path_to_trachea[jj]:
                            intersection_path_jj = None
                            for node1 in path_ii:
                                for node2 in path_jj:
                                    if node1 == node2:
                                        if intersection_path_jj == None:
                                            intersection_path_jj = node1
                            intersection_path_jj_arr.append(intersection_path_jj)
                        intersection_ij[jj] = intersection_path_jj_arr

                starting_node_ii = None
                for kk in range(len(path_ii)):
                    for jj in range(len(names_lobes)):
                        if ii != jj:
                            for counter_paths_jj in range(len(intersection_ij[jj])):
                                if starting_node_ii == None:
                                    if path_ii[kk + 1] in intersection_ij[jj][counter_paths_jj]:
                                        starting_node_ii = path_ii[kk]
                                        break
                                    counter_paths_jj += 1

                reachable = nx.descendants(oriented_graph, starting_node_ii)
                for node in reachable:
                    lobe[node] = number_lobes[names_lobes[ii]]
    else:
        lobe = {}
        for node in bfs_tree:
            lobe[node] == -1

    # COMPUTE DISTANCE TO TRACHEA
    x = nx.get_node_attributes(graph, 'x')
    y = nx.get_node_attributes(graph, 'y')
    z = nx.get_node_attributes(graph, 'z')
    r = nx.get_node_attributes(graph, 'r')

    print("Now computing distance to trachea")
    d2t = {}
    d2t_2 = {}
    distances = nx.get_edge_attributes(graph, 'weight')
    ii = 0
    for node in oriented_graph.nodes():
        print(f"\r{ii / len(oriented_graph.nodes()) * 100:.4} / 100 %", end='', flush=True)
        ii += 1
        shortest_path = nx.shortest_path(graph, source=node, target=initial_node)
        if len(shortest_path) == 0:
            dij = 0
            dij_2 = 0
        else:
            dij = 0
            dij_2 = 0
            for kk in range(len(shortest_path) - 1):
                dij_2 += math.sqrt((x[shortest_path[kk]] - x[shortest_path[kk + 1]]) ** 2 +
                                   (y[shortest_path[kk]] - y[shortest_path[kk + 1]]) ** 2 +
                                   (z[shortest_path[kk]] - z[shortest_path[kk + 1]]) ** 2)
                try:
                    dij += distances[shortest_path[kk], shortest_path[kk + 1]]
                except:
                    dij += distances[shortest_path[kk + 1], shortest_path[kk]]

        d2t[node] = dij
        d2t_2[node] = dij_2

    # DETECT BIFURCATION AND LEAFS
    print("Now detecting bifurcations and leafs...")
    is_bifurcation = {}
    is_leaf = {}
    for node in graph:
        degree = graph.degree[node]
        if degree == 3:
            is_bifurcation[node] = 1
            is_leaf[node] = 0
        elif degree == 1:
            is_bifurcation[node] = 0
            is_leaf[node] = 1
        else:
            is_bifurcation[node] = 0
            is_leaf[node] = 0

    # GENERATE TABLE WITH ALL THE DATA

    # 0:node_id,  1:parent_id, 2:is_bifurcation, 3:is_leaf, 4:x, 5:y, 6:z, 7:lobe, 8:gen, 9:d2t, 10:radius
    data = np.zeros((len(graph.nodes()), 12)) - 1
    ii = 0
    for node in graph.nodes():
        data[ii, 0] = int(node)
        data[ii, 1] = int(predecessor[node])
        data[ii, 2] = is_bifurcation[node]
        data[ii, 3] = is_leaf[node]
        data[ii, 4] = x[node]
        data[ii, 5] = y[node]
        data[ii, 6] = z[node]
        try:  # Some nodes don't have a lobe associated!
            data[ii, 7] = lobe[node]
        except:
            pass
        data[ii, 8] = gen[node]
        data[ii, 9] = d2t[node]
        data[ii, 10] = d2t_2[node]
        data[ii, 11] = r[node]
        ii += 1

    np.savetxt(path_output_csv, data, delimiter=",")


def extract_data(INPUT_FOLDER: str, POS_TRACHEA: tuple[float, float, float],
                              dictionary_propagate_lobes: dict):

    path_input_graphml_1 = INPUT_FOLDER + "/aux/graph_2.graphml"
    path_input_graphml_2 = INPUT_FOLDER + "/aux/graph_3.graphml"
    path_out_1 = INPUT_FOLDER + "/simplified.csv"
    path_out_2 = INPUT_FOLDER + "/smooth.csv"
    for path_input_graphml, path_output_csv in zip([path_input_graphml_1, path_input_graphml_2], [path_out_1, path_out_2]):
        main_code(path_input_graphml, POS_TRACHEA, dictionary_propagate_lobes, path_output_csv)

