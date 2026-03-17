def format_node_voltages(node_voltages):
    formatted = []
    for node, voltage in sorted(node_voltages.items()):
        formatted.append(f"V{node} = {voltage} V")
    return formatted


def format_branch_currents(branch_currents):
    formatted = []
    for branch, current in branch_currents.items():
        formatted.append(f"{branch} = {current} A")
    return formatted