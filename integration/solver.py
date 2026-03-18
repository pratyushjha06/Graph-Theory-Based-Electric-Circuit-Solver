import numpy as np

def solve_matrix(G, I):
    """
    Solve GV = I
    """
    try:
        V = np.linalg.solve(G, I)
        return V
    except Exception as e:
        print("Error solving matrix:", e)
        return None
    
def compute_node_voltages(V, node_mapping):
    node_voltages = {}

    for node, idx in node_mapping.items():
        node_voltages[node] = float(V[idx])

    # Ground node
    node_voltages[0] = 0.0

    return node_voltages

def compute_branch_currents(node_voltages, edges):
    branch_currents = {}

    for comp in edges:
        name, n1, n2, value = comp

        if name.startswith('R'):  # resistor
            v1 = node_voltages.get(n1, 0)
            v2 = node_voltages.get(n2, 0)

            current = (v1 - v2) / value
            branch_currents[name] = float(current)

    return branch_currents
       