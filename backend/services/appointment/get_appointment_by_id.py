# ---------------------------- External Imports ----------------------------

# Exception class for HTTP error responses
from fastapi import HTTPException

# SQLAlchemy ORM Session for DB interactions
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Appointment model from SQLAlchemy
from ...models.appointment_model import Appointment

# Utility to extract user info from token
from ...auth.auth_user_check import get_user_from_token

# ---------------------------- Function: Get Appointment by ID ----------------------------

# Get appointment by ID with access check (used by both API and LLM agent)
async def get_appointment_by_id(appointment_id: int, token: str, db: Session):
    # Extract user info (email, role, ID) from the access token
    _, user_role, user_id = get_user_from_token(token, db)

    # Fetch the appointment from the database using the given ID
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    # Raise error if the appointment does not exist
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Return the appointment if the user is authorized (admin, owner doctor, or owner patient)
    if user_role == "admin" or \
       (user_role == "doctor" and appointment.doctor_id == user_id) or \
       (user_role == "patient" and appointment.patient_id == user_id):
        return appointment

    # Raise an error if the user is not authorized to view this appointment
    raise HTTPException(status_code=403, detail="You are not authorized to view this appointment")
