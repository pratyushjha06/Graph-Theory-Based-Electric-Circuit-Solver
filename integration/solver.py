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
        