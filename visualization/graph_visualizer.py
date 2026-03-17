import networkx as nx
import matplotlib.pyplot as plt

def load_circuit(file_path):

    edges = []
    labels = {}

    with open(file_path, "r") as file:
        for line in file:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) < 4:
                print("Skipping invalid line:", line)
                continue

            component = parts[0]
            node1 = int(parts[1])
            node2 = int(parts[2])
            value = parts[3]

            edges.append((node1, node2))
            labels[(node1, node2)] = f"{component} ({value})"

    return edges, labels


def draw_circuit(edges, labels):

    G = nx.Graph()

    for edge in edges:
        G.add_edge(edge[0], edge[1])

    try:
        pos = nx.planar_layout(G)
    except:
        pos = nx.spring_layout(G)

    fig, ax = plt.subplots()

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=2000,
        node_color="lightblue",
        font_size=12,
        font_weight="bold",
        ax=ax
    )

    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax)

    ax.set_title("Circuit Graph Representation")

    return fig