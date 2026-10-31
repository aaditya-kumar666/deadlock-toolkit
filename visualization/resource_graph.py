"""
Visualization module: Interactive Resource Allocation Graph (RAG).
Constructs a directed bipartite graph using NetworkX and renders with Plotly,
with directed edge arrows, node styling, cycle highlighting, and OS academic explanations.
"""

from typing import List, Dict, Tuple, Optional, Any
import networkx as nx
import plotly.graph_objects as go
from core.models import SystemState
from core.detection import find_rag_cycles, is_single_instance_system, detect_deadlock_multiple_instances


def build_rag_networkx_graph(
    state: SystemState, 
    deadlocked_pids: Optional[List[str]] = None
) -> Tuple[nx.DiGraph, Dict[str, Tuple[float, float]], List[List[str]]]:
    """
    Builds a NetworkX DiGraph representing the Resource Allocation Graph.
    Uses a clean bipartite layout (Processes on left, Resources on right).
    """
    if deadlocked_pids is None:
        det = detect_deadlock_multiple_instances(state)
        deadlocked_pids = det.deadlocked_processes

    G = nx.DiGraph()

    # Add Process Nodes
    n = state.num_processes
    m = state.num_resources

    for i, pid in enumerate(state.process_ids):
        is_term = state.terminated.get(pid, False)
        is_dead = pid in deadlocked_pids and not is_term
        G.add_node(
            pid,
            bipartite=0,
            node_type="process",
            index=i,
            is_deadlocked=is_dead,
            is_terminated=is_term,
            priority=state.priorities.get(pid, 1),
            cost=state.costs.get(pid, 10.0),
        )

    # Add Resource Nodes
    for j, rid in enumerate(state.resource_ids):
        tot = state.total[j]
        avail = state.available[j]
        alloc = sum(state.allocation[i][j] for i in range(n))
        G.add_node(
            rid,
            bipartite=1,
            node_type="resource",
            index=j,
            total=tot,
            available=avail,
            allocated=alloc,
        )

    # Add Edges
    for i, pid in enumerate(state.process_ids):
        if state.terminated.get(pid, False):
            continue
        for j, rid in enumerate(state.resource_ids):
            # Assignment edge: R_j -> P_i
            alloc_amt = state.allocation[i][j]
            if alloc_amt > 0:
                G.add_edge(rid, pid, edge_type="allocation", weight=alloc_amt)

            # Request edge: P_i -> R_j
            req_amt = state.request[i][j]
            if req_amt > 0:
                G.add_edge(pid, rid, edge_type="request", weight=req_amt)

    # Detect cycles
    try:
        cycles = list(nx.simple_cycles(G))
    except Exception:
        cycles = []

    # Bipartite Layout: Processes at X=0.2, Resources at X=0.8
    pos: Dict[str, Tuple[float, float]] = {}

    y_p_step = 1.0 / max(n, 1)
    y_p_start = 1.0 - (y_p_step / 2.0)
    for i, pid in enumerate(state.process_ids):
        pos[pid] = (0.2, y_p_start - (i * y_p_step))

    y_r_step = 1.0 / max(m, 1)
    y_r_start = 1.0 - (y_r_step / 2.0)
    for j, rid in enumerate(state.resource_ids):
        pos[rid] = (0.8, y_r_start - (j * y_r_step))

    return G, pos, cycles


