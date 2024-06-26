import bronch-skele as sk

PATH_STL_16 = ""
PATH_STL_FULL = ""

PATH_TERMINALS_TO_KEEP_16 = ""
PATH_TERMINALS_TO_KEEP_FULL = ""

OUTPUT_FOLDER_16 = "./lung_16"
OUTPUT_FOLDER_FULL = "./lung_full"

POS_TRACHEA = (0.45, 13.4, -1.4)
POS_PROPAGATE_LOBES = {"RS": [(-4.43, 9.38, -12.69)],
                       "RM": [(-5.99, 8.93, -16.7)],
                       "RI": [(-4.72, 18.6, -16.92), (-0.29, 20.3, -12.36)],
                       "LS": [(3.29, 9.35, -9.8)],
                       "LI": [(5.32, 22.47, -15.51)]}

# Folders containing .stl files of secondary lung lobules and left / right lung:
PATH_LOBULES = ""  
PATH_LOBES = ""
PATH_LUNG_RIGHT = ""
PATH_LUNG_LEFT = ""

# ---------- SKELETON EXTRACTION FOR BOTH MESHES -----------

# LUNG_16, arrives to 17th generation
sk.stl2skel(PATH_STL_16, POS_TRACHEA, PATH_TERMINALS_TO_KEEP_16, OUTPUT_FOLDER_16)
print("NOW EXTRACTING DATA...")
sk.extract_data(OUTPUT_FOLDER_16, POS_TRACHEA, POS_PROPAGATE_LOBES)
sk.intrabronchial_distance(OUTPUT_FOLDER_16 + "/aux/graph_2.graphml", POS_TRACHEA, OUTPUT_FOLDER_16 + "/D.txt")
sk.extract_terminals_for_bm(OUTPUT_FOLDER_16 + "/aux/graph_2.graphml", POS_TRACHEA, PATH_LOBULES, PATH_LOBES,
                             PATH_LUNG_RIGHT, PATH_LUNG_LEFT, OUTPUT_FOLDER_16 + "/terminals.txt")

# LUNG_FULL, arrives to 23rd generation
sk.stl2skel(PATH_STL_FULL, POS_TRACHEA, PATH_TERMINALS_TO_KEEP_FULL, OUTPUT_FOLDER_FULL)
print("NOW EXTRACTING DATA...")
sk.extract_data(OUTPUT_FOLDER_FULL, POS_TRACHEA, POS_PROPAGATE_LOBES)
sk.intrabronchial_distance(OUTPUT_FOLDER_FULL + "/aux/graph_2.graphml", POS_TRACHEA, OUTPUT_FOLDER_FULL + "/D.txt")
sk.extract_terminals_for_bm(OUTPUT_FOLDER_FULL + "/aux/graph_2.graphml", POS_TRACHEA, PATH_LOBULES, PATH_LOBES,
                             PATH_LUNG_RIGHT, PATH_LUNG_LEFT, OUTPUT_FOLDER_FULL + "/terminals.txt")


