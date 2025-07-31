# ---------------------------- External Imports ----------------------------

# Exception class for HTTP errors
from fastapi import HTTPException

# SQLAlchemy session type
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# SQLAlchemy model for Appointment
from ...models.appointment_model import Appointment

# Auth utility to extract user info from token
from ...auth.auth_user_check import get_user_from_token

# ---------------------------- Function: Get All Appointments ----------------------------

# Return all appointments based on the role of the authenticated user
async def get_all_appointments_entry(token: str, db: Session):
    try:
        # Decode the token to extract user role and ID
        _, user_role, user_id = get_user_from_token(token, db)

        # If user is admin, return all appointments
        if user_role == "admin":
            return db.query(Appointment).all()

        # If user is a doctor, return appointments for that doctor
        elif user_role == "doctor":
            return db.query(Appointment).filter(Appointment.doctor_id == user_id).all()

        # If user is a patient, return appointments for that patient
        elif user_role == "patient":
            return db.query(Appointment).filter(Appointment.patient_id == user_id).all()

        # Raise 403 for any other role
        else:
            raise HTTPException(status_code=403, detail="Not authorized to view appointments.")
    
    # Re-raise HTTPExceptions as-is
    except HTTPException as http_exc:
        raise http_exc
    
    # Handle other unexpected errors with a 500 error
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
