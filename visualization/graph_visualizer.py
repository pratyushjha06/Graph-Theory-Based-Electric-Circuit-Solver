import networkx as nx
import matplotlib.pyplot as plt


def load_circuit(file_path):

    edges = []
    labels = {}

    with open(file_path, "r") as file:
        for line in file:

            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            parts = line.split()

            # Skip invalid lines
            if len(parts) < 4:
                print("Skipping invalid line:", line)
                continue

            component = parts[0]
            node1 = int(parts[1])
            node2 = int(parts[2])
            value = parts[3]

            edges.append((node1, node2))
            labels[(node1, node2)] = component + " (" + value + ")"

    return edges, labels


def draw_circuit(edges, labels):

    G = nx.Graph()

    for edge in edges:
        G.add_edge(edge[0], edge[1])

    pos = nx.spring_layout(G)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=2000,
        node_color="lightblue",
        font_size=12,
        font_weight="bold"
    )

    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    plt.title("Circuit Graph Representation")
    plt.show()


if __name__ == "__main__":

    file_path = "data/sample_circuit.txt"

    edges, labels = load_circuit(file_path)

    draw_circuit(edges, labels)