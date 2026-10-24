"""
Integration API tests for ParkSmart Flask endpoints.
"""

import json
import pytest
from app import app
from backend.database import init_db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        init_db(force_reseed=True)
        yield client


def test_api_health(client):
    """Tests health endpoint."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"


def test_api_stats(client):
    """Tests stats endpoint returns correct numeric fields."""
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert "total_spaces" in data
    assert "available_spaces" in data
    assert "occupied_spaces" in data
    assert "occupancy_percentage" in data
    assert data["total_spaces"] == 20


def test_api_slots_listing(client):
    """Tests fetching slots listing with filters."""
    res = client.get("/api/slots")
    assert res.status_code == 200
    slots = res.get_json()
    assert len(slots) == 20

    # Filter by slot_type
    res_ev = client.get("/api/slots?slot_type=ev")
    assert res_ev.status_code == 200
    ev_slots = res_ev.get_json()
    assert all(s["slot_type"] == "ev" for s in ev_slots)


def test_api_vehicle_entry_validation(client):
    """Tests validation errors on vehicle entry."""
    # Missing plate
    res = client.post("/api/vehicles/entry", json={"vehicle_type": "sedan"})
    assert res.status_code == 400

    # Invalid vehicle type
    res2 = client.post("/api/vehicles/entry", json={"plate_number": "ABC-123", "vehicle_type": "airplane"})
    assert res2.status_code == 400


def test_api_duplicate_vehicle_entry(client):
    """Tests 409 Conflict when the same vehicle tries to enter twice while active."""
    entry_payload = {
        "plate_number": "TWIN-101",
        "vehicle_type": "sedan",
        "color": "Red",
        "description": "Honda Civic"
    }

    res1 = client.post("/api/vehicles/entry", json=entry_payload)
    assert res1.status_code == 201

    res2 = client.post("/api/vehicles/entry", json=entry_payload)
    assert res2.status_code == 409
    assert "already parked" in res2.get_json()["error"]


def test_api_vehicle_exit(client):
    """Tests vehicle exit endpoint."""
    # Enter a vehicle
    res_entry = client.post("/api/vehicles/entry", json={
        "plate_number": "BYE-555",
        "vehicle_type": "compact",
        "color": "Green"
    })
    assert res_entry.status_code == 201
    entry_data = res_entry.get_json()
    slot_num = entry_data["slot"]["slot_number"]

    # Exit using slot number
    res_exit = client.post("/api/vehicles/exit", json={"identifier": slot_num})
    assert res_exit.status_code == 200
    exit_data = res_exit.get_json()
    assert exit_data["session"]["status"] == "completed"

    # Second exit on same slot returns 404
    res_exit2 = client.post("/api/vehicles/exit", json={"identifier": slot_num})
    assert res_exit2.status_code == 404
