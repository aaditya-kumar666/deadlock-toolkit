"""
Validation engine for Deadlock Prevention and Recovery Toolkit.
Guarantees mathematical and structural consistency without silent repairs or crashes.
"""

from typing import List, Tuple, Dict, Any
from core.models import SystemState


class ValidationError(Exception):
    """Custom exception raised when scenario constraints are violated."""
    pass


def validate_system_state(state: SystemState) -> Tuple[bool, List[str]]:
    """
    Validates the structural and mathematical consistency of a SystemState.
    
    Checks performed:
    1. Non-empty and unique process and resource identifiers.
    2. Dimensional consistency across all matrices and vectors.
    3. Non-negative counts for all instances.
    4. Allocation constraint: Allocation[i][j] <= Maximum[i][j].
    5. Conservation law: Total[j] == Available[j] + sum_i(Allocation[i][j]).
    6. Valid priority and termination cost values.
    
    Returns:
        (is_valid, list_of_error_messages)
    """
    errors: List[str] = []

    # 1. Identifier checks
    if not state.process_ids:
        errors.append("Process list cannot be empty.")
    if len(state.process_ids) != len(set(state.process_ids)):
        errors.append("Process IDs must be unique.")

    if not state.resource_ids:
        errors.append("Resource list cannot be empty.")
    if len(state.resource_ids) != len(set(state.resource_ids)):
        errors.append("Resource IDs must be unique.")

    n = len(state.process_ids)
    m = len(state.resource_ids)

    # 2. Vector dimension and non-negativity checks
    if len(state.total) != m:
        errors.append(f"Total vector dimension mismatch: expected {m}, got {len(state.total)}.")
    else:
        for j, val in enumerate(state.total):
            if not isinstance(val, int) or val < 0:
                errors.append(f"Total resource count for {state.resource_ids[j]} must be a non-negative integer (got {val}).")

    if len(state.available) != m:
        errors.append(f"Available vector dimension mismatch: expected {m}, got {len(state.available)}.")
    else:
        for j, val in enumerate(state.available):
            if not isinstance(val, int) or val < 0:
                errors.append(f"Available count for {state.resource_ids[j]} must be a non-negative integer (got {val}).")

    # 3. Allocation matrix dimension and content checks
    if len(state.allocation) != n:
        errors.append(f"Allocation matrix row count mismatch: expected {n} processes, got {len(state.allocation)}.")
    else:
        for i, row in enumerate(state.allocation):
            pid = state.process_ids[i] if i < n else f"P{i}"
            if len(row) != m:
                errors.append(f"Allocation row for process {pid} has length {len(row)}, expected {m}.")
            else:
                for j, val in enumerate(row):
                    rid = state.resource_ids[j] if j < m else f"R{j}"
                    if not isinstance(val, int) or val < 0:
                        errors.append(f"Allocation[{pid}][{rid}] must be a non-negative integer (got {val}).")

    # 4. Maximum matrix dimension and content checks
    if len(state.maximum) != n:
        errors.append(f"Maximum matrix row count mismatch: expected {n} processes, got {len(state.maximum)}.")
    else:
        for i, row in enumerate(state.maximum):
            pid = state.process_ids[i] if i < n else f"P{i}"
            if len(row) != m:
                errors.append(f"Maximum row for process {pid} has length {len(row)}, expected {m}.")
            else:
                for j, val in enumerate(row):
                    rid = state.resource_ids[j] if j < m else f"R{j}"
                    if not isinstance(val, int) or val < 0:
                        errors.append(f"Maximum[{pid}][{rid}] must be a non-negative integer (got {val}).")

    # 5. Request matrix dimension and content checks
    if len(state.request) != n:
        errors.append(f"Request matrix row count mismatch: expected {n} processes, got {len(state.request)}.")
    else:
        for i, row in enumerate(state.request):
            pid = state.process_ids[i] if i < n else f"P{i}"
            if len(row) != m:
                errors.append(f"Request row for process {pid} has length {len(row)}, expected {m}.")
            else:
                for j, val in enumerate(row):
                    rid = state.resource_ids[j] if j < m else f"R{j}"
                    if not isinstance(val, int) or val < 0:
                        errors.append(f"Request[{pid}][{rid}] must be a non-negative integer (got {val}).")

    # Stop here if basic dimensions are misaligned to prevent IndexError
    if errors:
        return False, errors

    # 6. Allocation <= Maximum demand check
    for i, pid in enumerate(state.process_ids):
        if state.terminated.get(pid, False):
            continue
        for j, rid in enumerate(state.resource_ids):
            alloc_val = state.allocation[i][j]
            max_val = state.maximum[i][j]
            if alloc_val > max_val:
                errors.append(
                    f"Process {pid} allocated {alloc_val} units of {rid}, "
                    f"which exceeds its declared maximum claim of {max_val}."
                )

    # 7. Conservation of resources check: Total[j] == Available[j] + sum_i(Allocation[i][j])
    for j, rid in enumerate(state.resource_ids):
        tot = state.total[j]
        avail = state.available[j]
        sum_alloc = sum(state.allocation[i][j] for i in range(n))
        if tot != avail + sum_alloc:
            errors.append(
                f"Resource conservation violation for {rid}: Total ({tot}) != "
                f"Available ({avail}) + Sum of Allocations ({sum_alloc}). Difference: {tot - (avail + sum_alloc)}."
            )

    # 8. Priorities and costs validation
    for pid in state.process_ids:
        p_val = state.priorities.get(pid)
        if p_val is not None and not isinstance(p_val, int):
            errors.append(f"Priority for {pid} must be an integer, got {p_val}.")
        c_val = state.costs.get(pid)
        if c_val is not None and (not isinstance(c_val, (int, float)) or c_val < 0):
            errors.append(f"Termination cost for {pid} must be a non-negative number, got {c_val}.")

    return (len(errors) == 0), errors


