# ---------------------------- External Imports ----------------------------

# Import HTTPException for API error handling
from fastapi import HTTPException

# Import SQLAlchemy Session type hint
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import Doctor ORM model
from ...models.doctor_model import Doctor

# Centralized auth helper to validate JWT and extract user info
from ...auth.auth_user_check import get_user_from_token

# ---------------------------- Function: Get Doctor by ID ----------------------------

# Define an asynchronous function to retrieve a doctor by ID
async def get_doctor_by_id_service(doctor_id: int, token: str, db: Session):
    """
    Retrieve a doctor by their unique ID.
    """
    try:
        # Validate token (even if user info isn't used)
        _ = get_user_from_token(token, db)

        # Fetch the doctor record from the database
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

        # Raise 404 if doctor not found
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Return the doctor object
        return doctor

    except HTTPException:
        # Propagate known HTTP errors directly
        raise

    except Exception as e:
        # Raise a generic server error on unexpected issues
        raise HTTPException(status_code=500, detail=str(e))
