"""
matrix_solver.py
================
Module: Matrix Formulation (Sunidhi Singh)
Project: Graph Theory Based Electric Circuit Solver

Responsibility:
    - Receive graph data (nodes + branches) from the Graph Builder
    - Apply KCL and KVL using Modified Nodal Analysis (MNA)
    - Build conductance matrix G and current vector I
    - Output G and I so the Numerical Solver (Khushi) can solve G * V = I

Supported components:
    - R  : Resistor
    - V  : Voltage source (independent)
    - I  : Current source (independent)

Input format (what Aayush's graph_builder.py must provide):
    {
        "nodes": [0, 1, 2, 3],          # list of node IDs (0 = ground)
        "branches": [
            {"name": "R1", "type": "R", "node1": 1, "node2": 2, "value": 10},
            {"name": "V1", "type": "V", "node1": 1, "node2": 0, "value": 12},
            {"name": "I1", "type": "I", "node1": 0, "node2": 2, "value": 0.5},
        ]
    }

    Convention for current sources:
        - "node1" is where current flows OUT OF
        - "node2" is where current flows INTO
        So I1 with node1=0, node2=2 means current flows INTO node 2

Output format (what this module returns):
    {
        "G_matrix": numpy 2D array,   # the conductance/MNA matrix
        "I_vector": numpy 1D array,   # the source vector
        "node_index": dict,           # maps node ID -> matrix row index
        "vsource_index": dict,        # maps voltage source name -> matrix row index
        "num_nodes": int,             # number of non-ground nodes
        "num_vsources": int           # number of voltage sources
    }

How to solve (Khushi's job):
    V_result = numpy.linalg.solve(G_matrix, I_vector)
    The first num_nodes values = node voltages
    The remaining values = currents through voltage sources
"""

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def build_mna_matrix(circuit_data: dict) -> dict:
    """
    Build the MNA (Modified Nodal Analysis) matrix system G * x = I
    from circuit graph data.

    Parameters
    ----------
    circuit_data : dict
        Must contain:
            "nodes"    -> list of node IDs (int). 0 is always ground.
            "branches" -> list of branch dicts, each with:
                          "name"  (str)   - component label e.g. "R1"
                          "type"  (str)   - "R", "V", or "I"
                          "node1" (int)   - first terminal node
                          "node2" (int)   - second terminal node
                          "value" (float) - resistance (Ω), voltage (V), or current (A)

    Returns
    -------
    dict with keys:
        G_matrix      : np.ndarray  - the full MNA matrix
        I_vector      : np.ndarray  - the right-hand side vector
        node_index    : dict        - {node_id: matrix_row}
        vsource_index : dict        - {source_name: matrix_row}
        num_nodes     : int
        num_vsources  : int
    """

    nodes    = circuit_data["nodes"]
    branches = circuit_data["branches"]

    # ── Step 1: Index non-ground nodes ────────────────────────────────────────
    # Ground (node 0) is our reference — it does NOT get a row/column.
    # Every other node gets an index starting from 0.
    #
    # Example: nodes = [0, 1, 2, 3]
    #   node_index = {1: 0, 2: 1, 3: 2}
    #   num_nodes  = 3

    non_ground_nodes = sorted([n for n in nodes if n != 0])
    node_index = {node: idx for idx, node in enumerate(non_ground_nodes)}
    num_nodes  = len(non_ground_nodes)

    # ── Step 2: Find all voltage sources and index them ───────────────────────
    # Voltage sources get EXTRA rows and columns appended after the node rows.
    # This is the core idea of MNA — we track the current through each V source
    # as an additional unknown.

    vsources = [b for b in branches if b["type"] == "V"]
    vsource_index = {}
    for idx, vs in enumerate(vsources):
        vsource_index[vs["name"]] = num_nodes + idx  # row comes after node rows
    num_vsources = len(vsources)

    # ── Step 3: Allocate the G matrix and I vector ────────────────────────────
    # Total matrix size = (num_nodes + num_vsources) x (num_nodes + num_vsources)
    # Example: 3 nodes + 1 voltage source → 4x4 matrix

    size     = num_nodes + num_vsources
    G_matrix = np.zeros((size, size), dtype=float)
    I_vector = np.zeros(size, dtype=float)

    # ── Step 4: Stamp each component into the matrix ─────────────────────────
    # "Stamping" = adding a component's contribution to specific matrix positions.
    # Each component type has a known stamping pattern.

    for branch in branches:
        name  = branch["name"]
        btype = branch["type"].upper()
        n1    = branch["node1"]
        n2    = branch["node2"]
        val   = float(branch["value"])

        # ── Resistor stamp ────────────────────────────────────────────────────
        #
        # A resistor between nodes n1 and n2 with resistance R
        # has conductance g = 1/R
        #
        # KCL contribution at n1:  +g * V_n1  -g * V_n2  = 0
        # KCL contribution at n2:  -g * V_n1  +g * V_n2  = 0
        #
        # Matrix positions:
        #   G[n1][n1] += g     G[n1][n2] -= g
        #   G[n2][n1] -= g     G[n2][n2] += g
        #
        # If a terminal is ground (node 0), that row/column doesn't exist → skip it.

        if btype == "R":
            if val == 0:
                raise ValueError(f"Resistor '{name}' has zero resistance (short circuit).")

            g = 1.0 / val  # conductance

            if n1 != 0 and n2 != 0:
                r1, r2 = node_index[n1], node_index[n2]
                G_matrix[r1][r1] += g
                G_matrix[r1][r2] -= g
                G_matrix[r2][r1] -= g
                G_matrix[r2][r2] += g

            elif n1 != 0:   # n2 is ground
                r1 = node_index[n1]
                G_matrix[r1][r1] += g

            elif n2 != 0:   # n1 is ground
                r2 = node_index[n2]
                G_matrix[r2][r2] += g

        # ── Voltage source stamp ──────────────────────────────────────────────
        #
        # A voltage source V between n1 (+) and n2 (-) adds:
        # 1. A row for the KVL constraint: V_n1 - V_n2 = V_value
        # 2. Columns tracking the unknown current through the source (I_vs)
        #
        # The source's row index is vs_row = vsource_index[name]
        #
        # G[n1][vs_row] += +1   (current enters n1 from the source)
        # G[n2][vs_row] += -1   (current leaves n2 into the source)
        # G[vs_row][n1] += +1   (KVL: +V_n1)
        # G[vs_row][n2] += -1   (KVL: -V_n2)
        # I[vs_row]      = V_value

        elif btype == "V":
            vs_row = vsource_index[name]

            if n1 != 0:
                r1 = node_index[n1]
                G_matrix[r1][vs_row]  += 1.0
                G_matrix[vs_row][r1]  += 1.0

            if n2 != 0:
                r2 = node_index[n2]
                G_matrix[r2][vs_row]  -= 1.0
                G_matrix[vs_row][r2]  -= 1.0

            I_vector[vs_row] = val   # the known voltage value goes on the right side

        # ── Current source stamp ──────────────────────────────────────────────
        #
        # A current source between n1 and n2 with value I_val:
        # Convention: current flows FROM n1 INTO n2
        #
        # KCL effect:
        #   Node n2 receives +I_val (current is injected IN)
        #   Node n1 loses   -I_val (current is drawn OUT)
        #
        # I[n2] += +I_val
        # I[n1] -= +I_val

        elif btype == "I":
            if n2 != 0:
                r2 = node_index[n2]
                I_vector[r2] += val

            if n1 != 0:
                r1 = node_index[n1]
                I_vector[r1] -= val

        else:
            print(f"[WARNING] Unknown component type '{btype}' for '{name}' — skipped.")

    # ── Step 5: Return everything the solver needs ────────────────────────────
    return {
        "G_matrix":     G_matrix,
        "I_vector":     I_vector,
        "node_index":   node_index,
        "vsource_index": vsource_index,
        "num_nodes":    num_nodes,
        "num_vsources": num_vsources
    }



