# ---------------------------- External Imports ----------------------------

# Import HTTPException for API error handling
from fastapi import HTTPException

# Import SQLAlchemy Session type hint
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import Doctor ORM model
from ...models.doctor_model import Doctor

# Centralized auth helper to validate JWT and extract user info
from ...auth.auth_user_check import AuthUserCheck

# ---------------------------- Class: GetDoctorByIdService ----------------------------

class GetDoctorByIdService:
    """
    Service class to retrieve a doctor by ID. Token validation is enforced,
    but user role is not restricted for this operation.
    """

    # ---------------------------- Constructor ----------------------------

    def __init__(self, db: Session):
        # Store the DB session for use in the method
        self.db = db

    # ---------------------------- Method: get_doctor_by_id ----------------------------

    async def get_doctor_by_id(self, doctor_id: int, token: str) -> Doctor:
        """
        Retrieve a doctor from the database by ID.

        Args:
            doctor_id (int): ID of the doctor to retrieve
            token (str): JWT token to validate access

        Returns:
            Doctor: The doctor object if found
        """
        try:
            # Validate token (user role isn't required for this call)
            _ = AuthUserCheck.get_user_from_token(token, self.db)

            # Fetch doctor from DB by ID
            doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()

            # Raise error if doctor is not found
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")

            # Return the doctor object
            return doctor

        # Re-raise known HTTP exceptions
        except HTTPException:
            raise

        # Handle and rethrow unexpected server errors
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
