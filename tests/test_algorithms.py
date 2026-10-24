"""
Algorithmic regression tests for the 4 ParkSmart DSA topics.
These tests assert the EXPECTED CORRECT BEHAVIOR for all 4 algorithms.

In the challenge version, these 4 tests will fail because of the 4 intentional bugs:
1. First-Fit Allocation Algorithm (Bug 1 - Easy)
2. Sorting Algorithms and Comparator Logic (Bug 2 - Easy)
3. Hash Maps and Key-Based Lookup (Bug 3 - Easy)
4. Interval Boundary Conditions and Overlap Detection (Bug 4 - Hard)
"""

import pytest
from backend.algorithms import (
    find_first_fit_slot,
    sort_slots_by_identifier,
    build_slot_status_lookup,
    get_slot_status_from_map,
    is_session_overlapping_interval,
    filter_sessions_by_interval
)


# ==============================================================================
# BUG 1 TEST: First-Fit Allocation Algorithm
# ==============================================================================
def test_first_fit_allocation_selects_first_valid_candidate():
    """
    Topic: First-Fit Allocation Algorithm
    Examines available slots in the defined order and selects the first slot
    compatible with the incoming vehicle without skipping an earlier candidate.
    """
    available_slots = [
        {"id": 1, "slot_number": "A-1", "slot_type": "compact", "is_occupied": 0},
        {"id": 2, "slot_number": "A-2", "slot_type": "compact", "is_occupied": 0},
        {"id": 3, "slot_number": "A-3", "slot_type": "standard", "is_occupied": 0}
    ]

    allocated = find_first_fit_slot(available_slots, vehicle_type="compact")

    assert allocated is not None, "First-fit allocation must find a compatible slot when candidates exist"
    # Expected: First compatible slot is A-1 at index 0.
    # Buggy behavior: Slices from index 1 and selects A-2 instead!
    assert allocated["slot_number"] == "A-1", (
        f"Expected first compatible slot 'A-1' to be allocated, but got '{allocated['slot_number']}'. "
        "The first candidate was skipped."
    )


# ==============================================================================
# BUG 2 TEST: Sorting Algorithms and Comparator Logic
# ==============================================================================
def test_sort_slots_natural_numeric_comparator():
    """
    Topic: Sorting Algorithms and Comparator Logic
    Slot identifiers must appear in natural numerical order, correctly handling
    multi-digit numbers so that 'A-2' appears before 'A-10'.
    """
    unsorted_slots = [
        {"slot_number": "A-10"},
        {"slot_number": "A-1"},
        {"slot_number": "A-2"},
        {"slot_number": "A-11"},
        {"slot_number": "A-3"}
    ]

    sorted_slots = sort_slots_by_identifier(unsorted_slots, order="asc")
    slot_order = [s["slot_number"] for s in sorted_slots]

    # Expected: ['A-1', 'A-2', 'A-3', 'A-10', 'A-11']
    # Buggy behavior: ['A-1', 'A-10', 'A-11', 'A-2', 'A-3'] due to lexicographical string sort
    expected_order = ["A-1", "A-2", "A-3", "A-10", "A-11"]
    assert slot_order == expected_order, (
        f"Expected natural numerical sort {expected_order}, but got {slot_order}. "
        "Lexicographical string sorting improperly sorted multi-digit identifiers."
    )


# ==============================================================================
# BUG 3 TEST: Hash Maps and Key-Based Lookup
# ==============================================================================
def test_hash_map_key_isolation_per_slot():
    """
    Topic: Hash Maps and Key-Based Lookup
    Each slot identifier must resolve to its own correct status.
    Occupying slot A-1 must not cause slot A-2 to inherit occupied status.
    """
    all_slots = [
        {"slot_number": "A-1", "is_occupied": 1},
        {"slot_number": "A-2", "is_occupied": 0}
    ]
    active_sessions = [
        {"slot_number": "A-1", "plate_number": "TEST-101", "vehicle_type": "compact"}
    ]

    status_map = build_slot_status_lookup(all_slots, active_sessions)

    # Check status of A-2 (which is unoccupied)
    a2_status = get_slot_status_from_map(status_map, "A-2")

    # Expected: A-2 is available and unoccupied
    # Buggy behavior: Key collision on prefix 'A' causes A-2 to inherit A-1's occupied status!
    assert a2_status["is_occupied"] is False, (
        "Slot 'A-2' should be available, but inherited 'occupied' status from another slot in the hash map."
    )
    assert a2_status["status"] == "available", (
        f"Expected 'available' for A-2, but got '{a2_status['status']}'"
    )


# ==============================================================================
# BUG 4 TEST: Interval Boundary Conditions and Overlap Detection
# ==============================================================================
def test_interval_boundary_touch_overlap_detection():
    """
    Topic: Interval Boundary Conditions and Overlap Detection
    Closed interval convention [filter_start, filter_end] must include sessions
    that touch the permitted boundary exactly (session_exit == filter_start or
    session_entry == filter_end).
    """
    filter_start = "2026-10-24T09:00:00"
    filter_end = "2026-10-24T12:00:00"

    # Session touching the start boundary: exited right at 09:00:00
    session_start_touch = {
        "session_id": "SES-TOUCH-START",
        "entry_time": "2026-10-24T08:00:00",
        "exit_time": "2026-10-24T09:00:00"
    }

    # Session touching the end boundary: entered right at 12:00:00
    session_end_touch = {
        "session_id": "SES-TOUCH-END",
        "entry_time": "2026-10-24T12:00:00",
        "exit_time": "2026-10-24T13:00:00"
    }

    # Expected: Both boundary-touching sessions are detected under inclusive convention
    # Buggy behavior: Strict inequality excludes both sessions!
    start_touch_overlaps = is_session_overlapping_interval(
        session_start_touch["entry_time"],
        session_start_touch["exit_time"],
        filter_start,
        filter_end
    )
    end_touch_overlaps = is_session_overlapping_interval(
        session_end_touch["entry_time"],
        session_end_touch["exit_time"],
        filter_start,
        filter_end
    )

    assert start_touch_overlaps is True, (
        "Session exiting exactly at filter_start (09:00:00) should be included under closed boundary convention"
    )
    assert end_touch_overlaps is True, (
        "Session entering exactly at filter_end (12:00:00) should be included under closed boundary convention"
    )
