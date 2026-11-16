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
- **Line:** 35

```python
# Change this:
return sorted(slots, key=lambda s: str(s.get("slot_number", "")), reverse=reverse)

# To this:
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
- **Lines:** 55 and 72

```python
# Line 55 - Change this:
lookup_key = slot_number.split("-")[0] if "-" in slot_number else slot_number

# Line 55 - To this:
lookup_key = slot_number


# Line 72 - Change this:
lookup_key = slot_number.split("-")[0] if "-" in slot_number else slot_number

# Line 72 - To this:
lookup_key = slot_number.strip().upper()
```

Use the full unique slot identifier as the dictionary key instead of truncating it to the section prefix.
This isolates the occupancy state of each bay so vacant slots do not inherit neighboring occupied statuses.

---

## BUG-04: Parking History Filter Misses Boundary Records

- **File:** `backend/algorithms.py`
- **Line:** 97

```python
# Change this:
return (entry_t < filter_end) and (exit_t > filter_start)

# To this:
return (entry_t <= filter_end) and (exit_t >= filter_start)
```

Replace strict inequality comparisons (`<` and `>`) with inclusive boundary operators (`<=` and `>=`).
This ensures sessions touching boundary timestamps exactly are properly included in the filtered history.
