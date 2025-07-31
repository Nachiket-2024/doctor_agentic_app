# ---------------------------- External Imports ----------------------------

# Import HTTPException for returning API error responses
from fastapi import HTTPException

# Import Session class to interact with the database
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import the Patient ORM model for database queries
from ...models.patient_model import Patient

# Import centralized token decoder utility
from ...auth.auth_user_check import get_user_from_token

# ---------------------------- Service Function ----------------------------

# Define an async function to fetch a patient by ID with role-based access control
async def get_patient_by_id_service(patient_id: int, token: str, db: Session):
    """
    Fetch patient details by ID.
    Only the patient themselves or an admin can access this data.
    """
    try:
        # Extract the user's email and role from the JWT token
        user_email, role, _ = get_user_from_token(token, db)

        # Query the database for the patient with the given ID
        patient = db.query(Patient).filter(Patient.id == patient_id).first()

        # If patient is not found, raise a 404 error
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # If the user is not an admin and not the owner of the data, deny access
        if role != "admin" and patient.email != user_email:
            raise HTTPException(status_code=403, detail="Access denied")

        # Return the patient record if access is permitted
        return patient

    # Reraise HTTP exceptions without modification
    except HTTPException as http_exc:
        raise http_exc

    # Catch any unexpected errors and raise as 500 Internal Server Error
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