def create_rag_plotly_figure(
    state: SystemState, 
    deadlocked_pids: Optional[List[str]] = None
) -> Tuple[go.Figure, str]:
    """
    Renders an interactive Plotly Resource Allocation Graph with directed arrows,
    hover details, cycle highlights, and academic explanation.
    """
    G, pos, cycles = build_rag_networkx_graph(state, deadlocked_pids)
    is_single = is_single_instance_system(state)

    # Extract all edges that participate in any cycle
    cycle_edge_set = set()
    for cyc in cycles:
        for idx in range(len(cyc)):
            u = cyc[idx]
            v = cyc[(idx + 1) % len(cyc)]
            cycle_edge_set.add((u, v))

    fig = go.Figure()

    # Draw Edges via Annotations (directed arrows)
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        e_type = data.get("edge_type", "normal")
        amt = data.get("weight", 1)
        in_cycle = (u, v) in cycle_edge_set

        if in_cycle:
            edge_color = "#EF4444"  # Red for cycle
            line_width = 3
        elif e_type == "allocation":
            edge_color = "#3B82F6"  # Blue for allocation (R -> P)
            line_width = 2
        else:
            edge_color = "#F59E0B"  # Amber for request (P -> R)
            line_width = 2

        # Directed arrow from u to v
        fig.add_annotation(
            ax=x0, ay=y0,
            x=x1, y=y1,
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.2,
            arrowwidth=line_width,
            arrowcolor=edge_color,
            text=f"<b>{amt}</b>" if amt > 1 else "",
            textangle=0,
            font=dict(color=edge_color, size=11),
            align="center",
            opacity=0.9,
        )

    # Separate node categories for plotting
    p_x, p_y, p_text, p_colors, p_symbols = [], [], [], [], []
    r_x, r_y, r_text, r_colors = [], [], [], []

    for node, data in G.nodes(data=True):
        x, y = pos[node]
        if data.get("node_type") == "process":
            p_x.append(x)
            p_y.append(y)
            is_term = data.get("is_terminated", False)
            is_dead = data.get("is_deadlocked", False)
            pri = data.get("priority", 1)
            cost = data.get("cost", 10.0)

            if is_term:
                status_str = "TERMINATED"
                p_colors.append("#6B7280")  # Gray
            elif is_dead:
                status_str = "DEADLOCKED"
                p_colors.append("#EF4444")  # Red
            else:
                status_str = "RUNNABLE / SAFE"
                p_colors.append("#10B981")  # Green

            p_text.append(
                f"<b>Process: {node}</b><br>"
                f"Status: {status_str}<br>"
                f"Priority: {pri}<br>"
                f"Cost: {cost}"
            )
        else:
            r_x.append(x)
            r_y.append(y)
            tot = data.get("total", 0)
            avail = data.get("available", 0)
            alloc = data.get("allocated", 0)
            r_colors.append("#8B5CF6")  # Purple for resources
            r_text.append(
                f"<b>Resource: {node}</b><br>"
                f"Total Units: {tot}<br>"
                f"Available: {avail}<br>"
                f"Allocated: {alloc}"
            )

    # Plot Resource Nodes (Squares)
    fig.add_trace(go.Scatter(
        x=r_x, y=r_y,
        mode="markers+text",
        marker=dict(symbol="square", size=38, color=r_colors, line=dict(color="#FFFFFF", width=2)),
        text=[f"<b>{r}</b>" for r in state.resource_ids],
        textposition="middle center",
        textfont=dict(color="#FFFFFF", size=13, family="monospace"),
        hoverinfo="text",
        hovertext=r_text,
        name="Resources",
    ))

    # Plot Process Nodes (Circles)
    fig.add_trace(go.Scatter(
        x=p_x, y=p_y,
        mode="markers+text",
        marker=dict(symbol="circle", size=36, color=p_colors, line=dict(color="#FFFFFF", width=2)),
        text=[f"<b>{p}</b>" for p in state.process_ids],
        textposition="middle center",
        textfont=dict(color="#FFFFFF", size=13, family="monospace"),
        hoverinfo="text",
        hovertext=p_text,
        name="Processes",
    ))

    # Add Layout Formatting
    fig.update_layout(
        title=dict(
            text="<b>Resource Allocation Graph (RAG)</b>",
            font=dict(size=18, color="#F8FAFC"),
            x=0.05,
        ),
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False, range=[0.0, 1.0],
            title=dict(text="Processes (Left: x=0.2) ⟵ Allocation / Request ⟶ Resources (Right: x=0.8)", font=dict(color="#94A3B8", size=12)),
        ),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.05, 1.05]),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(color="#E2E8F0", size=11),
        ),
        margin=dict(l=20, r=20, t=60, b=30),
        height=480,
    )

    # Generate Academic Explanation
    cycle_count = len(cycles)
    has_cycle = cycle_count > 0

    explanation_lines = [
        f"**Graph Analysis:** {G.number_of_nodes()} nodes ({state.num_processes} processes, {state.num_resources} resources), {G.number_of_edges()} active edges."
    ]

    if is_single:
        explanation_lines.append(
            "- **Resource Category:** Single-Instance System (all resources have exactly 1 unit)."
        )
        if has_cycle:
            explanation_lines.append(
                f"- **Cycle Status:** 🚨 **{cycle_count} cycle(s) detected** ({cycles}). "
                "In single-instance systems, a directed cycle is a **necessary and sufficient** condition for deadlock. "
                "The system is definitively deadlocked!"
            )
        else:
            explanation_lines.append(
                "- **Cycle Status:** ✅ **No cycles detected**. "
                "In single-instance systems, absence of a cycle guarantees that the system is **deadlock-free**."
            )
    else:
        explanation_lines.append(
            "- **Resource Category:** Multiple-Instance System (at least one resource has >1 instance)."
        )
        if has_cycle:
            explanation_lines.append(
                f"- **Cycle Status:** ⚠️ **{cycle_count} cycle(s) detected** ({cycles}). "
                "**Crucial OS Concept:** For multiple-instance resources, a directed cycle is **necessary but NOT sufficient** for deadlock. "
                "Other unblocked processes holding instances of the cycled resources may complete and free them. "
                "Check the Multi-Instance Detection algorithm for the conclusive verdict!"
            )
        else:
            explanation_lines.append(
                "- **Cycle Status:** ✅ **No cycles detected**. The system is deadlock-free."
            )

    return fig, "\n".join(explanation_lines)
