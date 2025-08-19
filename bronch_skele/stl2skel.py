import os
from .contract_from_csv import contract_from_csv
from .csv_to_vtk_graphml import csv_to_vtk_graphml
from .process_graph_csv import process_graph_csv
from .prune_graph import prune_graph
from .skeletonize_stl import skeletonize_stl

def stl2skel(PATH_STL, POS_TRAQUEA: tuple[float, float, float], PATH_TERMINALS_TO_KEEP, OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER,  exist_ok=True)
    os.makedirs(OUTPUT_FOLDER + "/aux",  exist_ok=True)

    PATH_GRAPH_0 = OUTPUT_FOLDER + "/aux/data_frame.csv"

    PATH_GRAPH_1 = OUTPUT_FOLDER + "/aux/graph_0_processed.csv"
    PATH_GRAPH_1_VTK = OUTPUT_FOLDER + "/aux/graph_0.vtk"
    PATH_GRAPH_1_GRAPHML = OUTPUT_FOLDER + "/aux/graph_0.graphml"

    PATH_GRAPH_2 = OUTPUT_FOLDER + "/aux/graph_1.csv"
    PATH_GRAPH_2_VTK = OUTPUT_FOLDER + "/aux/graph_1.vtk"
    PATH_GRAPH_2_GRAPHML = OUTPUT_FOLDER + "/aux/graph_1.graphml"

    PATH_GRAPH_3 = OUTPUT_FOLDER + "/aux/graph_1_pruned.csv"
    PATH_GRAPH_3_VTK = OUTPUT_FOLDER + "/aux/graph_1_pruned.vtk"
    PATH_GRAPH_3_GRAPHML = OUTPUT_FOLDER + "/aux/graph_1_pruned.graphml"

    PATH_GRAPH_4 = OUTPUT_FOLDER + "/aux/graph_1_reprocessed.csv"

    PATH_GRAPH_5 = OUTPUT_FOLDER + "/aux/graph_2.csv"
    PATH_GRAPH_5_VTK = OUTPUT_FOLDER + "/aux/graph_2.vtk"
    PATH_GRAPH_5_GRAPHML = OUTPUT_FOLDER + "/aux/graph_2.graphml"

    PATH_GRAPH_SMOOTH_AUX = OUTPUT_FOLDER + "/aux/graph_3.csv"
    PATH_GRAPH_SMOOTH_AUX_VTK = OUTPUT_FOLDER + "/aux/graph_3.vtk"
    PATH_GRAPH_SMOOTH_AUX_GRAPHML = OUTPUT_FOLDER + "/aux/graph_3.graphml"


    print("\nSKELETONIZING...")
    skeletonize_stl(PATH_STL, POS_TRAQUEA, OUTPUT_FOLDER+"/aux")
    
    print("\nPROCESSING...")
    process_graph_csv(PATH_GRAPH_0, PATH_GRAPH_1, update_euclidean_dist_father=True)
    csv_to_vtk_graphml(PATH_GRAPH_1, PATH_GRAPH_1_VTK, PATH_GRAPH_1_GRAPHML)

    print("\nCONTRACTING...")
    contract_from_csv(PATH_GRAPH_1, PATH_GRAPH_2)
    csv_to_vtk_graphml(PATH_GRAPH_2, PATH_GRAPH_2_VTK, PATH_GRAPH_2_GRAPHML)

    print("\nPRUNING...")
    print("Smooth skeleton...")
    prune_graph(PATH_GRAPH_1, PATH_GRAPH_1_GRAPHML, PATH_TERMINALS_TO_KEEP, POS_TRAQUEA, PATH_GRAPH_SMOOTH_AUX)
    print("\nSaving...")
    csv_to_vtk_graphml(PATH_GRAPH_SMOOTH_AUX, PATH_GRAPH_SMOOTH_AUX_VTK, PATH_GRAPH_SMOOTH_AUX_GRAPHML)

    print("Simple skeleton...")
    prune_graph(PATH_GRAPH_2, PATH_GRAPH_2_GRAPHML, PATH_TERMINALS_TO_KEEP, POS_TRAQUEA, PATH_GRAPH_3)
    print("\nSaving...")
    csv_to_vtk_graphml(PATH_GRAPH_3, PATH_GRAPH_3_VTK, PATH_GRAPH_3_GRAPHML)

    print("\nPROCESSING...")
    process_graph_csv(PATH_GRAPH_3, PATH_GRAPH_4, update_euclidean_dist_father=False)

    print("\nCONTRACTING...")
    contract_from_csv(PATH_GRAPH_4, PATH_GRAPH_5)
    csv_to_vtk_graphml(PATH_GRAPH_5, PATH_GRAPH_5_VTK, PATH_GRAPH_5_GRAPHML)

    print("\nDONE! ALL OUTPUT IS FOUND IN " + OUTPUT_FOLDER + "/aux")
    print("\nNow consider running extract_data...\n")
