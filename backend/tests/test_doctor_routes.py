from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

# Test to check if the 'GET /doctors/' route works and returns status code 200
def test_get_doctors():
    response = client.get("/doctors/")  # Changed from /doctor/ to /doctors/ to match the route
    # Assert the response status code is 200 (OK)
    assert response.status_code == 200

# Test to check if the 'POST /doctors/' route creates a new doctor and returns status code 200
def test_create_doctor():
    doctor_data = {
        "name": "Dr. Ahuja",
        "specialization": "Cardiologist",
        "available_days": {
            "Monday": ["09:00", "10:00"],
            "Tuesday": ["11:00", "12:00"]
        },
        "slot_duration": 30
    }
    response = client.post("/doctors/", json=doctor_data)
    print("RESPONSE JSON:", response.json())  # Optional: print this if still debugging
    assert response.status_code == 200
    assert response.json()["name"] == "Dr. Ahuja"
    assert response.json()["specialization"] == "Cardiologist"

# Test to check if the 'GET /doctors/{id}' route works and returns a doctor by ID
def test_get_doctor():
    doctor_data = {
        "name": "Dr. Ahuja",
        "specialization": "Cardiologist",
        "available_days": {
            "Monday": ["09:00", "10:00"],
            "Tuesday": ["11:00", "12:00"]
        },
        "slot_duration": 30
    }
    response = client.post("/doctors/", json=doctor_data)
    doctor_id = response.json()["id"]

    # Now get the doctor by ID
    response = client.get(f"/doctors/{doctor_id}")
    assert response.status_code == 200
    assert response.json()["id"] == doctor_id
    assert response.json()["name"] == "Dr. Ahuja"
    assert response.json()["specialization"] == "Cardiologist"

# Test to check if the 'PUT /doctors/{id}' route updates a doctor and returns status code 200
def test_update_doctor():
    doctor_data = {
        "name": "Dr. Ahuja",
        "specialization": "Cardiologist",
        "available_days": {
            "Monday": ["09:00", "10:00"],
            "Tuesday": ["11:00", "12:00"]
        },
        "slot_duration": 30
    }
    response = client.post("/doctors/", json=doctor_data)
    doctor_id = response.json()["id"]

    # Update the doctor's information
    update_data = {
        "name": "Dr. Ahuja Updated",
        "specialization": "Neurologist",
        "available_days": {
            "Monday": ["09:00", "10:00"]
        },
        "slot_duration": 45
    }

    response = client.put(f"/doctors/{doctor_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Dr. Ahuja Updated"
    assert response.json()["specialization"] == "Neurologist"

# Test to check if the 'DELETE /doctors/{id}' route deletes a doctor and returns status code 200
def test_delete_doctor():
    doctor_data = {
        "name": "Dr. Ahuja",
        "specialization": "Cardiologist",
        "available_days": {
            "Monday": ["09:00", "10:00"],
            "Tuesday": ["11:00", "12:00"]
        },
        "slot_duration": 30
    }
    response = client.post("/doctors/", json=doctor_data)
    doctor_id = response.json()["id"]

    # Now delete the doctor by ID
    response = client.delete(f"/doctors/{doctor_id}")
    assert response.status_code == 200
    assert response.json() == {"detail": "Doctor deleted"}

# Test to check if the 'GET /doctors/{id}/availability' route returns available slots for a specific date
def test_get_doctor_availability():
    doctor_data = {
        "name": "Dr. Ahuja",
        "specialization": "Cardiologist",
        "available_days": {
            "Monday": ["09:00", "10:00"],
            "Tuesday": ["11:00", "12:00"]
        },
        "slot_duration": 30
    }
    response = client.post("/doctors/", json=doctor_data)
    doctor_id = response.json()["id"]

    # Get the doctor's availability for a specific date
    response = client.get(f"/doctors/{doctor_id}/availability?date=2025-07-17")
    assert response.status_code == 200
    assert "available_slots" in response.json()
