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
from ...auth.auth_user_check import AuthUserCheck

# Import utility to regenerate slots if availability changes
from ...utils.slot_availability_utils import SlotAvailabilityUtils

# ---------------------------- Class: UpdateDoctorService ----------------------------
class UpdateDoctorService:
    """
    Service class to handle updating doctor details.
    Only accessible to users with admin privileges.
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self, db: Session):
        # Store DB session for instance-level access
        self.db = db

    # ---------------------------- Method: update_doctor ----------------------------
    async def update_doctor(
        self,
        doctor_id: int,
        updated_doctor: DoctorUpdate,
        token: str
    ) -> Doctor:
        """
        Update an existing doctor in the system.
        Only admins can perform this action.

        Args:
            doctor_id (int): The ID of the doctor to update.
            updated_doctor (DoctorUpdate): Fields to be updated.
            token (str): JWT for authentication.

        Returns:
            Doctor: The updated doctor object.
        """
        try:
            # Decode the token and extract role
            _, role, _ = AuthUserCheck.get_user_from_token(token, self.db)

            # Restrict access to admin only
            if role != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")

            # Fetch the doctor to be updated
            doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()

            # Raise 404 if doctor is not found
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")

            # Save previous values to check if slots need to be regenerated
            old_available_days = doctor.available_days
            old_slot_duration = doctor.slot_duration

            # Get only the fields provided in the update request
            update_data = updated_doctor.model_dump(exclude_unset=True)

            # Update doctor object dynamically
            for key, value in update_data.items():
                setattr(doctor, key, value)

            # Regenerate weekly slots if availability or duration changed
            if (
                ("available_days" in update_data and doctor.available_days != old_available_days) or
                ("slot_duration" in update_data and doctor.slot_duration != old_slot_duration)
            ):
                doctor.weekly_available_slots = SlotAvailabilityUtils.generate_all_weekly_slots(
                    doctor.available_days,
                    doctor.slot_duration
                )

            # Commit the changes to the database
            self.db.commit()
            self.db.refresh(doctor)

            # Return the updated doctor object
            return doctor

        # Propagate FastAPI-specific exceptions
        except HTTPException:
            raise

        # Handle and log unexpected server errors
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
