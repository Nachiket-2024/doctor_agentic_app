# ---------------------------- External Imports ----------------------------
# Import HTTPException to handle error responses
from fastapi import HTTPException

# Import SQLAlchemy Session for database operations
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------
# Import the Patient SQLAlchemy model
from ...models.patient_model import Patient

# Import the centralized auth utility to extract user info from token
from ...auth.auth_user_check import AuthUserCheck

# ---------------------------- Class: GetAllPatientsService ----------------------------
class GetAllPatientsService:
    """
    Service to retrieve patient records based on user role.
    Admins see all patients, while patients see only their own profile.
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self, db: Session):
        # Store the provided database session
        self.db = db

    # ---------------------------- Method: get_all_patients ----------------------------
    async def get_all_patients(self, token: str):
        """
        Retrieve patient records based on the user's role.

        Args:
            token (str): Bearer token containing user credentials.

        Returns:
            list[Patient]: A list of patient records.
        """
        try:
            # Extract the user's email and role from the JWT token
            user_email, role, _ = AuthUserCheck.get_user_from_token(token, self.db)

            # If user is an admin, return all patients in the database
            if role == "admin":
                return self.db.query(Patient).all()

            # If the user is a patient, return only their own profile
            patient = self.db.query(Patient).filter(Patient.email == user_email).first()

            # If no matching patient is found, raise a 404 error
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")

            # Return the single patient in a list to match the expected format
            return [patient]

        # Re-raise any known HTTP exceptions
        except HTTPException as http_exc:
            raise http_exc

        # Handle unexpected exceptions with a generic 500 response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
