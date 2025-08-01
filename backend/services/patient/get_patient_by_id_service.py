# ---------------------------- External Imports ----------------------------

# Import HTTPException for returning API error responses
from fastapi import HTTPException

# Import Session class to interact with the database
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import the Patient ORM model for database queries
from ...models.patient_model import Patient

# Import centralized token decoder utility
from ...auth.auth_user_check import AuthUserCheck

# ---------------------------- Class: GetPatientByIDService ----------------------------

class GetPatientByIDService:
    """
    Service to fetch a patient by ID with role-based access control.
    Only the patient or an admin is allowed to access this data.
    """

    # ---------------------------- Constructor ----------------------------

    def __init__(self, db: Session):
        # Store the database session for reuse
        self.db = db

    # ---------------------------- Method: get_patient_by_id ----------------------------

    async def get_patient_by_id(self, patient_id: int, token: str):
        """
        Retrieve patient information by ID with role-based authorization.

        Args:
            patient_id (int): ID of the patient to retrieve.
            token (str): JWT token for identifying the requester.

        Returns:
            Patient: The patient record if access is authorized.
        """
        try:
            # Extract the user's email and role from the JWT token
            user_email, role, _ = AuthUserCheck.get_user_from_token(token, self.db)

            # Query the database for the patient with the given ID
            patient = self.db.query(Patient).filter(Patient.id == patient_id).first()

            # If patient is not found, raise a 404 error
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")

            # If the user is not an admin and not the owner of the data, deny access
            if role != "admin" and patient.email != user_email:
                raise HTTPException(status_code=403, detail="Access denied")

            # Return the patient record if access is permitted
            return patient

        # Reraise HTTP exceptions without modification
        except HTTPException as http_exc:
            raise http_exc

        # Catch any unexpected errors and raise as 500 Internal Server Error
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
