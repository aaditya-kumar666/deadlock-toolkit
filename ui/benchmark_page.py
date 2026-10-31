"""
UI Module: Simulator Performance Benchmarking.
Evaluates algorithmic scaling of Banker's Algorithm and Deadlock Detection over process counts
with interactive Plotly graphs and academic disclaimers.
"""

import streamlit as st
import pandas as pd
from visualization.charts import run_benchmark_trials


def render_benchmark_page():
    """Renders the simulator performance benchmark and scaling analysis."""
    st.markdown("## ⚡ Simulator Performance Benchmarks")
    st.markdown(
        "*Empirical runtime analysis of Dijkstra's Banker's Algorithm and Multi-Instance Deadlock Detection.*"
    )

    st.warning(
        "⚠️ **Academic Benchmark Notice:**\n\n"
        "These measurements quantify in-memory Python algorithmic time complexity ($O(m \\cdot n^2)$). "
        "They do **NOT** represent actual operating system kernel context switching or hardware interrupt latencies."
    )

    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.markdown("""
        #### Banker's Algorithm Complexity
        - **Time Complexity:** $O(m \\cdot n^2)$, where $n$ is the number of processes and $m$ is the number of resource types.
        - **Worst-case:** In the worst case, each scan checks $O(n)$ processes against $m$ resources, finding only one process that can finish per iteration, repeating $n$ times.
        - **Space Complexity:** $O(m \\cdot n)$ for matrices ($C, M, N, Q$) and vectors ($E, A, W, F$).
        """)

    with col_info2:
        st.markdown("""
        #### Deadlock Detection Complexity
        - **Time Complexity:** $O(m \\cdot n^2)$ for the multi-instance matrix reduction algorithm.
        - **Single-Instance Graph Cycle Detection:** $O(V + E)$ where $V = n + m$ and $E$ is the number of allocation and request edges.
        - **Trade-off:** Avoidance checks every request dynamically; Detection runs periodically or when resource utilization drops below a threshold.
        """)

    st.markdown("---")

    if "bench_df" not in st.session_state:
        st.session_state["bench_df"] = None
        st.session_state["bench_fig"] = None

    if st.button("🚀 Run Simulator Benchmarks (n=5 to 100)", type="primary"):
        with st.spinner("Executing repeated algorithmic trials across scaling process counts..."):
            df, fig = run_benchmark_trials()
            st.session_state["bench_df"] = df
            st.session_state["bench_fig"] = fig

    if st.session_state["bench_fig"] is not None:
        st.plotly_chart(st.session_state["bench_fig"], use_container_width=True)
        st.dataframe(st.session_state["bench_df"], use_container_width=True, hide_index=True)
    else:
        st.info("Click the button above to run live timing trials and plot the scaling curve.")
