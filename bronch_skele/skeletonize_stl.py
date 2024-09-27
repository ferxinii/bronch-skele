import networkx as nx
import skeletor as sk
import trimesh as tm
import numpy as np
import networkx
import pyvista as pv


def skeletonize_stl(path_stl: str, POS_TRACHEA: tuple[float, float, float], output_folder: str):
    mesh = tm.load_mesh(path_stl)

    print("SKEL: Now fixing...")
    fixed = sk.pre.fix_mesh(mesh, remove_disconnected=5, inplace=False)

    print("SKEL: Finding node closest to trachea...")
    distances = np.linalg.norm(mesh.vertices - POS_TRACHEA, axis=1)
    starting_node_id = np.argmin(distances)

    print("SKEL: Now skeletonizing...")
    # ORIGIN SHOULD BE SET AT TRACHEA!!
    skel = sk.skeletonize.by_wavefront(fixed, origins=int(starting_node_id), waves=1, step_size=1)

    print("SKEL: Now post-processing...")
    sk.post.clean_up(skel, inplace=True)

    print("SKEL: Now saving...")
    np.save(output_folder+"/skel_edges.npy", skel.edges)
    np.save(output_folder+"/skel_vertices.npy", skel.vertices)
    np.save(output_folder+"/skel_map.npy", skel.skel_map)
    np.save(output_folder+"/mesh_map.npy", skel.mesh_map)
    data_frame = skel.swc
    data_frame.to_csv(output_folder+"/data_frame.csv", index=False, header=None)
    leafs = skel.leafs
    leafs.to_csv(output_folder+"/leafs.csv")

    # Producing and saving graph, including node position in 3D space
    not_root = skel.swc.parent_id >= 0
    nodes = skel.swc.loc[not_root]
    parents = skel.swc.set_index('node_id').loc[skel.swc.loc[not_root, 'parent_id'].values]

    dists = nodes[['x', 'y', 'z']].values - parents[['x', 'y', 'z']].values
    dists = np.sqrt((dists ** 2).sum(axis=1))

    graph = nx.Graph()
    graph.add_weighted_edges_from(zip(nodes.node_id.values, nodes.parent_id.values, dists))

    node_positions = np.array([data_frame.x, data_frame.y, data_frame.z])

    dict_x = dict(zip(range(1, len(data_frame.x) + 1), node_positions[0, :]))
    dict_y = dict(zip(range(1, len(data_frame.x) + 1), node_positions[1, :]))
    dict_z = dict(zip(range(1, len(data_frame.x) + 1), node_positions[2, :]))

    networkx.set_node_attributes(graph, dict_x, "x")
    networkx.set_node_attributes(graph, dict_y, "y")
    networkx.set_node_attributes(graph, dict_z, "z")

    networkx.write_graphml(graph, output_folder+"/graph_0.graphml")

    # Save skele vtk
    vertices = skel.vertices
    edges = skel.edges

    points = pv.PolyData(vertices)
    lines = []
    for edge in edges:
        lines.append([2, edge[0], edge[1]])

    poly_data = pv.PolyData()
    poly_data.points = points.points
    poly_data.lines = lines

    output_file = "/graph_0.vtk"
    poly_data.save(output_folder + output_file)
