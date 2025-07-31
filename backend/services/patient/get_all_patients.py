# ---------------------------- External Imports ----------------------------

# Import HTTPException to handle error responses
from fastapi import HTTPException

# Import SQLAlchemy Session for database operations
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import the Patient SQLAlchemy model
from ...models.patient_model import Patient

# Import the centralized auth utility to extract user info from token
from ...auth.auth_user_check import get_user_from_token

# ---------------------------- Service: Get All Patients ----------------------------

# Define an async function to retrieve all patients
async def get_all_patients_service(token: str, db: Session):
    """
    Get all patient records based on the user's role.
    Admins can see all patients. Regular patients only see their own profile.
    """

    try:
        # Extract the user's email and role from the JWT token
        user_email, role, _ = get_user_from_token(token, db)

        # If user is an admin, return all patients in the database
        if role == "admin":
            return db.query(Patient).all()

        # If the user is a patient, return only their own profile
        patient = db.query(Patient).filter(Patient.email == user_email).first()

        # If no matching patient is found, raise a 404 error
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Return the single patient in a list to match the expected response format
        return [patient]

    # Re-raise any known HTTP exceptions
    except HTTPException as http_exc:
        raise http_exc

    # Handle unexpected exceptions with a generic 500 response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
