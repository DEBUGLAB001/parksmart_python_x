# ParkSmart

## Description

ParkSmart is an urban parking management system that tracks facility occupancy, assigns incoming vehicles to compatible parking bays, and records vehicle exits. The backend is implemented in Python using Flask (`app.py`), backed by SQLite (`backend/database.py`) for transaction-safe persistence of slots, vehicles, and parking sessions. Core allocation algorithms, sorting comparator logic, hash map status caching, and session interval overlap detection are housed in `backend/algorithms.py`. Initial facility layout (Sections A and B) and boundary history records are defined in `backend/seed_data.py`. The frontend is a vanilla JavaScript client (`static/js/app.js`) with responsive CSS (`static/css/style.css`) and HTML templates (`templates/index.html`) communicating over RESTful API endpoints.

## Repository Structure

```
.
├── app.py                     # Flask application entry point and REST API routes
├── challenge.json             # Challenge configuration and runtime specifications
├── conftest.py                # Telemetry summary hook for test reporting
├── pytest.ini                 # Pytest runner configuration
├── requirements.txt           # Python package dependencies
├── backend/
│   ├── __init__.py
│   ├── algorithms.py          # Core allocation, sorting, lookup, and interval algorithms
│   ├── database.py            # SQLite schema initialization, queries, and transactions
│   └── seed_data.py           # Parking facility layout and history seed data
├── static/
│   ├── favicon.svg            # Application vector icon
│   ├── css/
│   │   └── style.css          # Design system styling and layout rules
│   └── js/
│       └── app.js             # Client state management, DOM rendering, and API calls
└── templates/
    └── index.html             # Dashboard markup structure
```

## Bugs and Bug Locations

1. First-Fit Allocation Skips Initial Candidate

- Bug location: `backend/algorithms.py`, within `find_first_fit_slot()`.
- How to observe it: Register an incoming compact vehicle when slots `A-1` and `A-2` are available. Check the allocated slot in the confirmation toast or active session list.
- Failure: The search loop slices candidate slots starting at index 1 (`available_slots[1:]`), skipping the valid candidate at index 0 and allocating `A-2` instead of `A-1`.
- Expected: Iterate over available candidates starting from index 0 and allocate the first compatible slot encountered.

2. Lexicographical Sorting Comparator on Multi-Digit Slot Identifiers

- Bug location: `backend/algorithms.py`, within `sort_slots_by_identifier()`.
- How to observe it: In the dashboard toolbar, set the sort selector to "Slot ID (Ascending)". Observe the bay order in Section A.
- Failure: Raw string comparison (`str(slot_number)`) sorts identifiers lexicographically, placing multi-digit numbers `A-10`, `A-11`, and `A-12` immediately before `A-2`.
- Expected: Parse the alpha section prefix and integer suffix so multi-digit slot identifiers sort in natural numerical order (`A-1`, `A-2`, ..., `A-10`, `A-11`, `A-12`).

3. Prefix Collision in Hash Map Slot Status Lookup

- Bug location: `backend/algorithms.py`, within `build_slot_status_lookup()` and `get_slot_status_from_map()`.
- How to observe it: Park a vehicle in any slot in Section A, then inspect an unoccupied slot in Section A via slot click or the visual map.
- Failure: Key generation extracts only the section prefix before the hyphen (`slot_number.split("-")[0]`), causing all Section A slots to share key `'A'`. Once any slot is occupied, all slots with prefix `'A'` inherit the occupied state.
- Expected: Key status lookup entries by their full unique identifier (`slot_number.strip().upper()`) so each slot resolves its status independently.

4. Strict Inequality in Time-Interval Boundary Handling

- Bug location: `backend/algorithms.py`, within `is_session_overlapping_interval()` and `filter_sessions_by_interval()`.
- How to observe it: Navigate to the Parking History tab, set start time to `2026-10-24T09:00` and end time to `2026-10-24T12:00`, and click "Apply Range Filter".
- Failure: Strict inequality comparisons (`entry_t < filter_end` and `exit_t > filter_start`) exclude sessions that touch boundaries exactly, omitting sessions ending at `09:00:00` (`SES-101`) or starting at `12:00:00` (`SES-104`).
- Expected: Use inclusive closed boundary comparisons (`entry_t <= filter_end` and `exit_t >= filter_start`) to detect all boundary-touching overlaps.
