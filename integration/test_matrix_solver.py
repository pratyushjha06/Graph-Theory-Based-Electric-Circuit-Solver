# integration/test_matrix_solver.py
# ─────────────────────────────────────────────────────────────────────────────
# Standalone tests for matrix_solver.py (Sunidhi's module)
# Run from the PROJECT ROOT folder with:
#     python integration/test_matrix_solver.py
#
# No other team member's code needed. Fully independent.
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os

# Make sure Python can find the project root even when run from any folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from integration.matrix_solver import build_mna_matrix


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1 — Resistor ladder with a voltage source
# ─────────────────────────────────────────────────────────────────────────────
# Circuit diagram:
#
#   V1(12V)  R1(10Ω)  R2(5Ω)
#   [1]──────[2]──────[3]
#    |                  |
#   GND               R3(20Ω)
#                       |
#                      GND
#
# Expected: V_node1 = 12V (forced by voltage source)

def test_resistor_ladder_with_voltage_source():
    circuit = {
        "nodes": [0, 1, 2, 3],
        "branches": [
            {"name": "V1", "type": "V", "node1": 1, "node2": 0, "value": 12},
            {"name": "R1", "type": "R", "node1": 1, "node2": 2, "value": 10},
            {"name": "R2", "type": "R", "node1": 2, "node2": 3, "value": 5},
            {"name": "R3", "type": "R", "node1": 3, "node2": 0, "value": 20},
        ]
    }

    result = build_mna_matrix(circuit)
    x = np.linalg.solve(result["G_matrix"], result["I_vector"])

    v_node1 = x[result["node_index"][1]]

    # Node 1 is directly connected to V1 = 12V, so it must be exactly 12V
    assert abs(v_node1 - 12.0) < 1e-6, \
        f"FAIL — Expected V_node1=12.0, got {v_node1:.6f}"

    print("  PASS — Test 1: Resistor ladder with voltage source")
    print(f"         V_node1={x[result['node_index'][1]]:.4f}V  "
          f"V_node2={x[result['node_index'][2]]:.4f}V  "
          f"V_node3={x[result['node_index'][3]]:.4f}V")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2 — Current source only circuit
# ─────────────────────────────────────────────────────────────────────────────
# Circuit:
#   I1 = 2A injected into node 1 from ground
#   R1 = 5Ω  between node 1 and node 2
#   R2 = 10Ω between node 1 and ground
#   R3 = 5Ω  between node 2 and ground
#
# KCL at node 1: 2 = V1/10 + (V1-V2)/5
# KCL at node 2: (V1-V2)/5 = V2/5
# Expected solution: V_node1 ≈ 8V, V_node2 ≈ 4V

def test_current_source_circuit():
    circuit = {
        "nodes": [0, 1, 2],
        "branches": [
            {"name": "I1", "type": "I", "node1": 0, "node2": 1, "value": 2},
            {"name": "R1", "type": "R", "node1": 1, "node2": 2, "value": 5},
            {"name": "R2", "type": "R", "node1": 1, "node2": 0, "value": 10},
            {"name": "R3", "type": "R", "node1": 2, "node2": 0, "value": 5},
        ]
    }

    result = build_mna_matrix(circuit)
    x = np.linalg.solve(result["G_matrix"], result["I_vector"])

    v_node1 = x[result["node_index"][1]]
    v_node2 = x[result["node_index"][2]]

    assert abs(v_node1 - 10.0) < 1e-6, \
        f"FAIL — Expected V_node1=10.0, got {v_node1:.6f}"
    assert abs(v_node2 - 5.0) < 1e-6, \
        f"FAIL — Expected V_node2=5.0, got {v_node2:.6f}"

    print("  PASS — Test 2: Current source circuit")
    print(f"         V_node1={v_node1:.4f}V  V_node2={v_node2:.4f}V")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3 — Mixed: R + Voltage source + Current source
# ─────────────────────────────────────────────────────────────────────────────
# Circuit:
#   V1 = 10V  from ground to node 1 (node 1 forced to 10V)
#   R1 = 4Ω   between node 1 and node 2
#   I1 = 1A   injected into node 2 from ground
#   R2 = 8Ω   between node 2 and ground

