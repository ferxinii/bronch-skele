import bronch-skele as sk

PATH_STL = ""

PATH_TERMINALS_TO_KEEP = ""

OUTPUT_FOLDER = "./lung_full"

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

# ---------- SKELETON EXTRACTION, INTRABRONCHIAL DISTANCE MATRIX AND TERMINAL INFORMATION -----------
sk.stl2skel(PATH_STL, POS_TRACHEA, PATH_TERMINALS_TO_KEEP, OUTPUT_FOLDER)
print("NOW EXTRACTING DATA...")
sk.extract_data(OUTPUT_FOLDER, POS_TRACHEA, POS_PROPAGATE_LOBES)
print("INTRABRONCHIAL DISTANCE...")
sk.intrabronchial_distance(OUTPUT_FOLDER + "/aux/graph_2.graphml", POS_TRACHEA, OUTPUT_FOLDER + "/D.txt")
print("TERMINALS FOR BUBBLE MODEL...")
sk.extract_terminals_for_bm(OUTPUT_FOLDER + "/aux/graph_2.graphml", POS_TRACHEA, PATH_LOBULES, PATH_LOBES,
                             PATH_LUNG_RIGHT, PATH_LUNG_LEFT, OUTPUT_FOLDER + "/terminals.txt")

