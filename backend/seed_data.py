"""
Initial seed data for ParkSmart.
Provides realistic parking facility configuration and historical sessions.
"""

INITIAL_SLOTS = [
    # Section A
    {"slot_number": "A-1", "section": "Section A", "slot_type": "compact", "is_occupied": 0},
    {"slot_number": "A-2", "section": "Section A", "slot_type": "compact", "is_occupied": 0},
    {"slot_number": "A-3", "section": "Section A", "slot_type": "standard", "is_occupied": 0},
    {"slot_number": "A-4", "section": "Section A", "slot_type": "standard", "is_occupied": 0},
    {"slot_number": "A-5", "section": "Section A", "slot_type": "ev", "is_occupied": 0},
    {"slot_number": "A-6", "section": "Section A", "slot_type": "large", "is_occupied": 0},
    {"slot_number": "A-7", "section": "Section A", "slot_type": "standard", "is_occupied": 0},
    {"slot_number": "A-8", "section": "Section A", "slot_type": "compact", "is_occupied": 0},
    {"slot_number": "A-9", "section": "Section A", "slot_type": "standard", "is_occupied": 0},
    {"slot_number": "A-10", "section": "Section A", "slot_type": "standard", "is_occupied": 0},
    {"slot_number": "A-11", "section": "Section A", "slot_type": "compact", "is_occupied": 0},
    {"slot_number": "A-12", "section": "Section A", "slot_type": "ev", "is_occupied": 0},

    # Section B
    {"slot_number": "B-1", "section": "Section B", "slot_type": "compact", "is_occupied": 0},
    {"slot_number": "B-2", "section": "Section B", "slot_type": "standard", "is_occupied": 0},
    {"slot_number": "B-3", "section": "Section B", "slot_type": "large", "is_occupied": 0},
    {"slot_number": "B-4", "section": "Section B", "slot_type": "ev", "is_occupied": 0},
    {"slot_number": "B-5", "section": "Section B", "slot_type": "standard", "is_occupied": 0},
    {"slot_number": "B-6", "section": "Section B", "slot_type": "compact", "is_occupied": 0},
    {"slot_number": "B-7", "section": "Section B", "slot_type": "standard", "is_occupied": 0},
    {"slot_number": "B-8", "section": "Section B", "slot_type": "large", "is_occupied": 0},
]

# Initial completed sessions with exact boundary timestamps for testing interval filtering
INITIAL_HISTORY = [
    {
        "session_id": "SES-101",
        "slot_number": "B-2",
        "plate_number": "CA-8891",
        "vehicle_type": "sedan",
        "entry_time": "2026-10-24T08:00:00",
        "exit_time": "2026-10-24T09:00:00",
        "status": "completed",
        "fee": 5.00
    },
    {
        "session_id": "SES-102",
        "slot_number": "A-4",
        "plate_number": "NY-4421",
        "vehicle_type": "standard",
        "entry_time": "2026-10-24T09:00:00",
        "exit_time": "2026-10-24T10:30:00",
        "status": "completed",
        "fee": 7.50
    },
    {
        "session_id": "SES-103",
        "slot_number": "B-4",
        "plate_number": "EV-9901",
        "vehicle_type": "ev",
        "entry_time": "2026-10-24T10:30:00",
        "exit_time": "2026-10-24T11:45:00",
        "status": "completed",
        "fee": 8.00
    },
    {
        "session_id": "SES-104",
        "slot_number": "A-6",
        "plate_number": "TX-1188",
        "vehicle_type": "large",
        "entry_time": "2026-10-24T12:00:00",
        "exit_time": "2026-10-24T13:30:00",
        "status": "completed",
        "fee": 10.00
    },
    {
        "session_id": "SES-105",
        "slot_number": "B-8",
        "plate_number": "WA-5523",
        "vehicle_type": "large",
        "entry_time": "2026-10-24T13:30:00",
        "exit_time": "2026-10-24T15:00:00",
        "status": "completed",
        "fee": 9.00
    },
    {
        "session_id": "SES-106",
        "slot_number": "A-8",
        "plate_number": "OR-3312",
        "vehicle_type": "compact",
        "entry_time": "2026-10-24T06:30:00",
        "exit_time": "2026-10-24T07:45:00",
        "status": "completed",
        "fee": 4.50
    }
]
