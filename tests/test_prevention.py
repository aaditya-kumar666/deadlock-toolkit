"""
Unit tests for Prevention Engine: Havender's Resource Ordering and Hold-and-Wait Protocols.
"""

import pytest
from core.prevention import (
    verify_resource_ordering,
    verify_hold_and_wait_protocol_a,
    verify_hold_and_wait_protocol_b,
    get_default_resource_ordering,
)


def test_resource_ordering_valid():
    ordering = {"R0": 1, "R1": 2, "R2": 3}
    # Process holds R0 (order 1), requests R1 (order 2) -> Allowed!
    valid, msg = verify_resource_ordering(["R0"], "R1", ordering)
    assert valid is True
    assert "COMPLIANT" in msg


def test_resource_ordering_violation():
    ordering = {"R0": 1, "R1": 2, "R2": 3}
    # Process holds R1 (order 2), requests R0 (order 1) -> VIOLATION!
    valid, msg = verify_resource_ordering(["R1"], "R0", ordering)
    assert valid is False
    assert "RESOURCE ORDERING VIOLATION" in msg


def test_resource_ordering_multiple_held():
    ordering = {"R0": 1, "R1": 2, "R2": 3}
    # Process holds R0 and R2. Requests R1 (order 2). Since order 2 < order 3 (R2), VIOLATION!
    valid, msg = verify_resource_ordering(["R0", "R2"], "R1", ordering)
    assert valid is False
    assert "VIOLATION" in msg


def test_hold_and_wait_protocol_a():
    # Protocol A: Initial batch before execution
    valid, msg = verify_hold_and_wait_protocol_a(currently_allocated_count=0, is_initial_batch_request=True)
    assert valid is True

    # Incremental request while holding resources: REJECTED
    valid, msg = verify_hold_and_wait_protocol_a(currently_allocated_count=2, is_initial_batch_request=False)
    assert valid is False
    assert "VIOLATION" in msg


def test_hold_and_wait_protocol_b():
    # Protocol B: Can only request when holding ZERO resources
    valid, msg = verify_hold_and_wait_protocol_b(total_currently_allocated=0, requested_amount=2)
    assert valid is True

    # Requesting while holding resources: REJECTED
    valid, msg = verify_hold_and_wait_protocol_b(total_currently_allocated=1, requested_amount=1)
    assert valid is False
    assert "VIOLATION" in msg
