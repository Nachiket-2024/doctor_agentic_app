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
from ...auth.auth_user_check import AuthUserCheck

# ---------------------------- Class: DeleteDoctorService ----------------------------

class DeleteDoctorService:
    """
    Service class to handle doctor deletion logic.
    Only accessible to admin users.
    """

    # Constructor accepts a DB session
    def __init__(self, db: Session):
        # Store the DB session instance
        self.db = db

    # ---------------------------- Method: delete_doctor ----------------------------

    async def delete_doctor(self, doctor_id: int, token: str) -> DoctorDeleteResponse:
        """
        Delete a doctor from the database.

        Args:
            doctor_id (int): ID of the doctor to be deleted
            token (str): Auth token to verify admin access

        Returns:
            DoctorDeleteResponse: Success message and doctor ID

        Raises:
            HTTPException: On unauthorized access or server error
        """
        try:
            # Decode the JWT token and get the user's role
            _, role, _ = AuthUserCheck.get_user_from_token(token, self.db)

            # Only admin users are allowed to delete doctors
            if role != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")

            # Fetch the doctor from the DB by ID
            doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()

            # Raise 404 if doctor doesn't exist
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")

            # Delete the doctor from the DB
            self.db.delete(doctor)
            self.db.commit()

            # Return a success response with doctor ID
            return DoctorDeleteResponse(
                message="Doctor deleted successfully",
                doctor_id=doctor_id
            )

        # Re-raise known HTTP exceptions
        except HTTPException:
            raise

        # Catch unexpected errors and raise internal server error
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
