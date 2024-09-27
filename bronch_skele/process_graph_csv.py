import numpy as np
import pandas as pd
import math

def process_graph_csv(input_graph_csv: str, output_graph_csv: str, update_euclidean_dist_father: id):
    """ Processes the input graph. That is, updates the number of daughter of each node, the number of daughters of the
    father of each node, determining which nodes may be contracted, and optionally computing the Euclidean distance to
    the father of each node (this should only be done once after test_skeletonization). """

    table = pd.read_csv(input_graph_csv, header=None)
    num_columns = len(table.columns)
    if num_columns == 10:
        column_names = ["node_id", "parent_id", "x", "y", "z", "radius", "num_daughters",
                        "num_daughters_of_father", "distance_to_father", "to_contract"]
        table.columns = column_names
    else:
        column_names = ["node_id", "parent_id", "x", "y", "z", "radius"]
        table.columns = column_names

    # First we count the number of daughters of each node
    print("\nNow counting daughters...")
    daughters = np.zeros(len(table))
    for idx, row in table.iterrows():
        parent_id = row["parent_id"]
        if parent_id != -1:
            daughters[table.index[table["node_id"] == int(parent_id)]] += 1
        if int(idx) % 30000 == 0:
            print(f"\r{idx}/{len(table)}", end="")
    table["num_daughters"] = daughters

    # We count the number of daughters of each father
    print("\nNow counting daughters of father...")
    arr = np.zeros(len(table))
    for idx, row in table.iterrows():
        parent_id = row["parent_id"]
        if parent_id != -1:
            num_daughter_of_father = table["num_daughters"][table.index[table["node_id"] == int(parent_id)]]
            if len(num_daughter_of_father) != 0:
                arr[idx] = num_daughter_of_father
        if int(idx) % 30000 == 0:
            print(f"\r{idx}/{len(table)}", end="")
    table["num_daughters_of_father"] = arr

    if update_euclidean_dist_father is True:
        print("\nNow computing euclidean distance to father...")
        arr = np.zeros(len(table))
        for idx, row in table.iterrows():
            parent_id = row["parent_id"]
            if parent_id != -1:
                row_dad = table.iloc[int(parent_id)]
                dx = row_dad["x"] - row["x"]
                dy = row_dad["y"] - row["y"]
                dz = row_dad["z"] - row["z"]
                d = math.sqrt(np.sum(dx * dx + dy * dy + dz * dz))
                arr[idx] = d
            else:
                arr[idx] = -1
            if int(idx) % 30000 == 0:
                print(f"\r{idx}/{len(table)}", end="")
        table["distance_to_father"] = arr

    # Identify nodes to contract
    print("\nNow identifying nodes to contract...")
    arr = np.zeros(len(table))
    for idx, row in table.iterrows():
        parent_id = row["parent_id"]
        if parent_id != -1:
            if row["num_daughters"] == 1:  # and row["num_daughters_of_father"] == 1:
                arr[idx] = 1
        if int(idx) % 30000 == 0:
            print(f"\r{idx}/{len(table)}", end="")
    table["to_contract"] = arr

    # Write data
    table.to_csv(output_graph_csv, header=None, index=False)

    return