def test_mixed_r_v_i():
    circuit = {
        "nodes": [0, 1, 2],
        "branches": [
            {"name": "V1", "type": "V", "node1": 1, "node2": 0, "value": 10},
            {"name": "R1", "type": "R", "node1": 1, "node2": 2, "value": 4},
            {"name": "I1", "type": "I", "node1": 0, "node2": 2, "value": 1},
            {"name": "R2", "type": "R", "node1": 2, "node2": 0, "value": 8},
        ]
    }

    result = build_mna_matrix(circuit)
    x = np.linalg.solve(result["G_matrix"], result["I_vector"])

    v_node1 = x[result["node_index"][1]]
    v_node2 = x[result["node_index"][2]]

    # Node 1 is forced to 10V by the voltage source
    assert abs(v_node1 - 10.0) < 1e-6, \
        f"FAIL — Expected V_node1=10.0, got {v_node1:.6f}"

    print("  PASS — Test 3: Mixed R + V + I sources")
    print(f"         V_node1={v_node1:.4f}V  V_node2={v_node2:.4f}V")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4 — Matrix shape is correct
# ─────────────────────────────────────────────────────────────────────────────
# 2 non-ground nodes + 1 voltage source → matrix must be 3×3

def test_matrix_shape():
    circuit = {
        "nodes": [0, 1, 2],
        "branches": [
            {"name": "V1", "type": "V", "node1": 1, "node2": 0, "value": 5},
            {"name": "R1", "type": "R", "node1": 1, "node2": 2, "value": 10},
            {"name": "R2", "type": "R", "node1": 2, "node2": 0, "value": 10},
        ]
    }

    result = build_mna_matrix(circuit)
    G = result["G_matrix"]

    assert G.shape == (3, 3), \
        f"FAIL — Expected shape (3,3), got {G.shape}"
    assert result["num_nodes"] == 2, \
        f"FAIL — Expected num_nodes=2, got {result['num_nodes']}"
    assert result["num_vsources"] == 1, \
        f"FAIL — Expected num_vsources=1, got {result['num_vsources']}"

    print("  PASS — Test 4: Matrix shape is correct")
    print(f"         G shape={G.shape}  num_nodes={result['num_nodes']}  "
          f"num_vsources={result['num_vsources']}")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5 — Output format matches what Khushi's solver expects
# ─────────────────────────────────────────────────────────────────────────────
# Verifies that the returned dict has all required keys with correct types

def test_output_format():
    circuit = {
        "nodes": [0, 1, 2],
        "branches": [
            {"name": "V1", "type": "V", "node1": 1, "node2": 0, "value": 5},
            {"name": "R1", "type": "R", "node1": 1, "node2": 2, "value": 10},
        ]
    }

    result = build_mna_matrix(circuit)

    required_keys = ["G_matrix", "I_vector", "node_index",
                     "vsource_index", "num_nodes", "num_vsources"]

    for key in required_keys:
        assert key in result, f"FAIL — Missing key '{key}' in output"

    assert isinstance(result["G_matrix"],    np.ndarray), "FAIL — G_matrix must be np.ndarray"
    assert isinstance(result["I_vector"],    np.ndarray), "FAIL — I_vector must be np.ndarray"
    assert isinstance(result["node_index"],  dict),       "FAIL — node_index must be dict"
    assert isinstance(result["vsource_index"], dict),     "FAIL — vsource_index must be dict"

    print("  PASS — Test 5: Output format is correct for integration")
    print(f"         Keys present: {list(result.keys())}")


# ─────────────────────────────────────────────────────────────────────────────
# RUN ALL TESTS
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("=" * 55)
    print("  matrix_solver.py — Test Suite")
    print("  Module by: Sunidhi Singh")
    print("=" * 55)
    print()

    tests = [
        test_resistor_ladder_with_voltage_source,
        test_current_source_circuit,
        test_mixed_r_v_i,
        test_matrix_shape,
        test_output_format,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR in {test.__name__}: {e}")
            failed += 1

    print()
    print("=" * 55)
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 55)
    print()

    if failed > 0:
        sys.exit(1)   # non-zero exit so Git CI can catch failures