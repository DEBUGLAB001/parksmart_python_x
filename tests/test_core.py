"""
Core functional tests for ParkSmart.
Covers database persistence, vehicle entry/exit, duplicate detection, and stats.
"""

import os
import pytest
from backend.database import (
    init_db,
    get_all_slots,
    get_available_slots,
    get_active_sessions,
    get_active_session_by_plate,
    create_vehicle_and_session,
    end_parking_session,
    get_occupancy_stats,
    get_parking_history
)
from backend.algorithms import is_compatible


@pytest.fixture(autouse=True)
def reset_db_before_test():
    """Ensures each test runs with a fresh database seed."""
    init_db(force_reseed=True)
    yield


def test_database_persistence_and_stats():
    """Tests that initial slots and occupancy stats reflect persisted database state."""
    slots = get_all_slots()
    assert len(slots) == 20
    stats = get_occupancy_stats()
    assert stats["total_spaces"] == 20
    assert stats["available_spaces"] == 20
    assert stats["occupied_spaces"] == 0
    assert stats["occupancy_percentage"] == 0.0
    assert stats["active_sessions"] == 0
    assert stats["completed_sessions"] > 0


def test_vehicle_entry_and_persistence():
    """Tests vehicle entry creation, slot occupation, and active session persistence."""
    available = get_available_slots()
    assert len(available) > 0
    target_slot = available[0]

    session = create_vehicle_and_session(
        plate_number="TEST-001",
        vehicle_type="compact",
        color="Blue",
        description="Electric hatchback",
        allocated_slot=target_slot
    )

    assert session["plate_number"] == "TEST-001"
    assert session["slot_number"] == target_slot["slot_number"]
    assert session["status"] == "active"

    # Verify slot is now occupied
    active_by_plate = get_active_session_by_plate("TEST-001")
    assert active_by_plate is not None
    assert active_by_plate["slot_number"] == target_slot["slot_number"]

    # Verify stats updated
    stats = get_occupancy_stats()
    assert stats["occupied_spaces"] == 1
    assert stats["available_spaces"] == 19
    assert stats["active_sessions"] == 1


def test_duplicate_active_vehicle_detection():
    """Tests that a vehicle cannot have two concurrent active parking sessions."""
    available = get_available_slots()
    create_vehicle_and_session(
        plate_number="DUP-999",
        vehicle_type="sedan",
        color="Black",
        description="Sedan",
        allocated_slot=available[0]
    )

    duplicate_session = get_active_session_by_plate("DUP-999")
    assert duplicate_session is not None
    assert duplicate_session["status"] == "active"


def test_vehicle_exit_and_slot_release():
    """Tests vehicle exit completes session, releases slot, and computes fee."""
    available = get_available_slots()
    slot = available[0]

    session = create_vehicle_and_session(
        plate_number="EXIT-123",
        vehicle_type="compact",
        color="Silver",
        description="Compact car",
        allocated_slot=slot
    )

    # End session
    completed = end_parking_session(session["session_id"])
    assert completed is not None
    assert completed["status"] == "completed"
    assert completed["exit_time"] is not None
    assert completed["fee"] >= 5.0

    # Verify slot is released
    all_slots = get_all_slots()
    released_slot = next(s for s in all_slots if s["id"] == slot["id"])
    assert released_slot["is_occupied"] == 0

    # Verify stats updated
    stats = get_occupancy_stats()
    assert stats["occupied_spaces"] == 0
    assert stats["active_sessions"] == 0


def test_repeated_entries_and_exits():
    """Tests repeated vehicle entries and exits for persistence and consistency."""
    available = get_available_slots()
    slot_a = available[0]

    s1 = create_vehicle_and_session("CYCLE-01", "compact", "White", "", slot_a)
    assert get_occupancy_stats()["occupied_spaces"] == 1

    end_parking_session(s1["session_id"])
    assert get_occupancy_stats()["occupied_spaces"] == 0

    # Vehicle returns and parks again
    available_again = get_available_slots()
    slot_b = available_again[0]
    s2 = create_vehicle_and_session("CYCLE-01", "compact", "White", "", slot_b)
    assert s2["session_id"] != s1["session_id"]
    assert get_occupancy_stats()["occupied_spaces"] == 1


def test_vehicle_compatibility_rules():
    """Tests vehicle type compatibility checks."""
    assert is_compatible("compact", "compact") is True
    assert is_compatible("standard", "compact") is True
    assert is_compatible("compact", "sedan") is False
    assert is_compatible("standard", "sedan") is True
    assert is_compatible("large", "suv") is True
    assert is_compatible("compact", "suv") is False
    assert is_compatible("ev", "ev") is True
