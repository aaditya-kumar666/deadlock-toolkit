"""
Unit tests for data validation and consistency checks.
"""

import pytest
from core.models import SystemState
from core.validation import validate_system_state, validate_resource_request


def create_sample_state():
    """Returns a valid 3-process, 3-resource system state."""
    return SystemState(
        process_ids=["P0", "P1", "P2"],
        resource_ids=["A", "B", "C"],
        total=[10, 5, 7],
        available=[3, 3, 2],
        allocation=[
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
        ],  # sum of allocations = [5, 1, 2]. Total = Available (3,3,2) + sum (5,1,2) = (8, 4, 4)?
        # Wait: 3+5=8 != 10, 3+1=4 != 5, 2+2=4 != 7.
        # Let's adjust total so it's consistent: Total = [8, 4, 4]
        maximum=[
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
        ],
        request=[
            [0, 0, 0],
            [1, 0, 2],
            [0, 0, 0],
        ]
    )


def test_consistent_state_validation():
    state = SystemState(
        process_ids=["P0", "P1", "P2"],
        resource_ids=["A", "B", "C"],
        total=[8, 4, 4],
        available=[3, 3, 2],
        allocation=[
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
        ],
        maximum=[
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
        ],
        request=[
            [0, 0, 0],
            [1, 0, 2],
            [0, 0, 0],
        ]
    )
    is_valid, errors = validate_system_state(state)
    assert is_valid is True
    assert len(errors) == 0


def test_need_matrix_calculation():
    state = SystemState(
        process_ids=["P0", "P1"],
        resource_ids=["R0", "R1"],
        total=[5, 5],
        available=[2, 2],
        allocation=[
            [1, 2],
            [2, 1],
        ],
        maximum=[
            [3, 4],
            [5, 2],
        ],
        request=[[0, 0], [0, 0]]
    )
    need = state.get_need_matrix()
    assert need == [
        [2, 2],  # [3-1, 4-2]
        [3, 1],  # [5-2, 2-1]
    ]


def test_negative_count_rejected():
    state = SystemState(
        process_ids=["P0"],
        resource_ids=["R0"],
        total=[-5],
        available=[0],
        allocation=[[0]],
        maximum=[[0]],
        request=[[0]]
    )
    is_valid, errors = validate_system_state(state)
    assert is_valid is False
    assert any("non-negative" in err for err in errors)


def test_dimension_mismatch_rejected():
    state = SystemState(
        process_ids=["P0", "P1"],
        resource_ids=["R0", "R1"],
        total=[10, 10],
        available=[10],  # Length 1 instead of 2
        allocation=[[0, 0], [0, 0]],
        maximum=[[0, 0], [0, 0]],
        request=[[0, 0], [0, 0]]
    )
    is_valid, errors = validate_system_state(state)
    assert is_valid is False
    assert any("dimension mismatch" in err for err in errors)


def test_allocation_exceeding_maximum_rejected():
    state = SystemState(
        process_ids=["P0"],
        resource_ids=["R0"],
        total=[10],
        available=[5],
        allocation=[[5]],
        maximum=[[3]],  # Allocated 5 > Max 3!
        request=[[0]]
    )
    is_valid, errors = validate_system_state(state)
    assert is_valid is False
    assert any("exceeds its declared maximum claim" in err for err in errors)


def test_inconsistent_total_rejected():
    state = SystemState(
        process_ids=["P0"],
        resource_ids=["R0"],
        total=[10],  # Total declared as 10
        available=[2],
        allocation=[[3]],  # 2 + 3 = 5 != 10
        maximum=[[5]],
        request=[[0]]
    )
    is_valid, errors = validate_system_state(state)
    assert is_valid is False
    assert any("conservation violation" in err for err in errors)


def test_empty_process_or_resource_rejected():
    state = SystemState(
        process_ids=[],
        resource_ids=["R0"],
        total=[1],
        available=[1],
        allocation=[],
        maximum=[],
        request=[]
    )
    is_valid, errors = validate_system_state(state)
    assert is_valid is False
    assert any("cannot be empty" in err for err in errors)


def test_processes_holding_no_resources():
    state = SystemState(
        process_ids=["P0", "P1"],
        resource_ids=["R0", "R1"],
        total=[4, 4],
        available=[4, 4],
        allocation=[
            [0, 0],
            [0, 0],
        ],
        maximum=[
            [2, 2],
            [1, 1],
        ],
        request=[[0, 0], [0, 0]]
    )
    is_valid, errors = validate_system_state(state)
    assert is_valid is True
    assert len(errors) == 0


def test_resource_request_validation():
    state = SystemState(
        process_ids=["P0", "P1"],
        resource_ids=["R0", "R1"],
        total=[10, 10],
        available=[2, 2],
        allocation=[
            [3, 3],
            [5, 5],
        ],
        maximum=[
            [5, 6],  # P0 Need = [2, 3]
            [6, 6],  # P1 Need = [1, 1]
        ],
        request=[[0, 0], [0, 0]]
    )
    # Valid and immediately grantable request: [1, 1] <= Need [2, 3] and <= Avail [2, 2]
    valid, can_grant, msgs = validate_resource_request(state, "P0", [1, 1])
    assert valid is True
    assert can_grant is True

    # Exceeding need: P0 requests [3, 1] when Need is [2, 3]
    valid, can_grant, msgs = validate_resource_request(state, "P0", [3, 1])
    assert valid is False
    assert can_grant is False
    assert any("exceeds its remaining need" in m for m in msgs)

    # Exceeding available: P0 requests [2, 3] <= Need [2, 3], but Avail is [2, 2] so R1 exceeds
    valid, can_grant, msgs = validate_resource_request(state, "P0", [2, 3])
    assert valid is True
    assert can_grant is False
    assert any("must wait" in m for m in msgs)
