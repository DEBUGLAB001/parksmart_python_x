"""
Database management module for ParkSmart.
Uses SQLite for persistent storage with parameterized queries and transactions.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
from backend.seed_data import INITIAL_SLOTS, INITIAL_HISTORY

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "parksmart.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row_factory set to dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(force_reseed: bool = False):
    """Initializes tables and seeds initial data if database is empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS parking_sessions;")
        cursor.execute("DROP TABLE IF EXISTS vehicles;")
        cursor.execute("DROP TABLE IF EXISTS slots;")

    # Slots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_number TEXT UNIQUE NOT NULL,
            section TEXT NOT NULL,
            slot_type TEXT NOT NULL,
            is_occupied INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Vehicles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT UNIQUE NOT NULL,
            vehicle_type TEXT NOT NULL,
            color TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Parking sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            slot_id INTEGER NOT NULL,
            slot_number TEXT NOT NULL,
            vehicle_id INTEGER,
            plate_number TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            entry_time TEXT NOT NULL,
            exit_time TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            fee REAL DEFAULT 0.0,
            FOREIGN KEY (slot_id) REFERENCES slots (id)
        );
    """)

    # Seed slots if table is empty
    cursor.execute("SELECT COUNT(*) as count FROM slots;")
    count = cursor.fetchone()["count"]
    if count == 0:
        for s in INITIAL_SLOTS:
            cursor.execute(
                "INSERT INTO slots (slot_number, section, slot_type, is_occupied) VALUES (?, ?, ?, ?);",
                (s["slot_number"], s["section"], s["slot_type"], s["is_occupied"])
            )

        # Seed initial history sessions
        for h in INITIAL_HISTORY:
            # find slot id if exists
            cursor.execute("SELECT id FROM slots WHERE slot_number = ?;", (h["slot_number"],))
            slot_row = cursor.fetchone()
            slot_id = slot_row["id"] if slot_row else 1

            cursor.execute("""
                INSERT INTO parking_sessions (session_id, slot_id, slot_number, plate_number, vehicle_type, entry_time, exit_time, status, fee)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                h["session_id"],
                slot_id,
                h["slot_number"],
                h["plate_number"],
                h["vehicle_type"],
                h["entry_time"],
                h["exit_time"],
                h["status"],
                h["fee"]
            ))

    conn.commit()
    conn.close()


