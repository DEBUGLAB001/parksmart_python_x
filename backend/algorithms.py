"""
ParkSmart Core DSA Algorithms

Modules:
1. First-Fit Allocation Algorithm (Bug 1 - Easy)
2. Sorting Algorithms and Comparator Logic (Bug 2 - Easy)
3. Hash Maps and Key-Based Lookup (Bug 3 - Easy)
4. Interval Boundary Conditions and Overlap Detection (Bug 4 - Hard)
"""

from datetime import datetime
from typing import List, Dict, Optional, Any

# Compatible slot categories for each vehicle type
VEHICLE_COMPATIBILITY: Dict[str, List[str]] = {
    "motorcycle": ["compact", "standard", "large", "ev"],
    "compact": ["compact", "standard", "large"],
    "sedan": ["standard", "large"],
    "suv": ["standard", "large"],
    "ev": ["ev", "standard", "large"]
}


def is_compatible(slot_type: str, vehicle_type: str) -> bool:
    """Checks if a given slot type can accommodate a given vehicle type."""
    if not slot_type or not vehicle_type:
        return False
    compatible_types = VEHICLE_COMPATIBILITY.get(vehicle_type.lower(), ["standard", "large"])
    return slot_type.lower() in compatible_types


# ==============================================================================
# BUG 1: First-Fit Allocation Algorithm (Difficulty: Easy)
# Topic: First-Fit Allocation Algorithm
# ==============================================================================
def find_first_fit_slot(available_slots: List[Dict[str, Any]], vehicle_type: str) -> Optional[Dict[str, Any]]:
    """
    First-Fit Parking Allocation Algorithm.
    Examines available slots in the defined order and selects the first slot
    compatible with the incoming vehicle without skipping an earlier candidate.

    Expected Correct Behavior:
    - Iterate from index 0 across available slots.
    - Return the very first slot that is compatible with the vehicle.

    Intentional Bug:
    - The search loop starts at index 1 instead of index 0 (`available_slots[1:]`).
    - Defect: Skips the first valid candidate slot (at index 0). For instance,
      if slots A-1 and A-2 are both available and compatible, it incorrectly
      skips A-1 and allocates A-2!
    """
    if not available_slots:
        return None

    # INTENTIONAL BUG 1: Slicing from index 1 skips the first candidate slot (index 0)
    for slot in available_slots[1:]:
        if is_compatible(slot.get("slot_type", ""), vehicle_type):
            return slot

    return None


# ==============================================================================
# BUG 2: Sorting Parking Slots (Difficulty: Easy)
# Topic: Sorting Algorithms and Comparator Logic
# ==============================================================================
def sort_slots_by_identifier(slots: List[Dict[str, Any]], order: str = "asc") -> List[Dict[str, Any]]:
    """
    Sorts parking slots by their identifier (e.g., 'A-1', 'A-2', ..., 'A-10', 'A-11').

    Expected Correct Behavior:
    - Slot identifiers must appear in natural numerical order.
    - Multi-digit numbers must be sorted numerically so 'A-2' appears before 'A-10'.

    Intentional Bug:
    - Uses naive lexicographical string comparison on the entire slot identifier.
    - Defect: As strings, 'A-10' < 'A-2', causing 'A-10', 'A-11', 'A-12' to be
      sorted immediately before 'A-2' in ascending order.
    """
    reverse = (order.lower() == "desc")

    # INTENTIONAL BUG 2: Naive string comparator instead of natural/numeric parsing
    # Produces: ['A-1', 'A-10', 'A-11', 'A-12', 'A-2', 'A-3', ...]
    return sorted(slots, key=lambda s: str(s.get("slot_number", "")), reverse=reverse)


