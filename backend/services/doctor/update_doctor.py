# ---------------------------- External Imports ----------------------------

# Import HTTPException for raising API-related errors
from fastapi import HTTPException

# Import Session type for type hinting the database session
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import the Doctor ORM model
from ...models.doctor_model import Doctor

# Import Pydantic schema for doctor update
from ...schemas.doctor_schema import DoctorUpdate

# Import utility for checking and decoding token
from ...auth.auth_user_check import get_user_from_token

# Import utility to regenerate slots if availability changes
from ...utils.generate_available_slots import generate_all_weekly_slots

# ---------------------------- Function: Update Doctor ----------------------------

# Define the async service function to update a doctor's information
async def update_doctor_service(
    doctor_id: int,
    updated_doctor: DoctorUpdate,
    token: str,
    db: Session
):
    """
    Update an existing doctor (Admin only).
    """
    try:
        # Decode the token and extract the role
        _, role, _ = get_user_from_token(token, db)

        # Check that only admin is authorized to update
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Fetch the doctor to update
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

        # Return 404 if the doctor doesn't exist
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Store the old availability and slot duration before update
        old_available_days = doctor.available_days
        old_slot_duration = doctor.slot_duration

        # Unpack only fields that were actually sent in the request
        update_data = updated_doctor.model_dump(exclude_unset=True)

        # Update the fields dynamically using setattr
        for key, value in update_data.items():
            setattr(doctor, key, value)

        # Recalculate slots only if relevant fields changed
        if (
            ("available_days" in update_data and doctor.available_days != old_available_days)
            or ("slot_duration" in update_data and doctor.slot_duration != old_slot_duration)
        ):
            doctor.weekly_available_slots = generate_all_weekly_slots(
                doctor.available_days,
                doctor.slot_duration
            )

        # Persist changes to the database
        db.commit()
        db.refresh(doctor)

        # Return the updated doctor
        return doctor

    except HTTPException:
        # Pass through any known FastAPI exceptions
        raise

    except Exception as e:
        # Raise internal server error for any unknown exceptions
        raise HTTPException(status_code=500, detail=str(e))
