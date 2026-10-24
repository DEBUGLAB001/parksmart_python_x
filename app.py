"""
ParkSmart: Smart Parking Management System
Flask Backend Application
"""

import os
from flask import Flask, jsonify, request, render_template, send_from_directory
from backend.database import (
    init_db,
    get_all_slots,
    get_slot_by_number,
    get_available_slots,
    get_active_sessions,
    get_active_session_by_plate,
    get_active_session_by_slot,
    create_vehicle_and_session,
    end_parking_session,
    get_parking_history,
    get_occupancy_stats
)
from backend.algorithms import (
    find_first_fit_slot,
    sort_slots_by_identifier,
    build_slot_status_lookup,
    get_slot_status_from_map,
    filter_sessions_by_interval,
    is_compatible
)

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Ensure database is initialized
init_db()


@app.route("/")
def index():
    """Serves the main ParkSmart dashboard interface."""
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "ParkSmart Smart Parking API",
        "version": "1.0.0"
    }), 200


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Calculates and returns live parking occupancy metrics."""
    try:
        stats = get_occupancy_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/slots", methods=["GET"])
def get_slots():
    """
    Returns the list of parking slots with live status.
    Supports filtering by status ('all', 'available', 'occupied'),
    by slot_type, and sorting.
    """
    try:
        all_slots = get_all_slots()
        active_sessions = get_active_sessions()

        # Bug 3 (Hash Map Lookup): Build status lookup table and look up slot statuses
        status_map = build_slot_status_lookup(all_slots, active_sessions)

        enriched_slots = []
        for s in all_slots:
            slot_info = dict(s)
            # Use hash map lookup to resolve status
            lookup = get_slot_status_from_map(status_map, s["slot_number"])
            slot_info["is_occupied"] = 1 if lookup.get("is_occupied") else 0
            slot_info["status"] = lookup.get("status", "available")
            slot_info["active_session"] = lookup.get("session")
            enriched_slots.append(slot_info)

        # Apply filtering
        status_filter = request.args.get("status", "all").lower()
        if status_filter in ["available", "occupied"]:
            is_occ = 1 if status_filter == "occupied" else 0
            enriched_slots = [s for s in enriched_slots if s["is_occupied"] == is_occ]

        type_filter = request.args.get("slot_type", "all").lower()
        if type_filter != "all":
            enriched_slots = [s for s in enriched_slots if s["slot_type"].lower() == type_filter]

        search_query = request.args.get("search", "").strip().upper()
        if search_query:
            filtered = []
            for s in enriched_slots:
                slot_match = search_query in s["slot_number"].upper()
                sess = s.get("active_session")
                plate_match = sess and (search_query in sess.get("plate_number", "").upper())
                if slot_match or plate_match:
                    filtered.append(s)
            enriched_slots = filtered

        # Apply sorting
        sort_by = request.args.get("sort_by", "slot_number")
        order = request.args.get("order", "asc")

        if sort_by == "slot_number":
            # Bug 2 (Sorting Comparator): Sort using the comparator algorithm
            enriched_slots = sort_slots_by_identifier(enriched_slots, order=order)
        elif sort_by == "slot_type":
            reverse = (order.lower() == "desc")
            enriched_slots = sorted(enriched_slots, key=lambda s: s["slot_type"], reverse=reverse)
        elif sort_by == "status":
            reverse = (order.lower() == "desc")
            enriched_slots = sorted(enriched_slots, key=lambda s: s["is_occupied"], reverse=reverse)

        return jsonify(enriched_slots), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/slots/<slot_number>", methods=["GET"])
def get_slot_detail(slot_number: str):
    """Fetches details for a single slot with its active session if occupied."""
    try:
        slot = get_slot_by_number(slot_number)
        if not slot:
            return jsonify({"error": f"Slot '{slot_number}' not found"}), 404

        active_sessions = get_active_sessions()
        all_slots = get_all_slots()
        status_map = build_slot_status_lookup(all_slots, active_sessions)
        lookup = get_slot_status_from_map(status_map, slot["slot_number"])

        slot_info = dict(slot)
        slot_info["is_occupied"] = 1 if lookup.get("is_occupied") else 0
        slot_info["status"] = lookup.get("status", "available")
        slot_info["active_session"] = lookup.get("session")

        return jsonify(slot_info), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/vehicles/entry", methods=["POST"])
def register_vehicle_entry():
    """
    Registers an arriving vehicle and allocates an available compatible slot.
    Uses the First-Fit allocation algorithm (Bug 1).
    """
    try:
        data = request.get_json() or {}
        plate_number = data.get("plate_number", "").strip().upper()
        vehicle_type = data.get("vehicle_type", "").strip().lower()
        color = data.get("color", "").strip()
        description = data.get("description", "").strip()

        # Validation
        if not plate_number:
            return jsonify({"error": "Vehicle registration plate number is required"}), 400
        if not vehicle_type:
            return jsonify({"error": "Vehicle type is required"}), 400
        if vehicle_type not in ["compact", "sedan", "suv", "motorcycle", "ev"]:
            return jsonify({"error": f"Invalid vehicle type '{vehicle_type}'"}), 400

        # Check for duplicate active parking session
        existing_session = get_active_session_by_plate(plate_number)
        if existing_session:
            return jsonify({
                "error": f"Vehicle with plate '{plate_number}' is already parked in slot {existing_session['slot_number']}"
            }), 409

        # Get all currently unoccupied slots
        available_slots = get_available_slots()
        if not available_slots:
            return jsonify({"error": "Parking facility is full. No available slots."}), 422

        # Filter by compatibility first to check if any compatible slot exists
        compatible_candidates = [s for s in available_slots if is_compatible(s["slot_type"], vehicle_type)]
        if not compatible_candidates:
            return jsonify({
                "error": f"No compatible parking space available for vehicle type '{vehicle_type}'"
            }), 422

        # Bug 1 (First-Fit Allocation): Chooses slot using find_first_fit_slot
        allocated_slot = find_first_fit_slot(available_slots, vehicle_type)

        if not allocated_slot:
            # Fallback if first-fit returned None due to candidate skipping
            return jsonify({
                "error": "Allocation failed: could not select an available slot"
            }), 422

        # Create session and persist state
        session = create_vehicle_and_session(
            plate_number=plate_number,
            vehicle_type=vehicle_type,
            color=color,
            description=description,
            allocated_slot=allocated_slot
        )

        return jsonify({
            "message": f"Vehicle '{plate_number}' successfully allocated to slot {allocated_slot['slot_number']}",
            "slot": allocated_slot,
            "session": session
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/vehicles/exit", methods=["POST"])
def register_vehicle_exit():
    """
    Records a vehicle exit, releases the assigned slot, and completes the parking session.
    Accepts identifier (session_id, slot_number, or plate_number).
    """
    try:
        data = request.get_json() or {}
        identifier = data.get("identifier") or data.get("slot_number") or data.get("plate_number") or data.get("session_id")

        if not identifier or not str(identifier).strip():
            return jsonify({"error": "Slot identifier, license plate, or session ID is required"}), 400

        updated_session = end_parking_session(str(identifier).strip())
        if not updated_session:
            return jsonify({
                "error": f"No active parking session found for identifier '{identifier}'"
            }), 404

        return jsonify({
            "message": f"Vehicle '{updated_session['plate_number']}' exited slot {updated_session['slot_number']}",
            "session": updated_session
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions/active", methods=["GET"])
def get_active_sessions_list():
    """Returns currently active parking sessions."""
    try:
        sessions = get_active_sessions()
        return jsonify(sessions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions/history", methods=["GET"])
def get_sessions_history():
    """
    Returns parking history with optional search and time interval filtering.
    Uses interval overlap filtering (Bug 4).
    """
    try:
        search = request.args.get("search", "").strip()
        start_time = request.args.get("start_time", "").strip()
        end_time = request.args.get("end_time", "").strip()

        history = get_parking_history(search=search if search else None)

        if start_time or end_time:
            # Bug 4 (Interval Boundary Overlap): Filter sessions with boundary check
            history = filter_sessions_by_interval(history, start_time or None, end_time or None)

        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def reset_database():
    """Resets database to initial seed."""
    try:
        init_db(force_reseed=True)
        return jsonify({"message": "Database successfully reset to initial seed"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Flask development server binding to 0.0.0.0:5000 as required
    app.run(host="0.0.0.0", port=5000, debug=True)
