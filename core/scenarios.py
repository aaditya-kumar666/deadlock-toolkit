"""
Preset Deadlock Scenarios for Academic Demonstration.
Provides 5 distinct, internally consistent, textbook-grade scenarios illustrating
safe states, unsafe states, circular-wait deadlocks, multi-instance cycle nuances,
and recovery workflows.
"""

from typing import Dict, List, Any
from core.models import SystemState
from core.validation import validate_system_state


def get_preset_safe_system() -> SystemState:
    """
    Preset 1: Classic Textbook Safe System (Silberschatz OS Example).
    5 processes, 3 resource types.
    Sufficient available resources exist to complete all processes in a safe sequence.
    """
    state = SystemState(
        process_ids=["P0", "P1", "P2", "P3", "P4"],
        resource_ids=["A", "B", "C"],
        total=[10, 5, 7],
        available=[3, 3, 2],
        allocation=[
            [0, 1, 0],  # P0
            [2, 0, 0],  # P1
            [3, 0, 2],  # P2
            [2, 1, 1],  # P3
            [0, 0, 2],  # P4
        ],
        maximum=[
            [7, 5, 3],  # P0
            [3, 2, 2],  # P1
            [9, 0, 2],  # P2
            [2, 2, 2],  # P3
            [4, 3, 3],  # P4
        ],
        request=[[0, 0, 0] for _ in range(5)],
        priorities={"P0": 3, "P1": 5, "P2": 2, "P3": 4, "P4": 1},
        costs={"P0": 40.0, "P1": 15.0, "P2": 30.0, "P3": 25.0, "P4": 10.0},
    )
    is_valid, errors = validate_system_state(state)
    if not is_valid:
        raise ValueError(f"Preset 1 validation failed: {errors}")
    return state


def get_preset_unsafe_not_deadlocked() -> SystemState:
    """
    Preset 2: Unsafe System Without Proven Deadlock.
    
    Academic Concept:
    - An UNSAFE state means there is no guaranteed safe sequence if all processes
      demand their full maximum claims simultaneously.
    - However, an unsafe state is NOT yet a DEADLOCK because current outstanding requests
      are small enough to allow some processes to make progress and release resources.
    """
    state = SystemState(
        process_ids=["P0", "P1", "P2"],
        resource_ids=["R0", "R1"],
        total=[5, 5],
        available=[0, 1],
        allocation=[
            [2, 2],  # P0
            [2, 1],  # P1
            [1, 1],  # P2
        ],  # sum alloc = [5, 4], available = [0, 1] => total = [5, 5]
        maximum=[
            [4, 3],  # P0 Need = [2, 1] > [0, 1]
            [4, 3],  # P1 Need = [2, 2] > [0, 1]
            [3, 3],  # P2 Need = [2, 2] > [0, 1]
        ],
        request=[
            [0, 0],  # P0 has no current request (ready to run and release)
            [0, 1],  # P1 requests 1 unit of R1 (which is available!)
            [0, 0],  # P2 has no current request
        ],
        priorities={"P0": 2, "P1": 1, "P2": 3},
        costs={"P0": 20.0, "P1": 15.0, "P2": 30.0},
    )
    is_valid, errors = validate_system_state(state)
    if not is_valid:
        raise ValueError(f"Preset 2 validation failed: {errors}")
    return state


def get_preset_single_instance_deadlock() -> SystemState:
    """
    Preset 3: Two-Process Circular-Wait Deadlock (Single-Instance Resources).
    
    Academic Concept:
    - Single-instance resources (Total = 1 for each type).
    - P0 holds R0 and requests R1.
    - P1 holds R1 and requests R0.
    - Directed cycle: P0 -> R1 -> P1 -> R0 -> P0.
    - In single-instance systems, a cycle is both necessary and sufficient for deadlock.
    """
    state = SystemState(
        process_ids=["P0", "P1"],
        resource_ids=["R0", "R1"],
        total=[1, 1],
        available=[0, 0],
        allocation=[
            [1, 0],  # P0 holds R0
            [0, 1],  # P1 holds R1
        ],
        maximum=[
            [1, 1],
            [1, 1],
        ],
        request=[
            [0, 1],  # P0 requests R1
            [1, 0],  # P1 requests R0
        ],
        priorities={"P0": 2, "P1": 1},
        costs={"P0": 50.0, "P1": 20.0},
    )
    is_valid, errors = validate_system_state(state)
    if not is_valid:
        raise ValueError(f"Preset 3 validation failed: {errors}")
    return state


