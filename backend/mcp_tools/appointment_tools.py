import requests
from fastapi import HTTPException, Depends
from fastapi import Cookie


# Base URL for your FastAPI backend
BASE_URL = "http://localhost:8000"

# Function to get current user from cookies using the auth method from auth_routes.py
from ..auth.auth_routes import get_current_user_from_cookie

# Function to check availability for a doctor (use this in MCP)
def check_doctor_availability(
    doctor_id: int,
    date: str,
    cookies: dict[str, str]  # Ensure cookies are passed to authenticate the current user
) -> list[str]:
    """
    Calls the FastAPI endpoint to check the doctor's availability.
    Returns a list of available slots for the doctor.
    """
    url = f"{BASE_URL}/doctors/{doctor_id}/availability?date={date}"
    response = requests.get(url, cookies=cookies)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch availability")
    
    return response.json()


# Function to create an appointment (use this in MCP)
def create_appointment(
    appointment_data: dict,
    cookies: dict[str, str]
) -> dict:
    """
    Calls the FastAPI endpoint to create an appointment.
    Uses the cookies to authenticate the user making the request.
    """
    # Get the current user to verify if they have permission
    current_user = get_current_user_from_cookie(cookies=cookies)

    # Ensure the user has permission to create appointments (for themselves or admin)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    if current_user.role != "patient" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only patients or admins can create appointments")

    # Proceed with appointment creation by sending a request to FastAPI
    url = f"{BASE_URL}/appointments/"
    response = requests.post(url, json=appointment_data, cookies=cookies)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to create appointment")

    return response.json()
