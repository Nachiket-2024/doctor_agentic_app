from fastapi.testclient import TestClient
from ..main import app
import uuid

client = TestClient(app)

# Helper function to generate a unique email for each test
def generate_unique_email():
    return f"john.doe{uuid.uuid4().hex[:8]}@example.com"

# Test to check if the 'GET /patients/' route works and returns status code 200
def test_get_patients():
    response = client.get("/patients/")
    assert response.status_code == 200

# Test to check if the 'POST /patients/' route creates a new patient and returns status code 200
def test_create_patient():
    patient_email = generate_unique_email()  # Create a unique email for this test
    patient_data = {
        "name": "John Doe",
        "email": patient_email,
        "phone": "1234567890"
    }
    response = client.post("/patients/", json=patient_data)
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"
    assert response.json()["email"] == patient_data["email"]

# Test to check if the 'GET /patients/{id}' route works and returns a patient by ID
def test_get_patient():
    patient_email = generate_unique_email()  # Create a unique email for this test
    patient_data = {
        "name": "John Doe",
        "email": patient_email,
        "phone": "1234567890"
    }
    response = client.post("/patients/", json=patient_data)
    patient_id = response.json()["id"]

    # Now get the patient by ID
    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 200
    assert response.json()["id"] == patient_id
    assert response.json()["name"] == "John Doe"
    assert response.json()["email"] == patient_data["email"]

# Test to check if the 'PUT /patients/{id}' route updates a patient and returns status code 200
def test_update_patient():
    patient_email = generate_unique_email()  # Create a unique email for the creation
    patient_data = {
        "name": "John Doe",
        "email": patient_email,
        "phone": "1234567890"
    }
    # Create the patient first
    response = client.post("/patients/", json=patient_data)
    patient_id = response.json()["id"]

    # Update the patient's info (use the same email)
    update_data = {
        "name": "John Doe Updated",
        "email": patient_email,  # Same email
        "phone": "9876543210"
    }
    response = client.put(f"/patients/{patient_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe Updated"
    assert response.json()["email"] == patient_email  # Ensure the email stays the same

# Test to check if the 'DELETE /patients/{id}' route deletes a patient and returns status code 200
def test_delete_patient():
    patient_email = generate_unique_email()  # Create a unique email for the creation
    patient_data = {
        "name": "John Doe",
        "email": patient_email,
        "phone": "1234567890"
    }
    # Create the patient first
    response = client.post("/patients/", json=patient_data)
    patient_id = response.json()["id"]

    # Now delete the patient by ID
    response = client.delete(f"/patients/{patient_id}")
    assert response.status_code == 200
    assert response.json() == {"detail": "Patient deleted"}
