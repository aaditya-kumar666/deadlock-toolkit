"""
Unit tests for all 5 predefined academic scenario presets.
Verifies structural validity, consistency laws, and expected OS algorithm behaviors.
"""

import pytest
from core.scenarios import (
    get_preset_safe_system,
    get_preset_unsafe_not_deadlocked,
    get_preset_single_instance_deadlock,
    get_preset_multi_instance_cycle_no_deadlock,
    get_preset_recoverable_deadlock,
    PRESETS,
)
from core.validation import validate_system_state
from core.bankers import is_safe_state
from core.detection import detect_deadlock_multiple_instances, find_rag_cycles
from core.recovery import run_full_recovery_loop, RecoveryPolicy


def test_preset_1_safe_system():
    state = get_preset_safe_system()
    is_valid, errors = validate_system_state(state)
    assert is_valid is True
    assert len(errors) == 0

    # Banker's algorithm check
    safety = is_safe_state(state)
    assert safety.is_safe is True
    assert len(safety.safe_sequence) == 5

    # Deadlock detection check
    det = detect_deadlock_multiple_instances(state)
    assert det.is_deadlocked is False


def test_preset_2_unsafe_not_deadlocked():
    """
    Crucial academic test:
    Banker's reports UNSAFE, but Deadlock Detection reports NO DEADLOCK!
    """
    state = get_preset_unsafe_not_deadlocked()
    is_valid, errors = validate_system_state(state)
    assert is_valid is True

    # Banker's safety check
    safety = is_safe_state(state)
    assert safety.is_safe is False  # Cannot guarantee safe completion under max claim!

    # Detection algorithm check
    det = detect_deadlock_multiple_instances(state)
    assert det.is_deadlocked is False  # But no current deadlock exists!


def test_preset_3_single_instance_deadlock():
    state = get_preset_single_instance_deadlock()
    is_valid, errors = validate_system_state(state)
    assert is_valid is True

    # Cycle check
    cycles = find_rag_cycles(state)
    assert len(cycles) > 0

    # Deadlock detection
    det = detect_deadlock_multiple_instances(state)
    assert det.is_deadlocked is True
    assert set(det.deadlocked_processes) == {"P0", "P1"}


def test_preset_4_multi_instance_cycle_no_deadlock():
    """
    Shows that a cycle in a multi-instance RAG does not imply deadlock.
    """
    state = get_preset_multi_instance_cycle_no_deadlock()
    is_valid, errors = validate_system_state(state)
    assert is_valid is True

    # Cycle exists
    cycles = find_rag_cycles(state)
    assert len(cycles) > 0

    # But detection passes (no deadlock)
    det = detect_deadlock_multiple_instances(state)
    assert det.is_deadlocked is False


def test_preset_5_recoverable_deadlock():
    state = get_preset_recoverable_deadlock()
    is_valid, errors = validate_system_state(state)
    assert is_valid is True

    # Deadlock confirmed
    det = detect_deadlock_multiple_instances(state)
    assert det.is_deadlocked is True

    # Recovery can resolve it
    recovered_state, actions, is_free = run_full_recovery_loop(state, RecoveryPolicy.LOWEST_COST)
    assert is_free is True
    assert len(actions) > 0

    # Verify no deadlocks remain
    det_after = detect_deadlock_multiple_instances(recovered_state)
    assert det_after.is_deadlocked is False
