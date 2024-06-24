""" Module to contract a graph from csv format. It has to have been processed beforehand. """
import numpy as np
import numba as nb


@nb.njit
def contract_node(nodes: np.ndarray, id: int) -> np.ndarray:
    """ Contracts the node at row index id, numba decorator for performance. """
    # Find index of daughter node, numba implementation
    for i in range(len(nodes)):
        if nodes[i, 1] == nodes[id, 0]:  # Be careful with indexes
            daughter_id = i
            break
    # Change daughter's father_id to id's father_id
    nodes[daughter_id, 1] = nodes[id, 1]
    # Update daughter's distance to father
    nodes[daughter_id, 8] += nodes[id, 8]
    return np.concatenate((nodes[:id], nodes[id+1:]), axis=0)


def contract_from_csv(path_graph_csv: str, path_output_csv: str):
    """ Contracts the graph in the input path (csv), and saves it in output path (csv). INPUT MUST BE PROCESSED. """
    table = np.genfromtxt(path_graph_csv, delimiter=',', skip_header=0)
    """  0: "node_id",  1: "parent_id",   2,3,4: "x","y","z",  5: "radius",   6: "num_daughters",
         7: "num_daughters_of_father",  8: "distance_to_father",   9: "to_contract" """
    print("Now contracting...")
    ii = 0
    max_ii = 0
    while ii+1 != len(table):
        if table[ii, 9] == 1:
            table = contract_node(table, ii)
            ii = 0
        else:
            ii += 1
        if ii > max_ii:
            print(f"\r{ii/len(table)*100:.4f}  /  100 %", end="", flush=True)
            max_ii = ii

    np.savetxt(path_output_csv, table, delimiter=",")
