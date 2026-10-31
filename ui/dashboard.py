"""
UI Module: Executive System Dashboard.
Displays high-level OS metric cards, interactive RAG, resource utilization, and status summaries.
"""

import streamlit as st
import pandas as pd
from ui.state_manager import get_current_state
from core.bankers import is_safe_state
from core.detection import detect_deadlock_multiple_instances, find_rag_cycles
from visualization.resource_graph import create_rag_plotly_figure
from visualization.charts import create_resource_utilization_chart


def render_dashboard():
    """Renders the primary system dashboard."""
    state = get_current_state()

    st.markdown("## 📊 System Overview & Live Dashboard")
    st.markdown(
        "*Real-time status of simulated OS processes, resource allocations, avoidance state, and deadlock detection.*"
    )

    # Compute live algorithms
    safety = is_safe_state(state, find_all=False)
    detection = detect_deadlock_multiple_instances(state)
    cycles = find_rag_cycles(state)

    active_pids = [p for p in state.process_ids if not state.terminated.get(p, False)]
    terminated_pids = [p for p in state.process_ids if state.terminated.get(p, False)]

    # Top Metric Cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if safety.is_safe:
            st.metric(
                label="Banker's Avoidance",
                value="SAFE STATE",
                delta="Safe Sequence Available",
                delta_color="normal",
            )
        else:
            st.metric(
                label="Banker's Avoidance",
                value="UNSAFE STATE",
                delta="Deadlock Risk",
                delta_color="inverse",
            )

    with c2:
        if detection.is_deadlocked:
            st.metric(
                label="Deadlock Detection",
                value=f"{len(detection.deadlocked_processes)} Deadlocked",
                delta="Active Deadlock",
                delta_color="inverse",
            )
        else:
            st.metric(
                label="Deadlock Detection",
                value="DEADLOCK FREE",
                delta="All Progressing",
                delta_color="normal",
            )

    with c3:
        st.metric(
            label="Active Processes",
            value=f"{len(active_pids)} / {state.num_processes}",
            delta=f"{len(terminated_pids)} Terminated" if terminated_pids else "0 Terminated",
            delta_color="off",
        )

    with c4:
        st.metric(
            label="Total Available Units",
            value=f"{sum(state.available)} units",
            delta=f"{len(state.resource_ids)} Resource Types",
            delta_color="off",
        )

    st.markdown("---")

    # Primary Visualization: Resource Allocation Graph
    col_graph, col_util = st.columns([3, 2])

    with col_graph:
        st.markdown("### 🕸️ Resource Allocation Graph (RAG)")
        fig_rag, explanation = create_rag_plotly_figure(state, detection.deadlocked_processes)
        st.plotly_chart(fig_rag, use_container_width=True)
        st.info(explanation)

    with col_util:
        st.markdown("### 📈 Resource Pool Utilization")
        fig_util = create_resource_utilization_chart(state)
        st.plotly_chart(fig_util, use_container_width=True)

        st.markdown("#### ⚡ Quick State Matrix Glance")
        # Format compact table
        need_matrix = state.get_need_matrix()
        summary_rows = []
        for i, pid in enumerate(state.process_ids):
            is_term = state.terminated.get(pid, False)
            summary_rows.append({
                "Process": pid,
                "Status": "TERMINATED" if is_term else ("DEADLOCKED" if pid in detection.deadlocked_processes else "RUNNABLE"),
                "Allocated": str(state.allocation[i]),
                "Max Claim": str(state.maximum[i]),
                "Need": str(need_matrix[i]),
                "Request": str(state.request[i]),
                "Priority": state.priorities.get(pid, 1),
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
