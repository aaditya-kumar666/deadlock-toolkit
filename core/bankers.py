"""
Module 1: Deadlock Avoidance Engine — Banker's Algorithm.
Implements Need matrix calculation, safety evaluation, all safe sequences search,
and tentative resource-request validation and rollback simulation.
"""

from typing import List, Tuple, Optional
import copy
from core.models import SystemState, SafetyResult, RequestEvaluation, StepTrace
from core.validation import validate_resource_request


def calculate_need_matrix(maximum: List[List[int]], allocation: List[List[int]]) -> List[List[int]]:
    """
    Calculates the Need matrix: Need[i][j] = Maximum[i][j] - Allocation[i][j].
    """
    n = len(maximum)
    m = len(maximum[0]) if n > 0 else 0
    return [[maximum[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]


def find_all_safe_sequences(state: SystemState, max_count: int = 25) -> List[List[str]]:
    """
    Backtracking search to find all possible safe execution sequences (capped at max_count).
    """
    active_indices = [
        i for i, pid in enumerate(state.process_ids) 
        if not state.terminated.get(pid, False)
    ]
    if not active_indices:
        return []

    need_matrix = state.get_need_matrix()
    m = state.num_resources
    results: List[List[str]] = []

    def backtrack(current_work: List[int], finished: set, current_seq: List[str]):
        if len(results) >= max_count:
            return
        if len(finished) == len(active_indices):
            results.append(list(current_seq))
            return

        for idx in active_indices:
            if idx not in finished:
                pid = state.process_ids[idx]
                p_need = need_matrix[idx]
                # Check if Need[idx] <= current_work
                if all(p_need[j] <= current_work[j] for j in range(m)):
                    new_work = [current_work[j] + state.allocation[idx][j] for j in range(m)]
                    finished.add(idx)
                    current_seq.append(pid)
                    backtrack(new_work, finished, current_seq)
                    current_seq.pop()
                    finished.remove(idx)

    backtrack(list(state.available), set(), [])
    return results


def is_safe_state(state: SystemState, find_all: bool = True) -> SafetyResult:
    """
    Executes Dijkstra's Banker's Safety Algorithm with step-by-step trace generation.
    
    Data structures:
    - Work: vector of length m initialized to Available.
    - Finish: boolean vector of length n initialized to False (True for terminated processes).
    
    Loop:
    Find process i such that Finish[i] == False and Need[i] <= Work.
    If found:
        Work = Work + Allocation[i]
        Finish[i] = True
    Repeat until no such process exists.
    If all Finish[i] == True -> SAFE. Else -> UNSAFE.
    """
    n = state.num_processes
    m = state.num_resources
    need_matrix = state.get_need_matrix()

    work = list(state.available)
    finish = {pid: state.terminated.get(pid, False) for pid in state.process_ids}

    safe_sequence: List[str] = []
    traces: List[StepTrace] = []
    step_num = 1

    while True:
        found_candidate = False

        for i, pid in enumerate(state.process_ids):
            if not finish[pid]:
                p_need = need_matrix[i]
                p_alloc = state.allocation[i]

                # Check if Need[i] <= Work
                can_satisfy = all(p_need[j] <= work[j] for j in range(m))

                if can_satisfy:
                    # Process can finish and release allocated resources
                    new_work = [work[j] + p_alloc[j] for j in range(m)]
                    explanation = (
                        f"Process {pid} can finish because remaining Need {p_need} <= Work {work}. "
                        f"Releases its allocation {p_alloc}, updating Work to {new_work}."
                    )
                    traces.append(StepTrace(
                        step_number=step_num,
                        process_id=pid,
                        work_vector=list(work),
                        requirement_vector=list(p_need),
                        can_finish=True,
                        allocated_resources=list(p_alloc),
                        new_work_vector=list(new_work),
                        explanation=explanation,
                    ))
                    step_num += 1
                    work = new_work
                    finish[pid] = True
                    safe_sequence.append(pid)
                    found_candidate = True
                    break

        if not found_candidate:
            break

    # Check if all active processes finished
    unresolved = [pid for pid in state.process_ids if not finish[pid]]
    is_safe = (len(unresolved) == 0)

    if not is_safe:
        for pid in unresolved:
            idx = state.process_ids.index(pid)
            p_need = need_matrix[idx]
            p_alloc = state.allocation[idx]
            traces.append(StepTrace(
                step_number=step_num,
                process_id=pid,
                work_vector=list(work),
                requirement_vector=list(p_need),
                can_finish=False,
                allocated_resources=list(p_alloc),
                new_work_vector=list(work),
                explanation=f"Process {pid} cannot finish: Need {p_need} exceeds available Work {work}."
            ))
            step_num += 1

    all_seqs = find_all_safe_sequences(state) if (is_safe and find_all) else []

    msg = (
        f"System is in a SAFE state. Safe sequence: <{' -> '.join(safe_sequence)}>."
        if is_safe else
        f"System is in an UNSAFE state. Deadlock could occur under worst-case demand. Unresolved processes: {unresolved}."
    )

    return SafetyResult(
        is_safe=is_safe,
        safe_sequence=safe_sequence,
        all_safe_sequences=all_seqs,
        trace=traces,
        unresolved_processes=unresolved,
        message=msg,
    )


def simulate_resource_request(
    state: SystemState, 
    process_id: str, 
    request_vector: List[int]
) -> RequestEvaluation:
    """
    Simulates a process resource request following Banker's Resource-Request Algorithm:
    
    1. Validation:
       - If Request_i > Need_i: Error (Process exceeded maximum claim).
       - If Request_i > Available: Process must wait (Cannot grant immediately).
    2. Tentative Grant:
       - Available = Available - Request
       - Allocation_i = Allocation_i + Request
       - Need_i = Need_i - Request
    3. Safety Algorithm:
       - Run Banker's Safety Algorithm on tentative state.
       - If Safe: Grant is safe! Return provisional state.
       - If Unsafe: Rollback to original state! Grant is denied to avoid deadlock.
    """
    # 1. Validate request
    is_valid, can_grant, messages = validate_resource_request(state, process_id, request_vector)
    if not is_valid:
        return RequestEvaluation(
            is_valid=False,
            can_grant=False,
            is_safe=False,
            reason="\n".join(messages),
            safe_sequence=[],
            provisional_state=None,
            trace=[],
        )

    if not can_grant:
        return RequestEvaluation(
            is_valid=True,
            can_grant=False,
            is_safe=False,
            reason="\n".join(messages),
            safe_sequence=[],
            provisional_state=None,
            trace=[],
        )

    # 2. Tentatively modify state
    provisional = state.clone()
    p_idx = provisional.process_ids.index(process_id)
    m = provisional.num_resources

    for j in range(m):
        provisional.available[j] -= request_vector[j]
        provisional.allocation[p_idx][j] += request_vector[j]

    # 3. Test safety of tentative state
    safety_result = is_safe_state(provisional)

    if safety_result.is_safe:
        reason = (
            f"SAFE: Request of {request_vector} by {process_id} can be safely granted immediately. "
            f"A safe sequence exists: <{' -> '.join(safety_result.safe_sequence)}>."
        )
        return RequestEvaluation(
            is_valid=True,
            can_grant=True,
            is_safe=True,
            reason=reason,
            safe_sequence=safety_result.safe_sequence,
            provisional_state=provisional,
            trace=safety_result.trace,
        )
    else:
        reason = (
            f"UNSAFE: Tentatively granting {request_vector} to {process_id} leaves the system in an unsafe state. "
            f"To prevent deadlock, the tentative allocation was rolled back. {process_id} must wait."
        )
        return RequestEvaluation(
            is_valid=True,
            can_grant=True,
            is_safe=False,
            reason=reason,
            safe_sequence=[],
            provisional_state=None,  # Rolled back!
            trace=safety_result.trace,
        )
