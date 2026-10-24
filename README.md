# ParkSmart — Smart Parking Management System

ParkSmart is a real-time parking facility dashboard designed for monitoring parking bays, tracking active vehicles, and managing facility turnover. It gives operators an interactive visual map of all parking spaces, automated bay allocation for incoming vehicles, and detailed records of parking fees and history.

## 1. Application Overview

### Core Functionality

- Real-Time Occupancy Dashboard: Monitor total capacity, available bays, occupied bays, and live facility occupancy percentages.
- Visual Parking Map: View individual parking spaces categorized by vehicle compatibility (Compact, Standard, EV Charging, and Large).
- Vehicle Entry & Allocation: Register arriving vehicles with license plate details and automatically assign a suitable available slot.
- Search and Filtering: Find parking bays by slot identifier or license plate, filter by status or vehicle category, and sort bay order.
- Vehicle Exit Processing: Release occupied parking bays upon vehicle departure, record timestamps, and calculate total parking fees.
- Parking History Logs: Inspect historical parking sessions with start and end time filters to analyze facility usage.

## 2. Debugging Challenge

The parking facility system has been deployed with several operational glitches affecting slot allocation, sorting order, space availability displays, and historical search results. Your goal is to identify each defect and restore correct behavior across all facility workflows.

### Reported Issues & Tasks:

Issue 1: Parking Allocation Skips First Available Space

- User Symptom: When registering an incoming vehicle, the system ignores the earliest available space and assigns the vehicle to the second space instead.
- Task: Ensure the allocation algorithm checks spaces in order from the beginning and assigns the first compatible available bay without skipping.

Issue 2: Parking Slot Order Jumbles Multi-Digit Numbers

- User Symptom: When sorting parking bays in ascending order, multi-digit slots like A-10 and A-11 appear ahead of A-2 and A-3.
- Task: Correct the sorting comparator so that parking spaces are arranged in natural numerical sequence.

Issue 3: Empty Parking Spaces Incorrectly Show as Occupied

- User Symptom: When one vehicle parks in Section A, other empty spaces in the same section mistakenly report as occupied.
- Task: Fix the slot status lookup so that each parking bay resolves its own availability independently without inheriting the state of neighboring bays.

Issue 4: Parking History Filter Misses Boundary Records

- User Symptom: Filtering parking history by start and end times excludes vehicles that entered or exited right on the selected boundary times.
- Task: Update the time-range filtering logic so that sessions touching or overlapping the specified time boundaries are included in the search results.

## 3. Expected Behavior After Fixing Bugs

1. Registering an arriving vehicle assigns the first compatible space in the facility (for example, slot A-1 is allocated rather than skipped).
2. Sorting parking bays by slot number arranges them in natural numerical order (A-1, A-2, A-3 through A-12).
3. Parking a vehicle in one slot leaves all other unoccupied spaces in that section marked as available.
4. Filtering parking history includes all sessions that touch or overlap the chosen time range, including boundary timestamps.

You can verify your fixes with the `pytest` command. Once all issues are resolved, the dashboard will accurately reflect live parking operations and all tests will pass.