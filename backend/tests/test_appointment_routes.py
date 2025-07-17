from fastapi.testclient import TestClient
from ..main import app
from datetime import datetime

client = TestClient(app)

# Test to check if the 'GET /appointments/' route works and returns status code 200
def test_get_appointments():
    response = client.get("/appointments/")  # Get all appointments
    assert response.status_code == 200

# Test to check if the 'POST /appointments/' route creates a new appointment and returns status code 200
def test_create_appointment():
    # First, create a doctor (simulating existing data)
    doctor_data = {
        "name": "Dr. Ahuja",
        "specialization": "Cardiologist",
        "available_days": {
            "Monday": ["09:00", "10:00"],
            "Tuesday": ["11:00", "12:00"]
        },
        "slot_duration": 30
    }
    doctor_response = client.post("/doctors/", json=doctor_data)
    doctor_id = doctor_response.json()["id"]

    # Ensure the patient has a unique email by appending a timestamp or random value
    patient_data = {
        "name": "John Doe",
        "email": f"john_{datetime.now().timestamp()}@example.com",  # Unique email
        "phone": "1234567890"
    }
    patient_response = client.post("/patients/", json=patient_data)
    patient_id = patient_response.json()["id"]

    # Now, create an appointment
    appointment_data = {
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "date": "2025-07-20",
        "start_time": "09:00",
        "end_time": "09:30",
        "status": "scheduled",
        "reason": "Routine check-up"
    }
    response = client.post("/appointments/", json=appointment_data)
    assert response.status_code == 200
    assert response.json()["doctor_id"] == doctor_id
    assert response.json()["patient_id"] == patient_id
    assert response.json()["status"] == "scheduled"

# Test to check if the 'GET /appointments/{appointment_id}' route works and returns appointment by ID
def test_get_appointment():
    # First, create a doctor and a patient (to simulate existing data)
    doctor_data = {
        "name": "Dr. Ahuja",
        "specialization": "Cardiologist",
        "available_days": {
            "Monday": ["09:00", "10:00"],
            "Tuesday": ["11:00", "12:00"]
        },
        "slot_duration": 30
    }
    doctor_response = client.post("/doctors/", json=doctor_data)
    doctor_id = doctor_response.json()["id"]

    patient_data = {
        "name": "John Doe",
        "email": f"john_{datetime.now().timestamp()}@example.com",  # Unique email
        "phone": "1234567890"
    }
    patient_response = client.post("/patients/", json=patient_data)
    patient_id = patient_response.json()["id"]

    # Now, create an appointment
    appointment_data = {
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "date": "2025-07-20",
        "start_time": "09:00",
        "end_time": "09:30",
        "status": "scheduled",
        "reason": "Routine check-up"
    }
    appointment_response = client.post("/appointments/", json=appointment_data)
    appointment_id = appointment_response.json()["id"]

    # Get the appointment by ID
    response = client.get(f"/appointments/{appointment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == appointment_id
    assert response.json()["status"] == "scheduled"
    assert response.json()["reason"] == "Routine check-up"

# Test to check if the 'PUT /appointments/{appointment_id}' route updates an appointment and returns status code 200
def test_update_appointment():
    # First, create a doctor and a patient (to simulate existing data)
    doctor_data = {
        "name": "Dr. Ahuja",
        "specialization": "Cardiologist",
        "available_days": {
            "Monday": ["09:00", "10:00"],
            "Tuesday": ["11:00", "12:00"]
        },
        "slot_duration": 30
    }
    doctor_response = client.post("/doctors/", json=doctor_data)
    doctor_id = doctor_response.json()["id"]

    patient_data = {
        "name": "John Doe",
        "email": f"john_{datetime.now().timestamp()}@example.com",  # Unique email
        "phone": "1234567890"
    }
    patient_response = client.post("/patients/", json=patient_data)
    patient_id = patient_response.json()["id"]

    # Now, create an appointment
    appointment_data = {
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "date": "2025-07-20",
        "start_time": "09:00",
        "end_time": "09:30",
        "status": "scheduled",
        "reason": "Routine check-up"
    }
    appointment_response = client.post("/appointments/", json=appointment_data)
    appointment_id = appointment_response.json()["id"]

    # Now update the appointment
    update_data = {
        "status": "completed",
        "reason": "Follow-up check-up"
    }

    response = client.put(f"/appointments/{appointment_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["reason"] == "Follow-up check-up"

# Test to check if the 'DELETE /appointments/{appointment_id}' route deletes an appointment and returns status code 200
def test_delete_appointment():
    # First, create a doctor and a patient (to simulate existing data)
    doctor_data = {
        "name": "Dr. Ahuja",
        "specialization": "Cardiologist",
        "available_days": {
            "Monday": ["09:00", "10:00"],
            "Tuesday": ["11:00", "12:00"]
        },
        "slot_duration": 30
    }
    doctor_response = client.post("/doctors/", json=doctor_data)
    doctor_id = doctor_response.json()["id"]

    patient_data = {
        "name": "John Doe",
        "email": f"john_{datetime.now().timestamp()}@example.com",  # Unique email
        "phone": "1234567890"
    }
    patient_response = client.post("/patients/", json=patient_data)
    patient_id = patient_response.json()["id"]

    # Now, create an appointment
    appointment_data = {
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "date": "2025-07-20",
        "start_time": "09:00",
        "end_time": "09:30",
        "status": "scheduled",
        "reason": "Routine check-up"
    }
    appointment_response = client.post("/appointments/", json=appointment_data)
    appointment_id = appointment_response.json()["id"]

    # Now delete the appointment
    response = client.delete(f"/appointments/{appointment_id}")
    assert response.status_code == 200
    assert response.json() == {"detail": "Appointment deleted"}
