import networkx as nx
import numpy as np
import math


def get_leafs_and_pos(graph) -> (list[str], dict):
    leafs = [x for x in graph.nodes() if graph.degree(x) == 1]
    x_dict = nx.get_node_attributes(graph, 'x')
    y_dict = nx.get_node_attributes(graph, 'y')
    z_dict = nx.get_node_attributes(graph, 'z')
    pos_leafs = {leaf: (x_dict[leaf], y_dict[leaf], z_dict[leaf]) for leaf in leafs}
    return leafs, pos_leafs


def remove_trachea_leaf(leafs, pos_leafs, POS_TRACHEA) -> (list[str], dict):
    dist_trachea = {x: np.linalg.norm(np.array(pos_leafs[x]) - np.array(POS_TRACHEA)) for x in leafs}
    min_id = np.argmin(list(dist_trachea.values()))
    min_key = min(dist_trachea, key=dist_trachea.get)
    del leafs[min_id]
    del pos_leafs[min_key]
    return leafs, pos_leafs


def compute_dij_distance(graph, leafs) -> np.ndarray:
    x = nx.get_node_attributes(graph, 'x')
    y = nx.get_node_attributes(graph, 'y')
    z = nx.get_node_attributes(graph, 'z')
    d = np.zeros([len(leafs), len(leafs)])
    distances = nx.get_edge_attributes(graph, 'weight')
    for ii, leaf_ii in enumerate(leafs):
        for jj, leaf_jj in enumerate(leafs):
            shortest_path = nx.shortest_path(graph, source=leaf_ii, target=leaf_jj)
            if len(shortest_path) == 0:
                dij = 0
            else:
                dij = 0
                for kk in range(len(shortest_path)-1):
                    dij += math.sqrt((x[shortest_path[kk]] - x[shortest_path[kk + 1]]) ** 2 +
                                     (y[shortest_path[kk]] - y[shortest_path[kk + 1]]) ** 2 +
                                     (z[shortest_path[kk]] - z[shortest_path[kk + 1]]) ** 2)
                    # dij = math.sqrt(np.square(pos_leafs[shortest_path[kk]] - pos_leafs[shortest_path[kk+1]]))
                    """
                    try:
                        dij += distances[shortest_path[kk], shortest_path[kk+1]]
                    except:
                        dij += distances[shortest_path[kk+1], shortest_path[kk]]
                    """
            d[ii, jj] = dij
        print(f"\rComputing distance matrix... {ii/len(leafs)*100:.1f} %", end='', flush=True)
    return d


def write_matrix_file(input: np.ndarray, path) -> None:
    matrix = np.asmatrix(input)
    with open(path, 'wb') as f:
        for line in matrix:
            np.savetxt(f, line, delimiter=',', fmt='%f')


def intrabronchial_distance(input_graphml: str, POS_TRACHEA, output_txt: str):
    graph = nx.read_graphml(input_graphml)
    leafs_full, pos_leafs_full = get_leafs_and_pos(graph)
    leafs_full, pos_leafs_full = remove_trachea_leaf(leafs_full, pos_leafs_full, POS_TRACHEA)
    d_full = compute_dij_distance(graph, leafs_full)
    write_matrix_file(d_full, output_txt)
