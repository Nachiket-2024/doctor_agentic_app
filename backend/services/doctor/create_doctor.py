# ---------------------------- External Imports ----------------------------

# Import HTTPException for error handling
from fastapi import HTTPException

# Import Session type from SQLAlchemy
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import Doctor ORM model
from ...models.doctor_model import Doctor

# Import Pydantic schema for doctor creation
from ...schemas.doctor_schema import DoctorCreate

# JWT utility to extract user identity and role
from ...auth.auth_user_check import get_user_from_token

# Slot generation utility to compute weekly slots from available_days
from ...utils.generate_available_slots import generate_all_weekly_slots

# ---------------------------- Function: Create Doctor ----------------------------

# Define an asynchronous service function to create a doctor
async def create_doctor_service(doctor: DoctorCreate, token: str, db: Session):
    """
    Create a new doctor (Admin only).
    """
    try:
        # Validate token and extract role
        _, role, _ = get_user_from_token(token, db)

        # Ensure only admins can create doctors
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Create a new Doctor ORM instance from the Pydantic schema
        new_doctor = Doctor(**doctor.model_dump())

        # Automatically generate weekly slots based on days and duration
        new_doctor.weekly_available_slots = generate_all_weekly_slots(
            new_doctor.available_days,
            new_doctor.slot_duration
        )

        # Add the new doctor to the database
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)

        # Return the newly created doctor object
        return new_doctor

    except HTTPException:
        # Re-raise known HTTP errors
        raise

    except Exception as e:
        # Raise internal server error for unhandled exceptions
        raise HTTPException(status_code=500, detail=str(e))
