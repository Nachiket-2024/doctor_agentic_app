# ---------------------------- External Imports ----------------------------
# FastAPI HTTPException for proper error responses
from fastapi import HTTPException

# SQLAlchemy session class for DB operations
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------
# Import the Doctor model for querying doctor data
from ...models.doctor_model import Doctor

# Import the JWT helper to extract role and user ID
from ...auth.auth_user_check import AuthUserCheck

# ---------------------------- Class: GetAllDoctorsService ----------------------------
class GetAllDoctorsService:
    """
    Service class to retrieve doctors based on user role:
    - Admins and patients see all doctors.
    - Doctors see only their own record.
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self, db: Session):
        # Store the DB session instance
        self.db = db

    # ---------------------------- Method: get_all_doctors ----------------------------
    async def get_all_doctors(self, token: str) -> list[Doctor]:
        """
        Get a list of doctors based on user's role.

        Args:
            token (str): JWT token to identify user

        Returns:
            list[Doctor]: List of doctor records
        """
        try:
            # Decode the token and extract user role and ID
            _, role, user_id = AuthUserCheck.get_user_from_token(token, self.db)

            # Admins and patients can view all doctors
            if role in ("admin", "patient"):
                return self.db.query(Doctor).all()

            # Doctors can only view themselves
            elif role == "doctor":
                doctor = self.db.query(Doctor).filter(Doctor.id == user_id).first()
                if not doctor:
                    raise HTTPException(status_code=404, detail="Doctor not found")
                return [doctor]

            # If role is invalid or unauthorized
            else:
                raise HTTPException(status_code=403, detail="Unauthorized role")

        # Reraise known HTTP exceptions without masking
        except HTTPException:
            raise

        # Catch unexpected errors and return a 500 error
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