# ==============================================================================
# BUG 3: Hash Map Slot-Status Lookup (Difficulty: Easy)
# Topic: Hash Maps and Key-Based Lookup
# ==============================================================================
def build_slot_status_lookup(slots: List[Dict[str, Any]], active_sessions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Builds a hash map of slot statuses for key-based status lookups.

    Expected Correct Behavior:
    - Each unique slot identifier (e.g. 'A-1', 'A-2') must map to its own status.
    - Other slots must not inherit another slot's availability.

    Intentional Bug:
    - The key generation logic strips the specific slot number and retains only
      the section prefix before the hyphen (e.g. 'A' instead of 'A-1').
    - Defect: All slots in Section A collide on the same hash map key 'A'.
      When ANY slot in Section A becomes occupied, key 'A' is updated with that
      occupied state, causing subsequent lookups for other slots in Section A
      to inherit that occupied status.
    """
    status_map: Dict[str, Dict[str, Any]] = {}

    occupied_slots_by_number: Dict[str, Dict[str, Any]] = {}
    for session in active_sessions:
        slot_no = session.get("slot_number")
        if slot_no:
            occupied_slots_by_number[slot_no.strip().upper()] = session

    for slot in slots:
        slot_number = slot.get("slot_number", "").strip().upper()
        if not slot_number:
            continue

        is_occ = (slot_number in occupied_slots_by_number) or (slot.get("is_occupied", 0) == 1)
        session_info = occupied_slots_by_number.get(slot_number)

        # INTENTIONAL BUG 3: Key extraction strips the slot number and uses only the prefix (e.g. 'A')
        lookup_key = slot_number.split("-")[0] if "-" in slot_number else slot_number

        # If any slot with this section prefix is occupied, the entire section key gets marked occupied
        if is_occ or lookup_key not in status_map:
            status_map[lookup_key] = {
                "slot_number": slot_number,
                "status": "occupied" if is_occ else "available",
                "is_occupied": is_occ,
                "session": session_info
            }

    return status_map


def get_slot_status_from_map(status_map: Dict[str, Dict[str, Any]], slot_number: str) -> Dict[str, Any]:
    """
    Looks up a slot's status from the hash map.
    """
    if not slot_number:
        return {"status": "available", "is_occupied": False, "session": None}

    # INTENTIONAL BUG 3 (Matching Lookup): Looks up using only the section prefix
    lookup_key = slot_number.split("-")[0] if "-" in slot_number else slot_number
    return status_map.get(
        lookup_key,
        {"status": "available", "is_occupied": False, "session": None}
    )


# ==============================================================================
# BUG 4: Interval Boundary Handling for Parking Sessions (Difficulty: Hard)
# Topic: Interval Boundary Conditions and Overlap Detection
# ==============================================================================
def is_session_overlapping_interval(
    session_entry: str,
    session_exit: Optional[str],
    filter_start: str,
    filter_end: str
) -> bool:
    """
    Interval Boundary Conditions and Overlap Detection.
    Determines if a parking session interval [session_entry, session_exit] overlaps
    with a query interval [filter_start, filter_end].

    Boundary Convention:
    - Closed / inclusive boundaries [start, end].
    - Sessions touching the boundary (e.g., session_exit == filter_start or
      session_entry == filter_end) MUST be included as valid overlaps.
    - Invalid query ranges (filter_start > filter_end) MUST safely return False.

    Expected Correct Behavior:
    - session_entry <= filter_end and session_exit >= filter_start

    Intentional Bug:
    - Uses strict inequality ('<' and '>') on boundaries instead of inclusive ('<=' and '>=').
    - Defect: Excludes sessions that touch the boundary exactly at filter_start or filter_end!
    """
    if not filter_start or not filter_end:
        return True

    # Empty / inverted query interval safety check
    if filter_start > filter_end:
        return False

    if not session_entry:
        return False

    entry_t = session_entry
    exit_t = session_exit if session_exit else datetime.now().isoformat()

    # INTENTIONAL BUG 4: Strict inequality excludes boundary-touching sessions
    # (e.g. exit_t == filter_start or entry_t == filter_end)
    return (entry_t < filter_end) and (exit_t > filter_start)


def filter_sessions_by_interval(
    sessions: List[Dict[str, Any]],
    filter_start: Optional[str],
    filter_end: Optional[str]
) -> List[Dict[str, Any]]:
    """
    Filters a list of parking sessions by time interval.
    """
    if not filter_start and not filter_end:
        return sessions

    filtered = []
    for s in sessions:
        entry_time = s.get("entry_time", "")
        exit_time = s.get("exit_time")
        if is_session_overlapping_interval(entry_time, exit_time, filter_start or "", filter_end or ""):
            filtered.append(s)

    return filtered
