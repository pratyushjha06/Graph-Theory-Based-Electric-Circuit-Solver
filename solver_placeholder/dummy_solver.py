def get_dummy_solution(edges):

    node_voltages = {}
    branch_currents = {}

    # Extract nodes
    nodes = set()
    for u, v in edges:
        nodes.add(u)
        nodes.add(v)

    # Assign dummy voltages
    for node in nodes:
        if node == 0:
            node_voltages[node] = 0
        else:
            node_voltages[node] = round(12 / (node + 1), 2)

    # Assign dummy currents
    for i, (u, v) in enumerate(edges):
        branch_currents[f"I_{u}-{v}"] = round(0.5 / (i + 1), 3)

    return node_voltages, branch_currents