def print_matrix_system(result: dict):
    """Pretty-print the G matrix and I vector for debugging."""
    G      = result["G_matrix"]
    I      = result["I_vector"]
    n_n    = result["num_nodes"]
    n_vs   = result["num_vsources"]
    ni     = result["node_index"]
    vsi    = result["vsource_index"]

    # Build row labels
    labels = [""] * (n_n + n_vs)
    for node, idx in ni.items():
        labels[idx] = f"V_node{node}"
    for name, idx in vsi.items():
        labels[idx] = f"I_{name}"

    print("\n" + "="*55)
    print("  MNA Matrix System:  G * x = I")
    print("="*55)
    print(f"  Matrix size: {G.shape[0]} x {G.shape[1]}")
    print(f"  Non-ground nodes : {n_n}")
    print(f"  Voltage sources  : {n_vs}")
    print()

    # Header
    col_w = 10
    header = "         " + "".join(f"{lbl:>{col_w}}" for lbl in labels)
    print(header)
    print("         " + "-" * (col_w * len(labels)))

    # Rows
    for i, lbl in enumerate(labels):
        row_str = f"{lbl:>8} |"
        for j in range(len(labels)):
            row_str += f"{G[i][j]:>{col_w}.4f}"
        row_str += f"  |  {I[i]:>8.4f}"
        print(row_str)

    print("="*55)
    print()


