import numpy as np

def solve_matrix(G, I):
    """
    Solve GV = I
    """
    try:
        V = np.linalg.solve(G, I)
        return V
    except Exception as e:
        return None


def compute_node_voltages(V, node_mapping):
    node_voltages = {}

    for node, idx in node_mapping.items():
        node_voltages[node] = round(float(V[idx]), 4)

    # Ground node
    node_voltages[0] = 0.0

    return node_voltages


def compute_branch_currents(node_voltages, edges):
    branch_currents = {}

    for comp in edges:

        # SAFETY CHECK
        if len(comp) != 4:
            print("Skipping invalid edge:", comp)
            continue

        name, n1, n2, value = comp

        if name.startswith('R'):

            if value == 0:
                continue

            v1 = node_voltages.get(n1, 0)
            v2 = node_voltages.get(n2, 0)

            current = (v1 - v2) / value
            branch_currents[name] = round(float(current), 4)

    return branch_currents

def run_solver(G, I, node_mapping, edges):
    """
    Main solver pipeline
    """

    # Step 1: Solve matrix
    V = solve_matrix(G, I)

    if V is None:
        return {"error": "Matrix solve failed (possibly singular matrix)"}

    # Step 2: Node voltages
    node_voltages = compute_node_voltages(V, node_mapping)

    # Step 3: Branch currents
    branch_currents = compute_branch_currents(node_voltages, edges)

    return {
        "node_voltages": node_voltages,
        "branch_currents": branch_currents
    }
    