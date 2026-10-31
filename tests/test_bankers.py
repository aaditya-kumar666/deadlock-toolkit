"""
Unit tests for Banker's Algorithm, safe sequences, and request simulation.
"""

import pytest
from core.models import SystemState
from core.bankers import calculate_need_matrix, is_safe_state, simulate_resource_request, find_all_safe_sequences


def create_classic_silberschatz_state() -> SystemState:
    """Standard 5-process, 3-resource safe state from Silberschatz OS textbook."""
    return SystemState(
        process_ids=["P0", "P1", "P2", "P3", "P4"],
        resource_ids=["A", "B", "C"],
        total=[10, 5, 7],
        available=[3, 3, 2],
        allocation=[
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ],
        maximum=[
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ],
        request=[[0, 0, 0] for _ in range(5)]
    )


def test_classic_safe_state():
    state = create_classic_silberschatz_state()
    res = is_safe_state(state)
    assert res.is_safe is True
    assert len(res.unresolved_processes) == 0
    assert len(res.safe_sequence) == 5
    # P1 or P3 can typically finish first
    assert res.safe_sequence[0] in ["P1", "P3"]
    # Check trace count matches processes
    assert len(res.trace) == 5
    for t in res.trace:
        assert t.can_finish is True


def test_all_safe_sequences():
    state = create_classic_silberschatz_state()
    all_seqs = find_all_safe_sequences(state)
    assert len(all_seqs) > 0
    # Every returned sequence must contain all 5 distinct processes
    for seq in all_seqs:
        assert set(seq) == {"P0", "P1", "P2", "P3", "P4"}


def test_unsafe_state_detection():
    # Deplete available so no process can satisfy remaining need
    state = SystemState(
        process_ids=["P0", "P1"],
        resource_ids=["R0", "R1"],
        total=[6, 6],
        available=[0, 0],
        allocation=[
            [3, 2],
            [3, 4],
        ],
        maximum=[
            [5, 5],  # Need: [2, 3] > [0, 0]
            [6, 5],  # Need: [3, 1] > [0, 0]
        ],
        request=[[0, 0], [0, 0]]
    )
    res = is_safe_state(state)
    assert res.is_safe is False
    assert set(res.unresolved_processes) == {"P0", "P1"}
    assert res.safe_sequence == []


def test_safe_resource_request_grant():
    state = create_classic_silberschatz_state()
    # P1 requests [1, 0, 2]
    # In classic textbook, this request is granted and leaves the system in a safe state!
    eval_res = simulate_resource_request(state, "P1", [1, 0, 2])
    assert eval_res.is_valid is True
    assert eval_res.can_grant is True
    assert eval_res.is_safe is True
    assert eval_res.provisional_state is not None
    # Verify provisional state reflects new allocation and available
    assert eval_res.provisional_state.available == [2, 3, 0]
    p1_idx = eval_res.provisional_state.process_ids.index("P1")
    assert eval_res.provisional_state.allocation[p1_idx] == [3, 0, 2]
    # Original state is unchanged (immutability of input)
    assert state.available == [3, 3, 2]


def test_unsafe_resource_request_rollback():
    state = create_classic_silberschatz_state()
    # P4 requests [3, 3, 0] - available is [3, 3, 2]
    # This leaves Available = [0, 0, 2], from which no process can satisfy its Need!
    eval_res = simulate_resource_request(state, "P4", [3, 3, 0])
    assert eval_res.is_valid is True
    assert eval_res.can_grant is True
    assert eval_res.is_safe is False
    # Must rollback provisional state to None to avoid corrupting system
    assert eval_res.provisional_state is None
    assert "UNSAFE" in eval_res.reason
    assert state.available == [3, 3, 2]


def test_request_exceeding_claim_rejected():
    state = create_classic_silberschatz_state()
    # P0 maximum is [7, 5, 3], allocation is [0, 1, 0] => Need is [7, 4, 3]
    # P0 requests 5 units of B, exceeding remaining need of 4!
    eval_res = simulate_resource_request(state, "P0", [0, 5, 0])
    assert eval_res.is_valid is False
    assert eval_res.can_grant is False
    assert "exceeds its remaining need" in eval_res.reason