def validate_resource_request(
    state: SystemState, 
    process_id: str, 
    request_vector: List[int]
) -> Tuple[bool, bool, List[str]]:
    """
    Validates a resource request against Banker's Algorithm rules.
    
    Rule 1: Request[j] <= Need[j] (Claim limit). If violated -> Error (exceeded maximum claim).
    Rule 2: Request[j] <= Available[j] (Availability limit). If violated -> Must wait (not an error, but cannot grant).
    
    Returns:
        (is_valid, can_grant_immediately, messages)
    """
    messages: List[str] = []

    if process_id not in state.process_ids:
        return False, False, [f"Process ID '{process_id}' does not exist in the system."]

    if state.terminated.get(process_id, False):
        return False, False, [f"Process '{process_id}' is already terminated and cannot make resource requests."]

    m = state.num_resources
    if len(request_vector) != m:
        return False, False, [f"Request vector length mismatch: expected {m}, got {len(request_vector)}."]

    # Non-negative check
    for j, val in enumerate(request_vector):
        rid = state.resource_ids[j]
        if not isinstance(val, int) or val < 0:
            return False, False, [f"Request amount for {rid} must be a non-negative integer (got {val})."]

    # All-zero request check
    if all(val == 0 for val in request_vector):
        return True, True, ["Request vector is all zeros (trivial grant)."]

    p_idx = state.process_ids.index(process_id)
    need_matrix = state.get_need_matrix()
    p_need = need_matrix[p_idx]

    # Check Rule 1: Request <= Need
    exceeded_need = False
    for j, val in enumerate(request_vector):
        rid = state.resource_ids[j]
        if val > p_need[j]:
            messages.append(
                f"Error: Process {process_id} requested {val} units of {rid}, "
                f"which exceeds its remaining need of {p_need[j]} (Max: {state.maximum[p_idx][j]}, Alloc: {state.allocation[p_idx][j]})."
            )
            exceeded_need = True

    if exceeded_need:
        return False, False, messages

    # Check Rule 2: Request <= Available
    can_grant = True
    wait_messages = []
    for j, val in enumerate(request_vector):
        rid = state.resource_ids[j]
        if val > state.available[j]:
            can_grant = False
            wait_messages.append(
                f"Process {process_id} must wait: requested {val} units of {rid}, "
                f"but only {state.available[j]} units are currently available."
            )

    if not can_grant:
        return True, False, wait_messages

    return True, True, [f"Request of {request_vector} by {process_id} is valid and can be tentatively evaluated."]
