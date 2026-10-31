"""
Module 1: Deadlock Detection Engine.
Implements multi-instance deadlock detection (Silberschatz algorithm) and 
single-instance Resource Allocation Graph (RAG) cycle analysis.
"""

from typing import List, Tuple, Set, Dict, Any
import copy
from core.models import SystemState, DetectionResult, StepTrace


def detect_deadlock_multiple_instances(state: SystemState) -> DetectionResult:
    """
    Executes the standard multi-instance Deadlock Detection Algorithm.
    
    Distinction from Banker's Avoidance:
    - Banker's evaluates Maximum potential demand (Need = Maximum - Allocation).
    - Detection evaluates actual outstanding current requests (Request matrix Q).
    - An unsafe state is NOT necessarily a deadlock!
    
    Algorithm:
    1. Work = copy of Available.
    2. For each process i:
       if Allocation[i] != 0 and not terminated:
           Finish[i] = False
       else:
           Finish[i] = True  (Processes holding 0 resources cannot block others)
    3. Find an i such that Finish[i] == False and Request[i] <= Work:
       If found:
           Work = Work + Allocation[i]
           Finish[i] = True
           Repeat step 3.
    4. If Finish[i] == False for any i, process i is deadlocked.
    """
    n = state.num_processes
    m = state.num_resources

    work = list(state.available)
    finish: Dict[str, bool] = {}

    # Initialize Finish vector
    for i, pid in enumerate(state.process_ids):
        if state.terminated.get(pid, False):
            finish[pid] = True
        else:
            has_allocation = any(state.allocation[i][j] > 0 for j in range(m))
            finish[pid] = not has_allocation  # True if holds 0 resources, False otherwise

    traces: List[StepTrace] = []
    step_num = 1
    cleared_processes: List[str] = [pid for pid in state.process_ids if finish[pid] and not state.terminated.get(pid, False)]

    if cleared_processes:
        traces.append(StepTrace(
            step_number=step_num,
            process_id=", ".join(cleared_processes),
            work_vector=list(work),
            requirement_vector=[0] * m,
            can_finish=True,
            allocated_resources=[0] * m,
            new_work_vector=list(work),
            explanation=f"Processes holding 0 resources {cleared_processes} marked finished initially (cannot cause deadlock).",
        ))
        step_num += 1

    while True:
        candidate_found = False

        for i, pid in enumerate(state.process_ids):
            if not finish[pid]:
                p_req = state.request[i]
                p_alloc = state.allocation[i]

                # Check if Request[i] <= Work
                can_proceed = all(p_req[j] <= work[j] for j in range(m))

                if can_proceed:
                    new_work = [work[j] + p_alloc[j] for j in range(m)]
                    traces.append(StepTrace(
                        step_number=step_num,
                        process_id=pid,
                        work_vector=list(work),
                        requirement_vector=list(p_req),
                        can_finish=True,
                        allocated_resources=list(p_alloc),
                        new_work_vector=list(new_work),
                        explanation=(
                            f"Process {pid} requests {p_req} <= Work {work}. "
                            f"It finishes and releases allocation {p_alloc}, updating Work to {new_work}."
                        ),
                    ))
                    step_num += 1
                    work = new_work
                    finish[pid] = True
                    candidate_found = True
                    break

        if not candidate_found:
            break

    deadlocked_pids = [
        pid for pid in state.process_ids 
        if not finish[pid] and not state.terminated.get(pid, False)
    ]
    is_deadlocked = len(deadlocked_pids) > 0

    if is_deadlocked:
        for pid in deadlocked_pids:
            idx = state.process_ids.index(pid)
            traces.append(StepTrace(
                step_number=step_num,
                process_id=pid,
                work_vector=list(work),
                requirement_vector=list(state.request[idx]),
                can_finish=False,
                allocated_resources=list(state.allocation[idx]),
                new_work_vector=list(work),
                explanation=f"DEADLOCK: Process {pid} request {state.request[idx]} cannot be satisfied with available Work {work}.",
            ))
            step_num += 1
        msg = f"DEADLOCK DETECTED! {len(deadlocked_pids)} process(es) deadlocked: {deadlocked_pids}."
    else:
        msg = "NO DEADLOCK: All processes can either finish or currently hold no blocking resources."

    # Extract cycles from RAG for completeness
    cycles = find_rag_cycles(state)

    return DetectionResult(
        is_deadlocked=is_deadlocked,
        deadlocked_processes=deadlocked_pids,
        trace=traces,
        cycles=cycles,
        message=msg,
    )


def find_rag_cycles(state: SystemState) -> List[List[str]]:
    """
    Constructs a directed Resource Allocation Graph and detects all simple cycles.
    
    Edges:
    - Allocation: Resource R_j -> Process P_i (Resource is assigned to Process)
    - Request: Process P_i -> Resource R_j (Process is waiting for Resource)
    
    Returns:
        List of cycle node paths.
    """
    import networkx as nx

    graph = nx.DiGraph()

    for pid in state.process_ids:
        if not state.terminated.get(pid, False):
            graph.add_node(pid, node_type="process")

    for rid in state.resource_ids:
        graph.add_node(rid, node_type="resource")

    for i, pid in enumerate(state.process_ids):
        if state.terminated.get(pid, False):
            continue
        for j, rid in enumerate(state.resource_ids):
            # Assignment edge: R_j -> P_i
            if state.allocation[i][j] > 0:
                graph.add_edge(rid, pid, weight=state.allocation[i][j])
            # Request edge: P_i -> R_j
            if state.request[i][j] > 0:
                graph.add_edge(pid, rid, weight=state.request[i][j])

    try:
        cycles = list(nx.simple_cycles(graph))
    except Exception:
        cycles = []

    return cycles


def is_single_instance_system(state: SystemState) -> bool:
    """Checks whether every resource in the system has strictly 1 total instance."""
    return all(count == 1 for count in state.total)
