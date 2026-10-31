"""
Visualization module: Analytical and performance charts.
Provides resource utilization breakdowns, recovery audit visualizations,
and simulator runtime benchmark plots.
"""

from typing import List, Dict, Any, Tuple
import time
import random
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from core.models import SystemState, RecoveryAction
from core.bankers import is_safe_state
from core.detection import detect_deadlock_multiple_instances


def create_resource_utilization_chart(state: SystemState) -> go.Figure:
    """
    Renders a stacked bar chart displaying Allocated vs Available instances for each resource type.
    """
    n = state.num_processes
    alloc_sums = [sum(state.allocation[i][j] for i in range(n)) for j in range(state.num_resources)]

    fig = go.Figure()

    # Allocated Bar
    fig.add_trace(go.Bar(
        x=state.resource_ids,
        y=alloc_sums,
        name="Allocated Units",
        marker_color="#3B82F6",
        text=alloc_sums,
        textposition="auto",
    ))

    # Available Bar
    fig.add_trace(go.Bar(
        x=state.resource_ids,
        y=state.available,
        name="Available Units",
        marker_color="#10B981",
        text=state.available,
        textposition="auto",
    ))

    fig.update_layout(
        barmode="stack",
        title=dict(
            text="<b>Resource Utilization Breakdown (Allocated vs Available)</b>",
            font=dict(size=16, color="#F8FAFC"),
            x=0.05,
        ),
        xaxis=dict(title="Resource Type", color="#94A3B8"),
        yaxis=dict(title="Total Instances", color="#94A3B8"),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(color="#E2E8F0"),
        ),
        margin=dict(l=20, r=20, t=50, b=30),
        height=320,
    )

    return fig


def create_recovery_audit_chart(actions: List[RecoveryAction]) -> go.Figure:
    """
    Renders an audit bar chart of recovery actions: cost and reclaimed resources per victim.
    """
    if not actions:
        fig = go.Figure()
        fig.update_layout(
            title="No recovery actions recorded.",
            plot_bgcolor="#0F172A",
            paper_bgcolor="#0F172A",
            font=dict(color="#94A3B8"),
        )
        return fig

    victims = [f"Step {a.step}: {a.victim_process_id}" for a in actions]
    costs = [a.cost for a in actions]
    reclaimed_totals = [sum(a.reclaimed_resources) for a in actions]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=victims,
        y=costs,
        name="Termination Cost",
        marker_color="#EF4444",
        text=costs,
        textposition="auto",
    ))

    fig.add_trace(go.Bar(
        x=victims,
        y=reclaimed_totals,
        name="Total Units Reclaimed",
        marker_color="#10B981",
        text=reclaimed_totals,
        textposition="auto",
    ))

    fig.update_layout(
        barmode="group",
        title=dict(
            text="<b>Recovery Actions: Termination Cost vs Reclaimed Units</b>",
            font=dict(size=16, color="#F8FAFC"),
            x=0.05,
        ),
        xaxis=dict(title="Victim Selection Step", color="#94A3B8"),
        yaxis=dict(title="Units / Cost", color="#94A3B8"),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(color="#E2E8F0"),
        ),
        margin=dict(l=20, r=20, t=50, b=30),
        height=320,
    )

    return fig


def run_benchmark_trials() -> Tuple[pd.DataFrame, go.Figure]:
    """
    Executes algorithmic runtime benchmarking of Banker's Algorithm and Multi-Instance Detection
    over scaling process counts (n = 5, 10, 25, 50, 75, 100) and resource types (m = 3, 5).
    
    ACADEMIC NOTICE:
    These timings measure in-memory Python algorithmic execution, NOT operating system kernel dispatching.
    """
    process_counts = [5, 10, 25, 50, 75, 100]
    results = []

    for n in process_counts:
        m = 4
        # Generate synthetic consistent state
        total = [n * 3] * m
        allocation = [[random.randint(0, 2) for _ in range(m)] for _ in range(n)]
        alloc_sums = [sum(allocation[i][j] for i in range(n)) for j in range(m)]
        available = [max(total[j] - alloc_sums[j], 1) for j in range(m)]
        # Re-sync total to ensure conservation law holds
        total = [available[j] + alloc_sums[j] for j in range(m)]
        maximum = [[allocation[i][j] + random.randint(0, 3) for j in range(m)] for i in range(n)]
        request = [[random.randint(0, 1) for _ in range(m)] for _ in range(n)]

        state = SystemState(
            process_ids=[f"P{i}" for i in range(n)],
            resource_ids=[f"R{j}" for j in range(m)],
            total=total,
            available=available,
            allocation=allocation,
            maximum=maximum,
            request=request,
        )

        # Benchmark Banker's Algorithm
        t0 = time.perf_counter()
        for _ in range(5):
            is_safe_state(state, find_all=False)
        t_bankers = ((time.perf_counter() - t0) / 5) * 1000.0  # ms

        # Benchmark Detection Algorithm
        t1 = time.perf_counter()
        for _ in range(5):
            detect_deadlock_multiple_instances(state)
        t_detection = ((time.perf_counter() - t1) / 5) * 1000.0  # ms

        results.append({
            "Processes (n)": n,
            "Resource Types (m)": m,
            "Banker's Algorithm (ms)": round(t_bankers, 4),
            "Deadlock Detection (ms)": round(t_detection, 4),
        })

    df = pd.DataFrame(results)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Processes (n)"],
        y=df["Banker's Algorithm (ms)"],
        mode="lines+markers",
        name="Banker's Avoidance O(m * n²)",
        line=dict(color="#3B82F6", width=3),
        marker=dict(size=8),
    ))

    fig.add_trace(go.Scatter(
        x=df["Processes (n)"],
        y=df["Deadlock Detection (ms)"],
        mode="lines+markers",
        name="Deadlock Detection O(m * n²)",
        line=dict(color="#EF4444", width=3),
        marker=dict(size=8),
    ))

    fig.update_layout(
        title=dict(
            text="<b>Simulator Benchmark: Algorithmic Execution Time vs Process Count</b>",
            font=dict(size=16, color="#F8FAFC"),
            x=0.05,
        ),
        xaxis=dict(title="Number of Processes (n)", color="#94A3B8"),
        yaxis=dict(title="Execution Time (milliseconds)", color="#94A3B8"),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(color="#E2E8F0"),
        ),
        margin=dict(l=20, r=20, t=50, b=30),
        height=360,
    )

    return df, fig
