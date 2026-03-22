from integration.graph_builder import build_graph_from_file
from integration.matrix_solver import build_mna_matrix
from integration.solver import run_solver


def solve_circuit(file_path, edges):
    # ignore edges from UI; use graph builder
    graph = build_graph_from_file(file_path)
    nodes = graph.nodes
    elements = graph.elements
    edges = graph.edges   # ✅ now exists

    branches = []
    for el in elements:
        branches.append({
            "name": el.name,
            "type": el.etype,
            "node1": el.n1,
            "node2": el.n2,
            "value": el.value,
        })

    circuit_data = {
        "nodes": nodes,
        "branches": branches,
        # "incidence": graph.incidence_matrix,  # optional
    }

    result = build_mna_matrix(circuit_data)
    G = result["G_matrix"]
    I = result["I_vector"]
    node_mapping = result["node_index"]

    solver_edges = [(el.name, el.n1, el.n2, el.value) for el in elements]

    solver_result = run_solver(G, I, node_mapping, solver_edges)

    if "error" in solver_result:
        print("Solver Error:", solver_result["error"])
        return {}, {}

    return solver_result["node_voltages"], solver_result["branch_currents"]