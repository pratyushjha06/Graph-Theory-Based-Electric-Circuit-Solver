from integration.matrix_solver import build_mna_matrix
from integration.solver import run_solver


def solve_circuit(file_path, edges):
    """
    Convert edges → circuit_data → solve
    """

    # 🔹 Step 1: Convert edges to branches format
    branches = []

    for idx, edge in enumerate(edges):
        # edge format: (node1, node2)
        n1, n2 = edge

        # Temporary assumption: all are resistors (for now)
        branches.append({
            "name": f"R{idx+1}",
            "type": "R",
            "node1": n1,
            "node2": n2,
            "value": 10   # default value (IMPORTANT)
        })

    # 🔹 Step 2: Build nodes list
    nodes = set()
    for n1, n2 in edges:
        nodes.add(n1)
        nodes.add(n2)

    nodes = list(nodes)

    # 🔹 Step 3: Build circuit_data
    circuit_data = {
        "nodes": nodes,
        "branches": branches
    }

    # 🔹 Step 4: Matrix generation
    result = build_mna_matrix(circuit_data)

    G = result["G_matrix"]
    I = result["I_vector"]
    node_mapping = result["node_index"]

    # 🔹 Step 5: Convert edges for solver
    solver_edges = []
    for b in branches:
        solver_edges.append((b["name"], b["node1"], b["node2"], b["value"]))

    # 🔹 Step 6: Run solver
    solver_result = run_solver(G, I, node_mapping, solver_edges)

    if "error" in solver_result:
        print("Solver Error:", solver_result["error"])
        return {}, {}

    return solver_result["node_voltages"], solver_result["branch_currents"]
    