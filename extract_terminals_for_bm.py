import numpy as np
import trimesh as tm
import os
import math
import networkx as nx


def get_leafs(graph) -> (list[str], dict):
    leafs = [x for x in graph.nodes() if graph.degree(x) == 1]
    x_dict = nx.get_node_attributes(graph, 'x')
    y_dict = nx.get_node_attributes(graph, 'y')
    z_dict = nx.get_node_attributes(graph, 'z')
    r_dict = nx.get_node_attributes(graph, 'r')
    pos_leafs = {leaf: (x_dict[leaf], y_dict[leaf], z_dict[leaf]) for leaf in leafs}
    diameter = {leaf: 2*r_dict[leaf] for leaf in leafs}
    return leafs, pos_leafs, diameter


def remove_trachea_leaf(leafs, pos_leafs, diameter, POS_TRACHEA) -> (list[str], dict):
    dist_trachea = {x: np.linalg.norm(np.array(pos_leafs[x]) - np.array(POS_TRACHEA)) for x in leafs}
    min_id = np.argmin(list(dist_trachea.values()))
    min_key = min(dist_trachea, key=dist_trachea.get)
    del leafs[min_id]
    del pos_leafs[min_key]
    del diameter[min_key]
    return leafs, pos_leafs, diameter


def read_lobules(INPUT_DIR: str) -> dict:
    cells = {}
    counter = 1
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".stl"):
            cells[counter] = tm.load_mesh(INPUT_DIR + "/" + file)
            counter += 1
    return cells


def map_leafs_to_lobules(leafs, pos_leafs, lobules) -> dict:
    mapping = {}
    ii = 0
    for leaf in leafs:
        print(f"\rMapping leafs to lobules... {ii / len(leafs) * 100:.1f} %", end='')
        aux = []
        for lobule_id, lobule in lobules.items():
            if lobule.contains([pos_leafs[leaf]]):
                aux.append(lobule_id)
        mapping[leaf] = aux
        ii += 1
    return mapping

"""
def map_lobules_to_terminals(lobules, leafs, pos_leafs) -> dict:
    mapping = {}
    ii = 0
    for lobule_id, lobule in lobules.items():
        print(ii/len(lobules))
        is_inside = lobule.contains(terminals)
        mapping[ii] = [i for i, x in enumerate(is_inside) if x]
        ii += 1
    return mapping
"""


def find_distance_to(leafs, pos_leafs, lobules, map_terminals_lobules) -> dict:
    min_distance = {}
    closest_lobe_dict = {}
    # for ii, term in enumerate(terminals):
    ii = 0
    for leaf in leafs:
        ii += 1
        mapping = map_terminals_lobules[leaf]
        if len(mapping) >= 1:
            lobule = lobules[mapping[0]]
            lobule_vertices = lobule.vertices
            dij = [math.sqrt(np.sum(np.square(pos_leafs[leaf] - xyz_vert))) for xyz_vert in lobule_vertices]
            min_distance[ii] = min(dij)
        else:  # Find closest point in all segments
            minimum = 100
            closest_lobe = -1
            for jj, lobule in lobules.items():
                for vertex in lobule.vertices:
                    dij = math.sqrt(np.sum(np.square(pos_leafs[leaf] - vertex)))
                    if dij < minimum:
                        closest_lobe = jj
                        minimum = dij
            closest_lobe_dict[leaf] = closest_lobe
            min_distance[ii] = minimum
        print(f"\rFinding distance to wall... {ii / len(leafs) * 100:.1f} %", end='', flush=True)
    return min_distance, closest_lobe_dict


#PATH_TERMINALS = "/Users/ferxinii/Desktop/TFG/human_lung/terminals/pos_terminals_w_trachea_full.csv"


def extract_terminals_for_bm(input_graphml, POS_TRACHEA, path_lobules, path_lobes, path_lung_right, path_lung_left, output_txt):
    # Read terminal data
    # terminals = np.genfromtxt(PATH_TERMINALS, delimiter=',', skip_header=2)  # Skip name and trachea
    graph = nx.read_graphml(input_graphml)
    leafs, pos_leafs, diameter = get_leafs(graph)
    leafs, pos_leafs, diameter = remove_trachea_leaf(leafs, pos_leafs, diameter, POS_TRACHEA)

    # Read enclosure data
    lobules = read_lobules(path_lobules)
    lobes = read_lobules(path_lobes)
    left_lung = tm.load_mesh(path_lung_left)
    right_lung = tm.load_mesh(path_lung_right)

    # Distance to lobules
    print("Finding distance to lobules:")
    leafs_map_lobules = map_leafs_to_lobules(leafs, pos_leafs, lobules)
    distance_to_lobule, closest_lobule = find_distance_to(leafs, pos_leafs, lobules, leafs_map_lobules)
    # lobules_map = map_lobules_to_terminals(lobules, terminals)

    # Distance to lobes
    print("Finding distance to lobes:")
    leafs_map_lobes = map_leafs_to_lobules(leafs, pos_leafs, lobes)
    distance_to_lobes, closest_lobe = find_distance_to(leafs, pos_leafs, lobes, leafs_map_lobes)

    # Convert into array
    leafs_map_lobules_array = []
    for leaf in leafs:
        if len(leafs_map_lobules[leaf]) != 0:
            leafs_map_lobules_array.append(leafs_map_lobules[leaf][0])
        else:
            leafs_map_lobules_array.append(closest_lobule[leaf])
    leafs_map_lobules_array = np.array(leafs_map_lobules_array)
    distance_to_lobule_array = np.array(list(distance_to_lobule.values()))

    leafs_map_lobes_array = []
    for leaf in leafs:
        if len(leafs_map_lobes[leaf]) != 0:
            leafs_map_lobes_array.append(leafs_map_lobes[leaf][0])
        else:
            leafs_map_lobes_array.append(closest_lobe[leaf])
    leafs_map_lobes_array = np.array(leafs_map_lobes_array)
    distance_to_lobes_array = np.array(list(distance_to_lobes.values()))

    leafs_pos_array = []
    for leaf in leafs:
        leafs_pos_array.append(pos_leafs[leaf])
    leafs_pos_array = np.array(leafs_pos_array)

    """
    diameter_array = []
    for leaf in leafs:
        diameter_array.append(diameter[leaf])
    diameter_array = np.array(diameter_array)
    """

    # SAVE
    data = np.hstack((leafs_pos_array,
                      leafs_map_lobules_array.reshape(len(leafs),1),
                      distance_to_lobule_array.reshape(len(leafs),1),
                      leafs_map_lobes_array.reshape(len(leafs),1),
                      distance_to_lobes_array.reshape(len(leafs),1),))
                      # diameter_array.reshape(len(leafs),1)))
    np.savetxt(output_txt, data, delimiter=',', fmt="%f")

"""
# Determine which terminals are not inside a lobule
for ii, mapping in terminals_map_lobules.items():
    if len(mapping) == 0:
        print(f"terminal {ii} is not inside any lobe")
    elif len(mapping) > 1:
        print(f"terminal {ii} is inside multiple lobes: {mapping}")

# Determine which lobules are empty
for ii, mapping in lobules_map.items():
    if len(mapping) == 0:
        print(f"lobe {ii} is empty!!")

print("Done!")
"""