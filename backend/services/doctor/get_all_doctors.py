# ---------------------------- External Imports ----------------------------

# FastAPI HTTPException for proper error responses
from fastapi import HTTPException

# SQLAlchemy session class for DB operations
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import the Doctor model for querying doctor data
from ...models.doctor_model import Doctor

# Import the JWT helper to extract role and user ID
from ...auth.auth_user_check import get_user_from_token

# ---------------------------- Function: Get All Doctors ----------------------------

# Async service function to retrieve doctors based on user role
async def get_all_doctors_service(
    token: str,
    db: Session
) -> list[Doctor]:
    """
    Returns a list of doctors based on the user's role:
    - Admins and patients: see all doctors.
    - Doctors: see only their own record.
    """
    try:
        # Decode the token and extract user role and ID
        _, role, user_id = get_user_from_token(token, db)

        # Admins and patients can view all doctors
        if role in ("admin", "patient"):
            return db.query(Doctor).all()

        # Doctors can only view themselves
        elif role == "doctor":
            doctor = db.query(Doctor).filter(Doctor.id == user_id).first()
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")
            return [doctor]

        # If role is invalid or unauthorized
        else:
            raise HTTPException(status_code=403, detail="Unauthorized role")

    except HTTPException:
        # Reraise known HTTP exceptions without masking
        raise

    except Exception as e:
        # Catch unexpected errors and return a 500 error
        raise HTTPException(status_code=500, detail=str(e))
