# Solutions

## BUG-01: Parking Allocation Skips First Available Space

- **File:** `backend/algorithms.py`
- **Line:** 25

```python
# Change this:
    for slot in available_slots[1:]:

# To this:
    for slot in available_slots:
```

Iterate over all candidate slots starting from index 0 instead of slicing from index 1.
This ensures the earliest available compatible bay is selected rather than skipped.

---

## BUG-02: Parking Slot Order Jumbles Multi-Digit Numbers

- **File:** `backend/algorithms.py`
- **Function:** `sort_slots_by_identifier` (Lines 32–35)

Replace the entire `sort_slots_by_identifier` function with:

```python
def sort_slots_by_identifier(slots: List[Dict[str, Any]], order: str = "asc") -> List[Dict[str, Any]]:
    reverse = (order.lower() == "desc")

    def parse_slot_key(slot):
        val = str(slot.get("slot_number", "")).strip()
        match = re.match(r"^([A-Za-z]+)-?(\d+)$", val)
        return (match.group(1).upper(), int(match.group(2))) if match else (val, 0)

    return sorted(slots, key=parse_slot_key, reverse=reverse)
```

Parse slot identifiers into their alphabetical section prefix and numeric integer suffix.
This sorts slots in natural numerical sequence so multi-digit numbers like `A-10` appear after `A-2`.

---

## BUG-03: Empty Parking Spaces Incorrectly Show as Occupied

- **File:** `backend/algorithms.py`
- **Lines:** 60 and 77

```python
# Line 60 - Change this:
        lookup_key = slot_number.split("-")[0] if "-" in slot_number else slot_number

# Line 60 - To this:
        lookup_key = slot_number


# Line 77 - Change this:
    lookup_key = slot_number.split("-")[0] if "-" in slot_number else slot_number

# Line 77 - To this:
    lookup_key = slot_number.strip().upper()
```

Use the full unique slot identifier as the dictionary key instead of truncating it to the section prefix.
This isolates the occupancy state of each bay so vacant slots do not inherit neighboring occupied statuses.

---

## BUG-04: Parking History Filter Misses Boundary Records

- **File:** `backend/algorithms.py`
- **Line:** 102

```python
# Change this:
    return (entry_t < filter_end) and (exit_t > filter_start)

# To this:
    return (entry_t <= filter_end) and (exit_t >= filter_start)
```

Replace strict inequality comparisons (`<` and `>`) with inclusive boundary operators (`<=` and `>=`).
This ensures sessions touching boundary timestamps exactly are properly included in the filtered history.
