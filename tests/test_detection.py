"""
Unit tests for Deadlock Detection Engine (Multi-Instance and Single-Instance RAG analysis).
"""

import pytest
from core.models import SystemState
from core.detection import detect_deadlock_multiple_instances, find_rag_cycles, is_single_instance_system


def test_single_instance_circular_wait_deadlock():
    """
    Classic 2-process circular wait with single-instance resources:
    P0 holds R0, requests R1
    P1 holds R1, requests R0
    Available = [0, 0], Total = [1, 1]
    Cycle: P0 -> R1 -> P1 -> R0 -> P0.
    In single-instance systems, cycle == deadlock.
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
        maximum=[[1, 1], [1, 1]],
        request=[
            [0, 1],  # P0 requests R1
            [1, 0],  # P1 requests R0
        ]
    )

    assert is_single_instance_system(state) is True
    res = detect_deadlock_multiple_instances(state)
    assert res.is_deadlocked is True
    assert set(res.deadlocked_processes) == {"P0", "P1"}
    assert len(res.cycles) > 0


def test_multi_instance_cycle_without_deadlock():
    """
    Classic OS textbook case (Silberschatz Figure 8.7):
    A cycle exists in the RAG, but the system is NOT deadlocked because other processes
    holding instances of the resources can finish and release them.
    
    P0 holds R0, requests R1
    P1 holds R1, requests R0 (Cycle between P0 and P1)
    P2 holds R0, requests nothing (will finish and free R0)
    P3 holds R1, requests nothing (will finish and free R1)
    Total = [2, 2], Available = [0, 0]
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
        maximum=[[1, 1], [1, 1], [1, 0], [0, 1]],
        request=[
            [0, 1],  # P0 requests R1
            [1, 0],  # P1 requests R0
            [0, 0],  # P2 needs nothing, ready to release
            [0, 0],  # P3 needs nothing, ready to release
        ]
    )

    assert is_single_instance_system(state) is False
    cycles = find_rag_cycles(state)
    assert len(cycles) > 0  # Cycle DOES exist!

    res = detect_deadlock_multiple_instances(state)
    # But system is NOT deadlocked!
    assert res.is_deadlocked is False
    assert len(res.deadlocked_processes) == 0


def test_multi_instance_deadlock():
    """
    Multiple-instance scenario where deadlock actually occurs:
    P0 holds [0, 1, 0], requests [0, 0, 0] (can finish!)
    P1 holds [2, 0, 0], requests [2, 0, 2] (needs 2 of C, only 0 available)
    P2 holds [3, 0, 3], requests [0, 0, 0] (can finish!)
    P3 holds [2, 1, 1], requests [1, 0, 0]
    P4 holds [0, 0, 2], requests [0, 0, 2]
    """
    state = SystemState(
        process_ids=["P0", "P1", "P2"],
        resource_ids=["A", "B"],
        total=[2, 2],
        available=[0, 0],
        allocation=[
            [1, 0],
            [1, 1],
            [0, 1],
        ],
        maximum=[[2, 2], [2, 2], [2, 2]],
        request=[
            [1, 1],  # P0 needs [1, 1]
            [0, 1],  # P1 needs [0, 1]
            [1, 0],  # P2 needs [1, 0]
        ]
    )
    res = detect_deadlock_multiple_instances(state)
    assert res.is_deadlocked is True
    assert len(res.deadlocked_processes) == 3


def test_process_holding_no_resources_not_deadlocked():
    """
    A process holding 0 resources waiting for a resource is blocked,
    but cannot participate in holding any resource needed by others.
    """
    state = SystemState(
        process_ids=["P0", "P1"],
        resource_ids=["R0"],
        total=[1],
        available=[0],
        allocation=[
            [0],  # P0 holds nothing
            [1],  # P1 holds R0
        ],
        maximum=[[1], [1]],
        request=[
            [1],  # P0 waiting for R0
            [0],  # P1 requests nothing (can finish!)
        ]
    )
    res = detect_deadlock_multiple_instances(state)
    assert res.is_deadlocked is False
    assert len(res.deadlocked_processes) == 0
