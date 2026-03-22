# integration/graph_builder.py

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass
class Element:
    name: str     # e.g. "R1", "V1"
    etype: str    # "R", "V", "I", ...
    n1: int
    n2: int
    value: float


@dataclass
class GraphData:
    nodes: List[int]
    elements: List[Element]
    edges: List[Tuple[int, int]]      # ✅ added back
    incidence_matrix: np.ndarray


def parse_circuit_file(file_path: str) -> GraphData:
    elements: List[Element] = []
    edges: List[Tuple[int, int]] = []   # ✅ new
    node_set = set()

    with open(file_path, "r") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("#") or line.startswith("*"):
                continue

            parts = line.split()
            if len(parts) < 4:
                raise ValueError(f"Invalid line in circuit file: '{line}'")

            name = parts[0]
            etype = name[0].upper()
            n1 = int(parts[1])
            n2 = int(parts[2])
            value = float(parts[3])

            elements.append(Element(name=name, etype=etype, n1=n1, n2=n2, value=value))
            edges.append((n1, n2))          # ✅ store edge
            node_set.add(n1)
            node_set.add(n2)

    nodes = sorted(node_set)
    A = build_incidence_matrix(nodes, elements)

    return GraphData(
        nodes=nodes,
        elements=elements,
        edges=edges,                      # ✅ return edges
        incidence_matrix=A,
    )


def build_incidence_matrix(nodes: List[int], elements: List[Element]) -> np.ndarray:
    node_index = {n: i for i, n in enumerate(nodes)}
    A = np.zeros((len(nodes), len(elements)), dtype=float)

    for j, el in enumerate(elements):
        i1 = node_index[el.n1]
        i2 = node_index[el.n2]
        A[i1, j] = 1.0
        A[i2, j] = -1.0

    return A


def build_graph_from_file(file_path: str) -> GraphData:
    return parse_circuit_file(file_path)