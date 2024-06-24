"""Function definition of prune_graph."""
import networkx as nx
import numpy as np
import math
import numba as nb


def find_leaf_closest_to_point(point, graph):
    leafs = [x for x in graph.nodes() if graph.degree(x) == 1]

    pos_leafs = {}
    for node in leafs:
        pos_leafs[node] = graph._node[node]

    id_pos = np.zeros((len(pos_leafs), 4))
    ii = 0
    for node, value in pos_leafs.items():
        id_pos[ii, 0] = node
        id_pos[ii, 1] = value['x']
        id_pos[ii, 2] = value['y']
        id_pos[ii, 3] = value['z']
        ii += 1

    dij = [math.sqrt(np.sum(np.square(xyz - list(point)))) for xyz in id_pos[:, 1:4]]
    traquea_id = np.argmin(dij)

    return str(int(id_pos[traquea_id, 0]))



@nb.njit
def delete_row_workaround(arr: np.ndarray, row_id: int) -> np.ndarray:
    mask = np.zeros(arr.shape[0], dtype=np.int64) == 0
    mask[row_id] = False
    return arr[mask]


@nb.jit(nopython=True)
def find_branch(table: np.ndarray, leaf_id: float) -> (np.ndarray, np.ndarray):
    branch = np.array([leaf_id], dtype=np.float64)
    current_row = np.where(table[:, 0] == leaf_id)[0]
    # Security check:
    if table[current_row, 1] == -1:
        return branch, table

    father_row = np.where(table[:, 0] == table[current_row, 1])[0]
    while table[father_row, 6] == 1: # and table[father_row, 7] != 0:
        branch = np.append(branch, table[current_row, 1][0])
        current_row = father_row
        # Security check:
        if table[current_row, 1] == -1:
            return branch, table
        father_row = np.where(table[:, 0] == table[current_row, 1])[0]

    if table[father_row, 6] != 0:
        table[father_row, 6] = table[father_row, 6] - 1

    return branch, table

#@nb.njit
def main_loop(table, leafs_table, closest_leaf_id):
    n_removed = 0
    while len(leafs_table) != len(closest_leaf_id):
        # Remove branches that do not end in a node that is in closest_node
        for leaf_id in leafs_table[:, 0]:
            if leaf_id not in closest_leaf_id:
                #if table[np.where(table[:, 0] == leaf_id)[0], 1] != -1:
               # Find branch:
                branch, table = find_branch(table, leaf_id)
                n_removed += len(branch)
                for node in branch:
                    #table = np.delete(table, np.where(table[:, 0] == node)[0], axis=0)
                    table = delete_row_workaround(table, np.where(table[:, 0] == node)[0])

                #else:
                    #print("hey!")
            leafs_mask = np.logical_or(table[:, 6] == 0, table[:, 7] == 0)
            leafs_table = table[leafs_mask, :]
        print(f"\r{np.sum(leafs_mask == 1)} , {len(closest_leaf_id)}")
    print(f"\nDone! leafs: {np.sum(leafs_mask == 1)}")

    return table

