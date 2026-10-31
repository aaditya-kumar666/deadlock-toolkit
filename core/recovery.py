"""
Module 2: Deadlock Recovery Engine.
Simulates non-destructive educational recovery via victim selection, 
safe resource release, and iterative detection cycles.
"""

from typing import List, Dict, Tuple, Optional, Any
import copy
from core.models import SystemState, RecoveryAction, RecoveryPolicy, DetectionResult
from core.detection import detect_deadlock_multiple_instances


def select_recovery_victim(
    state: SystemState, 
    deadlocked_processes: List[str], 
    policy: RecoveryPolicy,
    manual_choice: Optional[str] = None
) -> Tuple[str, str]:
    """
    Selects a victim process to terminate from the deadlocked set based on chosen policy.
    
    Returns:
        (victim_pid, rationale_message)
    """
    if not deadlocked_processes:
        raise ValueError("Cannot select victim: No processes are currently deadlocked.")

    if policy == RecoveryPolicy.MANUAL:
        if manual_choice and manual_choice in deadlocked_processes:
            return manual_choice, f"Manually selected process '{manual_choice}' as termination victim."
        # Fallback to first if invalid choice
        chosen = deadlocked_processes[0]
        return chosen, f"Manual selection defaulted to '{chosen}' (invalid or missing override)."

    if policy == RecoveryPolicy.LOWEST_PRIORITY:
        # In this simulation, lower integer = lower priority / least critical
        # e.g., Priority 1 is lower than Priority 5
        sorted_by_pri = sorted(
            deadlocked_processes,
            key=lambda pid: (state.priorities.get(pid, 1), state.costs.get(pid, 10.0), pid)
        )
        victim = sorted_by_pri[0]
        pri = state.priorities.get(victim, 1)
        return victim, (
            f"Selected '{victim}' with lowest priority ({pri}) among deadlocked processes: "
            f"{[(p, state.priorities.get(p, 1)) for p in deadlocked_processes]}."
        )

    if policy == RecoveryPolicy.LOWEST_COST:
        # Lowest monetary/computational restart cost
        sorted_by_cost = sorted(
            deadlocked_processes,
            key=lambda pid: (state.costs.get(pid, 10.0), state.priorities.get(pid, 1), pid)
        )
        victim = sorted_by_cost[0]
        cost = state.costs.get(victim, 10.0)
        return victim, (
            f"Selected '{victim}' with lowest termination cost ({cost}) among deadlocked processes: "
            f"{[(p, state.costs.get(p, 10.0)) for p in deadlocked_processes]}."
        )

    if policy == RecoveryPolicy.MAX_RESOURCES:
        # Heuristic: Pick process holding the highest total sum of allocated resource units
        # to maximize resources reclaimed back to the available pool.
        def total_allocated(pid: str) -> int:
            idx = state.process_ids.index(pid)
            return sum(state.allocation[idx])

        sorted_by_alloc = sorted(
            deadlocked_processes,
            key=lambda pid: (-total_allocated(pid), state.costs.get(pid, 10.0), pid)
        )
        victim = sorted_by_alloc[0]
        reclaimed = total_allocated(victim)
        return victim, (
            f"Selected '{victim}' maximizing reclaimed resources (holding {reclaimed} total units) "
            f"among deadlocked processes: {[(p, total_allocated(p)) for p in deadlocked_processes]}."
        )

    # Default fallback
    return deadlocked_processes[0], "Default fallback victim selection."


def execute_recovery_step(
    state: SystemState, 
    policy: RecoveryPolicy,
    step_number: int = 1,
    manual_choice: Optional[str] = None
) -> Tuple[SystemState, Optional[RecoveryAction]]:
    """
    Executes a single atomic recovery step:
    1. Runs deadlock detection. If no deadlock, returns immediately.
    2. Selects victim according to policy.
    3. Reclaims victim's allocated resources into Available pool.
    4. Marks victim as TERMINATED in simulation model.
    5. Clears victim's allocations, requests, and maximum claim.
    6. Re-runs detection to evaluate new state.
    
    SAFETY NOTE: This operates strictly within the simulated SystemState data model.
    No actual operating system processes or system calls are executed.
    """
    det_before = detect_deadlock_multiple_instances(state)
    if not det_before.is_deadlocked:
        return state, None

    victim_pid, rationale = select_recovery_victim(
        state, det_before.deadlocked_processes, policy, manual_choice
    )

    new_state = state.clone()
    v_idx = new_state.process_ids.index(victim_pid)
    m = new_state.num_resources

    # Reclaim resources
    reclaimed = list(new_state.allocation[v_idx])
    for j in range(m):
        new_state.available[j] += reclaimed[j]
        new_state.allocation[v_idx][j] = 0
        new_state.request[v_idx][j] = 0
        new_state.maximum[v_idx][j] = 0

    # Mark as terminated
    new_state.terminated[victim_pid] = True

    # Re-evaluate deadlock status
    det_after = detect_deadlock_multiple_instances(new_state)

    action = RecoveryAction(
        step=step_number,
        victim_process_id=victim_pid,
        policy_used=policy.value if isinstance(policy, RecoveryPolicy) else str(policy),
        cost=float(state.costs.get(victim_pid, 10.0)),
        priority=int(state.priorities.get(victim_pid, 1)),
        reclaimed_resources=reclaimed,
        was_deadlocked_before=True,
        is_deadlocked_after=det_after.is_deadlocked,
        remaining_deadlocked=det_after.deadlocked_processes,
        rationale=rationale,
    )

    return new_state, action


def run_full_recovery_loop(
    state: SystemState, 
    policy: RecoveryPolicy,
    max_steps: int = 50
) -> Tuple[SystemState, List[RecoveryAction], bool]:
    """
    Iteratively terminates victim processes until system is completely free of deadlock.
    
    Returns:
        (final_state, list_of_actions, is_deadlock_free)
    """
    current_state = state.clone()
    actions: List[RecoveryAction] = []
    step = 1

    while step <= max_steps:
        det = detect_deadlock_multiple_instances(current_state)
        if not det.is_deadlocked:
            return current_state, actions, True

        current_state, action = execute_recovery_step(current_state, policy, step_number=step)
        if action is None:
            break
        actions.append(action)
        step += 1

    final_det = detect_deadlock_multiple_instances(current_state)
    return current_state, actions, not final_det.is_deadlocked
