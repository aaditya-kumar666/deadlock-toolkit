"""
Unit tests for Recovery Engine: victim selection, resource reclamation, and iterative resolution.
"""

import pytest
from core.models import SystemState, RecoveryPolicy
from core.recovery import select_recovery_victim, execute_recovery_step, run_full_recovery_loop
from core.detection import detect_deadlock_multiple_instances


def create_deadlocked_system() -> SystemState:
    """Creates a 3-process deadlocked state with distinct priorities and costs."""
    return SystemState(
        process_ids=["P0", "P1", "P2"],
        resource_ids=["R0", "R1", "R2"],
        total=[1, 1, 1],
        available=[0, 0, 0],
        allocation=[
            [1, 0, 0],  # P0 holds R0
            [0, 1, 0],  # P1 holds R1
            [0, 0, 1],  # P2 holds R2
        ],
        maximum=[[1, 1, 1], [1, 1, 1], [1, 1, 1]],
        request=[
            [0, 1, 0],  # P0 requests R1
            [0, 0, 1],  # P1 requests R2
            [1, 0, 0],  # P2 requests R0
        ],
        priorities={"P0": 3, "P1": 1, "P2": 2},  # P1 has lowest priority
        costs={"P0": 100.0, "P1": 50.0, "P2": 10.0},  # P2 has lowest cost
    )


def test_select_victim_lowest_priority():
    state = create_deadlocked_system()
    victim, rationale = select_recovery_victim(
        state, ["P0", "P1", "P2"], RecoveryPolicy.LOWEST_PRIORITY
    )
    assert victim == "P1"  # Priority 1 is lowest
    assert "lowest priority" in rationale


def test_select_victim_lowest_cost():
    state = create_deadlocked_system()
    victim, rationale = select_recovery_victim(
        state, ["P0", "P1", "P2"], RecoveryPolicy.LOWEST_COST
    )
    assert victim == "P2"  # Cost 10.0 is lowest
    assert "lowest termination cost" in rationale


def test_select_victim_manual():
    state = create_deadlocked_system()
    victim, rationale = select_recovery_victim(
        state, ["P0", "P1", "P2"], RecoveryPolicy.MANUAL, manual_choice="P0"
    )
    assert victim == "P0"


def test_execute_single_recovery_step_breaks_deadlock():
    state = create_deadlocked_system()
    # Initial detection confirms deadlock
    det = detect_deadlock_multiple_instances(state)
    assert det.is_deadlocked is True

    # Terminate P1 (lowest priority)
    new_state, action = execute_recovery_step(state, RecoveryPolicy.LOWEST_PRIORITY)
    assert action is not None
    assert action.victim_process_id == "P1"
    assert new_state.terminated["P1"] is True
    # P1 held [0, 1, 0], so R1 available must increase by 1
    assert new_state.available == [0, 1, 0]
    # Check if deadlock was resolved
    assert action.is_deadlocked_after is False


def test_recovery_requiring_multiple_victims():
    """
    Scenario with 4 processes where terminating one leaves another deadlock cycle,
    requiring multiple victim steps to completely resolve.
    """
    # Cycle 1: P0 <-> P1 on R0, R1
    # Cycle 2: P2 <-> P3 on R2, R3
    state = SystemState(
        process_ids=["P0", "P1", "P2", "P3"],
        resource_ids=["R0", "R1", "R2", "R3"],
        total=[1, 1, 1, 1],
        available=[0, 0, 0, 0],
        allocation=[
            [1, 0, 0, 0],  # P0 holds R0
            [0, 1, 0, 0],  # P1 holds R1
            [0, 0, 1, 0],  # P2 holds R2
            [0, 0, 0, 1],  # P3 holds R3
        ],
        maximum=[[1, 1, 1, 1] for _ in range(4)],
        request=[
            [0, 1, 0, 0],  # P0 requests R1
            [1, 0, 0, 0],  # P1 requests R0
            [0, 0, 0, 1],  # P2 requests R3
            [0, 0, 1, 0],  # P3 requests R2
        ],
        priorities={"P0": 1, "P1": 2, "P2": 1, "P3": 2},
        costs={"P0": 10.0, "P1": 20.0, "P2": 10.0, "P3": 20.0},
    )

    det_init = detect_deadlock_multiple_instances(state)
    assert det_init.is_deadlocked is True
    assert len(det_init.deadlocked_processes) == 4

    # Run full recovery loop
    final_state, actions, is_free = run_full_recovery_loop(state, RecoveryPolicy.LOWEST_COST)
    assert is_free is True
    # Must have terminated at least 2 victims to break both cycles!
    assert len(actions) == 2
    terminated_pids = [a.victim_process_id for a in actions]
    assert len(set(terminated_pids)) == 2
    # Check that final detection has 0 deadlocked processes
    det_final = detect_deadlock_multiple_instances(final_state)
    assert det_final.is_deadlocked is False
