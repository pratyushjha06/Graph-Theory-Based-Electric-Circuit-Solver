import streamlit as st
import os
from visualization.graph_visualizer import load_circuit, draw_circuit
from integration.api import solve_circuit
from results.result_display import format_node_voltages, format_branch_currents


# Page config
st.set_page_config(page_title="Circuit Solver", layout="wide")

# Title
st.title("🔌 Graph-Theory-Based Circuit Solver")
st.markdown("### Visualize and Analyze Electric Circuits")

# Sidebar
st.sidebar.header("⚙️ Controls")

uploaded_file = st.sidebar.file_uploader("Upload Circuit File (.txt)", type=["txt"])
use_sample = st.sidebar.checkbox("Use Sample Circuit", value=True)


# File selection
if uploaded_file is not None:
    file_path = os.path.join("data", "uploaded_circuit.txt")

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.sidebar.success("File uploaded!")

elif use_sample:
    file_path = "data/sample_circuit.txt"
else:
    file_path = None


# Run button
if st.sidebar.button("🚀 Run Solver"):

    if file_path is None:
        st.error("Please upload a file or select sample circuit.")
    else:
        try:
            edges, labels = load_circuit(file_path)

            col1, col2 = st.columns([2, 1])

            # LEFT → Graph
            with col1:
                st.subheader("📊 Circuit Graph")
                fig = draw_circuit(edges, labels)
                st.pyplot(fig)

            # RIGHT → Results
            with col2:
                st.subheader("⚡ Results")

                node_voltages, branch_currents = solve_circuit(file_path, edges)

                voltages = format_node_voltages(node_voltages)
                currents = format_branch_currents(branch_currents)

                st.markdown("#### 🔹 Node Voltages")
                for v in voltages:
                    st.write(f"**{v}**")

                st.markdown("#### 🔹 Branch Currents")
                for c in currents:
                    st.write(f"**{c}**")

            st.success("✅ Simulation Complete")

        except Exception as e:
            st.error(f"Error: {e}")
