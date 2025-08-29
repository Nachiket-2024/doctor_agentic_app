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
from ...auth.auth_user_check import AuthUserCheck

# Slot generation utility to compute weekly slots from available_days
from ...utils.slot_availability_utils import SlotAvailabilityUtils

# ---------------------------- Class: CreateDoctorService ----------------------------
class CreateDoctorService:
    """
    Service class to handle the creation of new doctor entries.
    Only accessible to admin users.
    """

    # Constructor to receive DB session
    def __init__(self, db: Session):
        # Store the DB session
        self.db = db

    # ---------------------------- Method: create_doctor ----------------------------
    async def create_doctor(self, doctor: DoctorCreate, token: str):
        """
        Create a new doctor entry in the system.

        Args:
            doctor (DoctorCreate): Input data for the doctor
            token (str): JWT token for authentication

        Returns:
            Doctor: The created doctor ORM object

        Raises:
            HTTPException: On permission error or server error
        """
        try:
            # Validate token and extract role
            _, role, _ = AuthUserCheck.get_user_from_token(token, self.db)

            # Ensure only admins can create doctors
            if role != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")

            # Create new Doctor object from Pydantic schema
            new_doctor = Doctor(**doctor.model_dump())

            # Generate slots from availability days and slot duration
            new_doctor.weekly_available_slots = SlotAvailabilityUtils.generate_all_weekly_slots(
                new_doctor.available_days,
                new_doctor.slot_duration
            )

            # Add and persist doctor to DB
            self.db.add(new_doctor)
            self.db.commit()
            self.db.refresh(new_doctor)

            # Return the created doctor
            return new_doctor

        # Re-raise known HTTP errors
        except HTTPException:
            raise

        # Handle unexpected exceptions
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
