# ---------------------------- External Imports ----------------------------

# Import FastAPI HTTP exception handler
from fastapi import HTTPException

# Import SQLAlchemy Session for DB operations
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import the Doctor ORM model
from ...models.doctor_model import Doctor

# Import the Pydantic response schema
from ...schemas.doctor_schema import DoctorDeleteResponse

# Import the helper function to decode JWT and extract user role
from ...auth.auth_user_check import get_user_from_token

# ---------------------------- Function: Delete Doctor ----------------------------

# Async service to delete a doctor by ID (admin only)
async def delete_doctor_service(
    doctor_id: int,
    token: str,
    db: Session
) -> DoctorDeleteResponse:
    """
    Deletes a doctor from the system. Only accessible to admin users.
    """
    try:
        # Decode the JWT token and get the user's role
        _, role, _ = get_user_from_token(token, db)

        # Only admin users are allowed to delete doctors
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Fetch the doctor from the DB by ID
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

        # Raise 404 if doctor doesn't exist
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Delete the doctor from the DB
        db.delete(doctor)
        db.commit()

        # Return a success response with doctor ID
        return DoctorDeleteResponse(
            message="Doctor deleted successfully",
            doctor_id=doctor_id
        )

    except HTTPException:
        # Re-raise known HTTP exceptions
        raise

    except Exception as e:
        # Catch unexpected errors and raise internal server error
        raise HTTPException(status_code=500, detail=str(e))