if __name__ == "__main__":

    print("\n" + "="*55)
    print("  TEST 1: Simple resistor ladder with voltage source")
    print("="*55)
    # Circuit:
    #   V1 = 12V between node 1 (+) and ground (0)
    #   R1 = 10Ω between node 1 and node 2
    #   R2 = 5Ω  between node 2 and node 3
    #   R3 = 20Ω between node 3 and ground (0)
    # Expected node voltages ≈ {1: 12V, 2: 7.5V, 3: 2.14V}

    circuit_1 = {
        "nodes": [0, 1, 2, 3],
        "branches": [
            {"name": "V1", "type": "V", "node1": 1, "node2": 0, "value": 12},
            {"name": "R1", "type": "R", "node1": 1, "node2": 2, "value": 10},
            {"name": "R2", "type": "R", "node1": 2, "node2": 3, "value": 5},
            {"name": "R3", "type": "R", "node1": 3, "node2": 0, "value": 20},
        ]
    }

    result_1 = build_mna_matrix(circuit_1)
    print_matrix_system(result_1)

    # Solve it here to verify (this is Khushi's job in production)
    x = np.linalg.solve(result_1["G_matrix"], result_1["I_vector"])
    print("  Solved node voltages:")
    for node, idx in result_1["node_index"].items():
        print(f"    V_node{node} = {x[idx]:.4f} V")
    for name, idx in result_1["vsource_index"].items():
        print(f"    I_{name}    = {x[idx]:.4f} A")


    print("\n" + "="*55)
    print("  TEST 2: Circuit with current source")
    print("="*55)
    # Circuit:
    #   I1 = 2A current source from ground into node 1
    #   R1 = 5Ω  between node 1 and node 2
    #   R2 = 10Ω between node 1 and ground
    #   R3 = 5Ω  between node 2 and ground

    circuit_2 = {
        "nodes": [0, 1, 2],
        "branches": [
            {"name": "I1", "type": "I", "node1": 0, "node2": 1, "value": 2},
            {"name": "R1", "type": "R", "node1": 1, "node2": 2, "value": 5},
            {"name": "R2", "type": "R", "node1": 1, "node2": 0, "value": 10},
            {"name": "R3", "type": "R", "node1": 2, "node2": 0, "value": 5},
        ]
    }

    result_2 = build_mna_matrix(circuit_2)
    print_matrix_system(result_2)

    x2 = np.linalg.solve(result_2["G_matrix"], result_2["I_vector"])
    print("  Solved node voltages:")
    for node, idx in result_2["node_index"].items():
        print(f"    V_node{node} = {x2[idx]:.4f} V")


    print("\n" + "="*55)
    print("  TEST 3: Mixed — R + V + I sources")
    print("="*55)
    # Circuit:
    #   V1 = 10V from ground to node 1
    #   R1 = 4Ω  between node 1 and node 2
    #   I1 = 1A  current source from ground into node 2
    #   R2 = 8Ω  between node 2 and ground

    circuit_3 = {
        "nodes": [0, 1, 2],
        "branches": [
            {"name": "V1", "type": "V", "node1": 1, "node2": 0, "value": 10},
            {"name": "R1", "type": "R", "node1": 1, "node2": 2, "value": 4},
            {"name": "I1", "type": "I", "node1": 0, "node2": 2, "value": 1},
            {"name": "R2", "type": "R", "node1": 2, "node2": 0, "value": 8},
        ]
    }

    result_3 = build_mna_matrix(circuit_3)
    print_matrix_system(result_3)

    x3 = np.linalg.solve(result_3["G_matrix"], result_3["I_vector"])
    print("  Solved node voltages:")
    for node, idx in result_3["node_index"].items():
        print(f"    V_node{node} = {x3[idx]:.4f} V")
    for name, idx in result_3["vsource_index"].items():
        print(f"    I_{name}    = {x3[idx]:.4f} A")

    print("\n  All tests passed! matrix_solver.py is ready.\n")
