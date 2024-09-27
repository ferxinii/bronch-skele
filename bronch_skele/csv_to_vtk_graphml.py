import pandas as pd
import vtk
import numpy as np
import networkx as nx


def csv_to_vtk_graphml(input_path_csv: str, output_path_vtk: str, output_path_graphml: str):
    column_names = ["node_id", "parent_id", "x", "y", "z", "radius", "num_daughters",
                    "num_daughter_of_father", "distance_to_father", "to_contract"]
    table = pd.read_csv(input_path_csv, header=None)
    table.columns = column_names
    # First produce vtk
    polydata = vtk.vtkPolyData()
    points_vtk = vtk.vtkPoints()
    lines = vtk.vtkCellArray()

    for idx, row in table.iterrows():
        x = row["x"]
        y = row["y"]
        z = row["z"]
        points_vtk.InsertNextPoint((x, y, z))

        father_id = np.where(table["node_id"] == row["parent_id"])[0]
        if len(father_id) != 0:
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, int(father_id[0]))
            line.GetPointIds().SetId(1, idx)  # Use index of point in list
            lines.InsertNextCell(line)

    polydata.SetPoints(points_vtk)
    polydata.SetLines(lines)

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(output_path_vtk)
    writer.SetInputData(polydata)
    writer.Write()

    # Now produce graph
    graph = nx.Graph()
    for idx, row in table.iterrows():
        xyzr = list(row[["x", "y", "z", "radius"]])
        graph.add_node(idx, x=xyzr[0], y=xyzr[1], z=xyzr[2], r=xyzr[3])
        father_id = np.where(table["node_id"] == row["parent_id"])[0]
        if len(father_id) != 0:
            graph.add_edge(father_id[0], idx, weight=row["distance_to_father"])

    nx.write_graphml(graph, output_path_graphml)
