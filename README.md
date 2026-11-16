# ParkSmart — Smart Parking Management System

## 1. Your Mission: Investigate & Fix the Bugs

You are a **Full-Stack Developer** working on ParkSmart, a real-time smart parking management platform designed to help facility operators monitor bay occupancy, allocate spaces for incoming vehicles, and track historical parking sessions. The QA team has identified four critical algorithmic defects affecting parking operations.

Your responsibility is to investigate the existing codebase, reproduce each issue, identify its root cause, and implement reliable fixes without disrupting existing functionality.

### BUG-01: Parking Allocation Skips First Available Space

**Problem:** When registering an incoming vehicle, the automated allocation algorithm ignores the earliest available parking bay and assigns the vehicle to the second available space instead.

**How to identify it:** Open the dashboard and observe available slots in Section A (e.g., `A-1` and `A-2` are both unoccupied). Register an incoming vehicle (such as a compact car) and inspect the allocated bay confirmation. Notice that `A-2` is assigned while `A-1` was skipped.

**Your task:** Ensure the first-fit allocation algorithm evaluates parking spaces in order from the beginning (index 0) and allocates the very first compatible available bay without skipping.

<p align="center">
  <img width="1200" height="800" alt="image" src="https://cdn.debuglab.online/Lab/Parksmart/uploads/bug-01.png" />
</p>

### BUG-02: Parking Slot Order Jumbles Multi-Digit Numbers

**Problem:** When sorting parking bays in ascending order, multi-digit slot identifiers such as `A-10`, `A-11`, and `A-12` appear ahead of single-digit slots like `A-2` and `A-3`.

**How to identify it:** In the dashboard toolbar, select the sort dropdown and sort parking slots by identifier in ascending order. Observe the bay listing and notice that slots sort lexicographically (e.g., `A-1`, `A-10`, `A-11`, `A-12`, `A-2`, `A-3`) rather than naturally.

**Your task:** Update the sorting comparator logic so that parking spaces are arranged in natural numerical sequence (`A-1`, `A-2`, ..., `A-10`, `A-11`, `A-12`).

<p align="center">
  <img width="1200" height="800" alt="image" src="https://cdn.debuglab.online/Lab/Parksmart/uploads/bug-02.png" />
</p>

### BUG-03: Empty Parking Spaces Incorrectly Show as Occupied

**Problem:** When a single vehicle parks in a section, other empty spaces in that same section mistakenly report as occupied.

**How to identify it:** Park a vehicle in Section A. Next, inspect other empty spaces in Section A (e.g., `A-1` or `A-3`). Observe that vacant bays in Section A are falsely reported as occupied due to key collisions in the status lookup map.

**Your task:** Fix the status cache lookup key logic so that each parking bay maps to its full unique identifier, ensuring each bay resolves its availability independently without inheriting the state of neighboring bays.

<p align="center">
  <img width="1200" height="800" alt="image" src="https://cdn.debuglab.online/Lab/Parksmart/uploads/bug-03.png" />
</p>

### BUG-04: Parking History Filter Misses Boundary Records

**Problem:** Filtering parking history by start and end times excludes vehicle sessions that entered or exited right on the selected boundary timestamps.

**How to identify it:** Navigate to the Parking History tab, set the filter start time to `2026-10-24T09:00:00` and end time to `2026-10-24T12:00:00`, and click "Apply Range Filter". Observe that sessions touching the boundary exactly (such as `SES-104` which entered at `12:00:00`) are omitted from the results.

**Your task:** Update the time-interval overlap detection to use inclusive closed boundaries (`<=` and `>=`) so that sessions touching or overlapping the specified time boundaries are included in the search results.

<p align="center">
  <img width="1200" height="800" alt="image" src="https://cdn.debuglab.online/Lab/Parksmart/uploads/bug-04.png" />
</p>

---

## 2. Get Familiar With the Application

ParkSmart is a lightweight, real-time parking facility management system that provides a unified dashboard for tracking bay availability, vehicle sessions, and parking analytics.

**Core Features:**

- **Real-Time Occupancy Dashboard:** Monitor total capacity, available bays, occupied bays, and live facility occupancy percentages.

- **Visual Parking Map:** View individual parking spaces categorized by vehicle compatibility (Compact, Standard, EV Charging, and Large).

- **Automated Vehicle Allocation:** Register incoming vehicles with license plate and vehicle type details to automatically assign a compatible bay using first-fit allocation.

- **Bay Sorting & Filtering:** Sort bays by identifier and filter spaces by vehicle category or occupancy status.

- **Vehicle Departure & Fee Processing:** Release occupied bays upon vehicle exit, record departure timestamps, and calculate parking fees based on duration.

- **Parking History & Interval Search:** Inspect historical parking logs with customizable start and end time filters to analyze facility turnover.

---

## 3. Expected Behaviour After Fixing the Bugs

Once all reported issues have been resolved, the application should behave as follows:

1. **First-Fit Allocation:** Arriving vehicles are assigned the first compatible space in sequence (e.g., allocating `A-1` when available rather than skipping to `A-2`).

2. **Natural Slot Ordering:** Sorting parking bays arranges slot numbers in natural numerical order (`A-1`, `A-2`, `A-3` through `A-12`), with multi-digit numbers correctly placed after single-digit numbers.

3. **Independent Slot Status:** Parking a vehicle in one slot leaves all other unoccupied spaces in that section marked as available.

4. **Inclusive History Filtering:** Filtering parking history by interval includes all sessions that touch or overlap the chosen time range, including exact boundary timestamps.

All existing parking management functionality and test suites must pass successfully.