def get_all_slots() -> List[Dict[str, Any]]:
    """Fetches all slots from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM slots ORDER BY id ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_slot_by_number(slot_number: str) -> Optional[Dict[str, Any]]:
    """Fetches a single slot by its slot number."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM slots WHERE UPPER(slot_number) = UPPER(?);", (slot_number.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_available_slots() -> List[Dict[str, Any]]:
    """Fetches all unoccupied slots in natural order of slot_number."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM slots WHERE is_occupied = 0 ORDER BY id ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_active_sessions() -> List[Dict[str, Any]]:
    """Fetches all active parking sessions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM parking_sessions 
        WHERE status = 'active'
        ORDER BY entry_time DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_active_session_by_plate(plate_number: str) -> Optional[Dict[str, Any]]:
    """Checks for an active parking session by vehicle plate."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM parking_sessions 
        WHERE UPPER(plate_number) = UPPER(?) AND status = 'active';
    """, (plate_number.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_active_session_by_slot(slot_number: str) -> Optional[Dict[str, Any]]:
    """Checks for an active parking session by slot number."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM parking_sessions 
        WHERE UPPER(slot_number) = UPPER(?) AND status = 'active';
    """, (slot_number.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_vehicle_and_session(
    plate_number: str,
    vehicle_type: str,
    color: Optional[str],
    description: Optional[str],
    allocated_slot: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Creates a vehicle entry and active parking session in a single transaction.
    Marks the slot as occupied.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        plate = plate_number.strip().upper()
        v_type = vehicle_type.strip().lower()

        # Insert or update vehicle info
        cursor.execute("""
            INSERT INTO vehicles (plate_number, vehicle_type, color, description)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(plate_number) DO UPDATE SET
                vehicle_type=excluded.vehicle_type,
                color=excluded.color,
                description=excluded.description;
        """, (plate, v_type, color or "", description or ""))

        cursor.execute("SELECT id FROM vehicles WHERE plate_number = ?;", (plate,))
        vehicle_id = cursor.fetchone()["id"]

        # Mark slot as occupied
        cursor.execute("UPDATE slots SET is_occupied = 1 WHERE id = ?;", (allocated_slot["id"],))

        # Generate unique session ID
        session_id = f"SES-{int(datetime.now().timestamp() * 1000) % 1000000}"
        entry_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        cursor.execute("""
            INSERT INTO parking_sessions (session_id, slot_id, slot_number, vehicle_id, plate_number, vehicle_type, entry_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active');
        """, (session_id, allocated_slot["id"], allocated_slot["slot_number"], vehicle_id, plate, v_type, entry_time))

        conn.commit()

        # Fetch the created session
        cursor.execute("SELECT * FROM parking_sessions WHERE session_id = ?;", (session_id,))
        session_row = dict(cursor.fetchone())
        return session_row
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def end_parking_session(identifier: str) -> Optional[Dict[str, Any]]:
    """
    Ends an active parking session by session_id, slot_number, or plate_number.
    Releases the slot and computes parking fee.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        ident = identifier.strip().upper()
        cursor.execute("""
            SELECT * FROM parking_sessions
            WHERE (UPPER(session_id) = ? OR UPPER(slot_number) = ? OR UPPER(plate_number) = ?)
              AND status = 'active';
        """, (ident, ident, ident))
        session_row = cursor.fetchone()

        if not session_row:
            return None

        session = dict(session_row)
        exit_time_dt = datetime.now()
        exit_time_str = exit_time_dt.strftime("%Y-%m-%dT%H:%M:%S")

        # Calculate duration and fee ($5 base + $2.50 per hour)
        entry_time_dt = datetime.fromisoformat(session["entry_time"])
        duration_hours = max(0.5, (exit_time_dt - entry_time_dt).total_seconds() / 3600.0)
        fee = round(5.0 + (duration_hours * 2.5), 2)

        # Update session
        cursor.execute("""
            UPDATE parking_sessions
            SET status = 'completed', exit_time = ?, fee = ?
            WHERE id = ?;
        """, (exit_time_str, fee, session["id"]))

        # Release slot
        cursor.execute("UPDATE slots SET is_occupied = 0 WHERE id = ?;", (session["slot_id"],))

        conn.commit()

        cursor.execute("SELECT * FROM parking_sessions WHERE id = ?;", (session["id"],))
        updated_session = dict(cursor.fetchone())
        return updated_session
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_parking_history(search: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches completed parking sessions, optionally filtered by search text."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if search:
        term = f"%{search.strip().upper()}%"
        cursor.execute("""
            SELECT * FROM parking_sessions
            WHERE status = 'completed' AND (UPPER(plate_number) LIKE ? OR UPPER(slot_number) LIKE ? OR UPPER(session_id) LIKE ?)
            ORDER BY exit_time DESC;
        """, (term, term, term))
    else:
        cursor.execute("""
            SELECT * FROM parking_sessions
            WHERE status = 'completed'
            ORDER BY exit_time DESC;
        """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_occupancy_stats() -> Dict[str, Any]:
    """Calculates live occupancy statistics from database records."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM slots;")
    total_slots = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as occupied FROM slots WHERE is_occupied = 1;")
    occupied_slots = cursor.fetchone()["occupied"]

    cursor.execute("SELECT COUNT(*) as active FROM parking_sessions WHERE status = 'active';")
    active_sessions = cursor.fetchone()["active"]

    cursor.execute("SELECT COUNT(*) as completed FROM parking_sessions WHERE status = 'completed';")
    completed_sessions = cursor.fetchone()["completed"]

    conn.close()

    available_slots = max(0, total_slots - occupied_slots)
    occupancy_rate = round((occupied_slots / total_slots * 100), 1) if total_slots > 0 else 0.0

    return {
        "total_spaces": total_slots,
        "available_spaces": available_slots,
        "occupied_spaces": occupied_slots,
        "occupancy_percentage": occupancy_rate,
        "active_sessions": active_sessions,
        "completed_sessions": completed_sessions
    }