def main_code(graph, cluster_pos):
    nodes = list(graph.nodes())
    leafs = [x for x in graph.nodes() if graph.degree(x) == 1]
    x = nx.get_node_attributes(graph, 'x')
    y = nx.get_node_attributes(graph, 'y')
    z = nx.get_node_attributes(graph, 'z')
    leafs_pos_graphml = [[x[ii], y[ii], z[ii]] for ii in leafs]

    if cluster_pos is None:
        cluster_pos = np.array(leafs_pos_graphml)

    # Find leaf closest to each cluster
    print("Finding leaf closest to each cluster...")
    closest_leaf_id_graphml = []
    for cluster in cluster_pos:
        dij_graphml = [math.sqrt(sum(np.square(cluster - leafs_pos_ii))) for leafs_pos_ii in leafs_pos_graphml]
        id_min_graphml = np.argmin(dij_graphml)
        closest_leaf_id_graphml.append(id_min_graphml)

    closest_leaf_id = closest_leaf_id_graphml
    leafs_pos = leafs_pos_graphml

    # Find if a leaf is assigned to multiple clusters:
    repeated_leafs = set([x for x in closest_leaf_id if closest_leaf_id.count(x) > 1])
    removing_clusters = []
    for repeated_leaf in repeated_leafs:
        critical_clusters = np.where(closest_leaf_id == repeated_leaf)[0]
        dij = []
        for critical_cluster in critical_clusters:
            dij.append(math.sqrt(sum(np.square(cluster_pos[critical_cluster] - leafs_pos[repeated_leaf]))))
        closest_critical_cluster_id = np.argmin(dij)
        removing_clusters_ii = [critical_clusters[ii] for ii in range(len(critical_clusters)) if
                                ii != closest_critical_cluster_id]
        removing_clusters.append(removing_clusters_ii)
    removing_clusters = np.array(removing_clusters)
    removing_clusters.flatten()

    mask_clusters = np.array(list(np.zeros(len(cluster_pos))))
    for ii in range(len(removing_clusters)):
        mask_clusters[removing_clusters[ii]] = 1
    cluster_pos = cluster_pos[mask_clusters == 0, :]
    closest_leaf_id = np.array(closest_leaf_id)[mask_clusters == 0]

    if sum(mask_clusters) != 0:
        print(f"ATTENTION!!! I HAVE REMOVED {sum(mask_clusters)} PROBLEMATIC CLUSTERS...")

    closest_leaf_nodes = [leafs[ii] for ii in closest_leaf_id]
    remove_nodes = []
    ii = 0
    for leaf_id in range(len(leafs)):
        ii += 1
        print(f"\r{ii / len(leafs) * 100:.4} / 100%", end='', flush=True)
        leaf_node = leafs[leaf_id]
        branch = []
        if leaf_node not in closest_leaf_nodes:
            remove_nodes.append(leaf_node)
            branch.append(leaf_node)
            neighbors = list(graph.neighbors(leaf_node))
            while len(neighbors) <= 2:
                for neigh in neighbors:
                    if neigh not in remove_nodes:
                        if graph.degree(neigh) == 2:
                            remove_nodes.append(neigh)
                            branch.append(leaf_node)
                        neighbors = list(graph.neighbors(neigh))

    jj = 0
    for ii in nodes:
        if ii in remove_nodes:
            graph.remove_node(ii)

    leafs = [x for x in graph.nodes() if graph.degree(x) == 1]
    return graph, len(leafs) == len(closest_leaf_id)


def prune_graph(path_input_graph_csv: str, path_input_graphml: str,
                path_xyz_terminals_to_keep_csv: str, POS_TRACHEA, path_output_graph_csv: str) -> None:
    """ This function prunes the input graph (graphml), removing branches that do not fall close to the
    terminals to keep (csv). The resulting graph (graphml) is saved in a file."""
    # Read cluster position
    if path_xyz_terminals_to_keep_csv is not None:
        cluster_pos = np.genfromtxt(path_xyz_terminals_to_keep_csv, delimiter=',', skip_header=0)
    else:
        cluster_pos = None

    # Read input
    # table = np.genfromtxt(path_input_graph_csv, delimiter=',', skip_header=0)
    """ Format csv after processing:  0: node_id, 1: parent_id, 2,3,4: x,y,z, 5: radius, 
        6: n_daughters, 7: n_daughters_of_father, 8: distance_father, 9: to_contract"""
    graph = nx.read_graphml(path_input_graphml)
    leafs = [x for x in graph.nodes() if graph.degree(x) == 1]

    is_done = False
    while is_done == False:
        # Might have to iterate a couple times until done
        print(f"\nCurrent leafs: {len(leafs)}, is graph connected: {nx.is_connected(graph)}")
        graph, is_done = main_code(graph, cluster_pos)
        leafs = [x for x in graph.nodes() if graph.degree(x) == 1]


    initial_node = find_leaf_closest_to_point(POS_TRACHEA, graph)
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

    x = nx.get_node_attributes(graph, 'x')
    y = nx.get_node_attributes(graph, 'y')
    z = nx.get_node_attributes(graph, 'z')
    r = nx.get_node_attributes(graph, 'r')
    distances = nx.get_edge_attributes(graph, 'weight')
    table_final = np.zeros((len(bfs_tree.nodes()), 10))
    ii = 0
    for node in bfs_tree.nodes():
        table_final[ii, 0] = node_id[ii]
        table_final[ii, 1] = predecessor[node_id[ii]]
        table_final[ii, 2] = x[node_id[ii]]
        table_final[ii, 3] = y[node_id[ii]]
        table_final[ii, 4] = z[node_id[ii]]
        table_final[ii, 5] = r[node_id[ii]]
        try:
            table_final[ii, 8] = distances[node_id[ii], predecessor[node_id[ii]]]
        except:
            pass
        try:
            table_final[ii, 8] = distances[predecessor[node_id[ii]], node_id[ii]]
        except:
            pass
        ii += 1

    np.savetxt(path_output_graph_csv, table_final, delimiter=",")


@nb.njit
def update_num_daughters(table: np.ndarray) -> np.ndarray:
    daughters = np.zeros(len(table))
    for ii, parent_id in enumerate(table[:, 1]):
        if parent_id != -1:
            index_parent = np.where(parent_id == table[:, 0])[0]
            daughters[index_parent] += 1
    table[:, 6] = daughters
    return table
