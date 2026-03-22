import numpy as np
from integration.solver import run_solver

# Dummy matrices (for testing)
G = np.array([
    [0.2, -0.1],
    [-0.1, 0.3]
])

I = np.array([1, 0])

node_mapping = {
    1: 0,
    2: 1
}

edges = [
    ("R1", 1, 2, 10),
    ("R2", 2, 0, 5)
]

result = run_solver(G, I, node_mapping, edges)

print("\nNode Voltages:")
print(result["node_voltages"])

print("\nBranch Currents:")
print(result["branch_currents"])