def get_preset_multi_instance_cycle_no_deadlock() -> SystemState:
    """
    Preset 4: Multiple-Instance Resource Scenario (Cycle in RAG, But NO Deadlock).
    
    Academic Concept (Silberschatz Figure 8.7):
    - P0 holds R0, requests R1.
    - P1 holds R1, requests R0.
    - Cycle exists between P0 and P1!
    - However, R0 and R1 have 2 instances each.
    - P2 holds R0, and P3 holds R1; neither has any outstanding requests.
    - P2 and P3 can finish, releasing their instances, which allows P0 and P1 to finish.
    - Proves: For multiple-instance resources, a cycle does NOT imply a deadlock.
    """
    state = SystemState(
        process_ids=["P0", "P1", "P2", "P3"],
        resource_ids=["R0", "R1"],
        total=[2, 2],
        available=[0, 0],
        allocation=[
            [1, 0],  # P0
            [0, 1],  # P1
            [1, 0],  # P2
            [0, 1],  # P3
        ],
        maximum=[
            [1, 1],
            [1, 1],
            [1, 0],
            [0, 1],
        ],
        request=[
            [0, 1],  # P0 requests R1
            [1, 0],  # P1 requests R0
            [0, 0],  # P2 can finish!
            [0, 0],  # P3 can finish!
        ],
        priorities={"P0": 1, "P1": 2, "P2": 3, "P3": 4},
        costs={"P0": 10.0, "P1": 20.0, "P2": 30.0, "P3": 40.0},
    )
    is_valid, errors = validate_system_state(state)
    if not is_valid:
        raise ValueError(f"Preset 4 validation failed: {errors}")
    return state


def get_preset_recoverable_deadlock() -> SystemState:
    """
    Preset 5: Recoverable Deadlock.
    
    4 processes deadlocked in a knot.
    Demonstrates automatic and manual victim selection (lowest priority, lowest cost,
    or max resources) to reclaim resources and restore system progress.
    """
    state = SystemState(
        process_ids=["P0", "P1", "P2", "P3"],
        resource_ids=["R0", "R1", "R2"],
        total=[2, 2, 2],
        available=[0, 0, 0],
        allocation=[
            [1, 0, 0],  # P0
            [0, 1, 0],  # P1
            [0, 0, 1],  # P2
            [1, 1, 1],  # P3
        ],  # sum alloc = [2, 2, 2], available = [0, 0, 0] => total = [2, 2, 2]
        maximum=[
            [2, 1, 0],
            [0, 2, 1],
            [1, 0, 2],
            [2, 2, 2],
        ],
        request=[
            [0, 1, 0],  # P0 waiting for R1
            [0, 0, 1],  # P1 waiting for R2
            [1, 0, 0],  # P2 waiting for R0
            [1, 0, 1],  # P3 waiting for R0, R2
        ],
        priorities={"P0": 4, "P1": 3, "P2": 2, "P3": 1},  # P3 lowest priority
        costs={"P0": 60.0, "P1": 45.0, "P2": 35.0, "P3": 15.0},  # P3 lowest cost
    )
    is_valid, errors = validate_system_state(state)
    if not is_valid:
        raise ValueError(f"Preset 5 validation failed: {errors}")
    return state


PRESETS: Dict[str, Any] = {
    "1. Safe System (Classic Banker's)": {
        "generator": get_preset_safe_system,
        "description": "5 processes, 3 resource types. Demonstrates safe state, Need calculation, and safe sequence finding.",
    },
    "2. Unsafe System (Not Deadlocked)": {
        "generator": get_preset_unsafe_not_deadlocked,
        "description": "System cannot guarantee completion under maximum claims, but no deadlock currently exists with active requests.",
    },
    "3. Circular-Wait Deadlock (Single-Instance)": {
        "generator": get_preset_single_instance_deadlock,
        "description": "2 processes, 2 single-instance resources forming a circular wait. Proves cycle = deadlock in single-instance RAG.",
    },
    "4. Multi-Instance Cycle (No Deadlock)": {
        "generator": get_preset_multi_instance_cycle_no_deadlock,
        "description": "RAG has a directed cycle, but multi-instance detection proves no deadlock exists because unblocked processes free resources.",
    },
    "5. Recoverable Deadlock": {
        "generator": get_preset_recoverable_deadlock,
        "description": "Active deadlock ready for automated or manual recovery by victim selection and resource reclamation.",
    },
}
