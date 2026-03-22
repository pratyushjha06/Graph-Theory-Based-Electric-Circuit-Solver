from visualization.graph_visualizer import load_circuit
from integration.api import solve_circuit


def main():
    file_path = "data/sample_circuit.txt"

    # Still load for visualization (edges, labels), if your UI uses them
    edges, labels = load_circuit(file_path)

    # ✅ Graph builder is now used inside solve_circuit(file_path)
    node_voltages, branch_currents = solve_circuit(file_path)

    print("Node Voltages:")
    for node, v in node_voltages.items():
        print(f"V{node} = {v} V")

    print("\nBranch Currents:")
    for b, i in branch_currents.items():
        print(f"{b} = {i} A")


if __name__ == "__main__":
    main()