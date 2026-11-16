from datetime import datetime
from typing import List, Dict, Optional, Any
import re

VEHICLE_COMPATIBILITY: Dict[str, List[str]] = {
    "motorcycle": ["compact", "standard", "large", "ev"],
    "compact": ["compact", "standard", "large"],
    "sedan": ["standard", "large"],
    "suv": ["standard", "large"],
    "ev": ["ev", "standard", "large"]
}


def is_compatible(slot_type: str, vehicle_type: str) -> bool:
    if not slot_type or not vehicle_type:
        return False
    compatible_types = VEHICLE_COMPATIBILITY.get(vehicle_type.lower(), ["standard", "large"])
    return slot_type.lower() in compatible_types


def find_first_fit_slot(available_slots: List[Dict[str, Any]], vehicle_type: str) -> Optional[Dict[str, Any]]:
    if not available_slots:
        return None

    for slot in available_slots[1:]:
        if is_compatible(slot.get("slot_type", ""), vehicle_type):
            return slot

    return None


def sort_slots_by_identifier(slots: List[Dict[str, Any]], order: str = "asc") -> List[Dict[str, Any]]:
    reverse = (order.lower() == "desc")

    return sorted(slots, key=lambda s: str(s.get("slot_number", "")), reverse=reverse)


def build_slot_status_lookup(slots: List[Dict[str, Any]], active_sessions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
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

        lookup_key = slot_number.split("-")[0] if "-" in slot_number else slot_number

        if is_occ or lookup_key not in status_map:
            status_map[lookup_key] = {
                "slot_number": slot_number,
                "status": "occupied" if is_occ else "available",
                "is_occupied": is_occ,
                "session": session_info
            }

    return status_map


def get_slot_status_from_map(status_map: Dict[str, Dict[str, Any]], slot_number: str) -> Dict[str, Any]:
    if not slot_number:
        return {"status": "available", "is_occupied": False, "session": None}

    lookup_key = slot_number.split("-")[0] if "-" in slot_number else slot_number
    return status_map.get(
        lookup_key,
        {"status": "available", "is_occupied": False, "session": None}
    )


def is_session_overlapping_interval(
    session_entry: str,
    session_exit: Optional[str],
    filter_start: str,
    filter_end: str
) -> bool:
    if not filter_start or not filter_end:
        return True

    if filter_start > filter_end:
        return False

    if not session_entry:
        return False

    entry_t = session_entry
    exit_t = session_exit if session_exit else datetime.now().isoformat()

    return (entry_t < filter_end) and (exit_t > filter_start)


def filter_sessions_by_interval(
    sessions: List[Dict[str, Any]],
    filter_start: Optional[str],
    filter_end: Optional[str]
) -> List[Dict[str, Any]]:
    if not filter_start and not filter_end:
        return sessions

    filtered = []
    for s in sessions:
        entry_time = s.get("entry_time", "")
        exit_time = s.get("exit_time")
        if is_session_overlapping_interval(entry_time, exit_time, filter_start or "", filter_end or ""):
            filtered.append(s)

    return filtered
