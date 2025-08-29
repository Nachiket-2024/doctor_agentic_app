# ---------------------------- External Imports ----------------------------
# Import HTTPException for raising standardized HTTP error responses
from fastapi import HTTPException

# Import SQLAlchemy session class to interact with the database
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------
# Import the Patient model to query patient records from the database
from ...models.patient_model import Patient

# Import schema used for returning delete confirmation response
from ...schemas.patient_schema import PatientDeleteResponse

# Import centralized JWT helper to extract user email, role, and ID
from ...auth.auth_user_check import AuthUserCheck

# ---------------------------- Class: DeletePatientService ----------------------------
class DeletePatientService:
    """
    Service class responsible for deleting a patient from the system,
    only accessible by admin users.
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self, db: Session):
        # Store the provided SQLAlchemy session
        self.db = db

    # ---------------------------- Method: delete_patient ----------------------------
    async def delete_patient(
        self,
        patient_id: int,  # Unique ID of the patient to delete
        token: str        # Bearer token extracted from the request
    ) -> PatientDeleteResponse:
        """
        Deletes a patient by ID, authorized for admin users only.

        Args:
            patient_id (int): ID of the patient to be deleted.
            token (str): Bearer token for authentication.

        Returns:
            PatientDeleteResponse: Confirmation response including deleted patient ID.
        """
        try:
            # Extract the user's role using the centralized auth utility
            _, role, _ = AuthUserCheck.get_user_from_token(token, self.db)

            # Check if the user is authorized to perform deletion
            if role != "admin":
                raise HTTPException(status_code=403, detail="Only admin can delete patients")

            # Query the database to fetch the patient record by ID
            patient = self.db.query(Patient).filter(Patient.id == patient_id).first()

            # Raise a 404 error if no such patient exists
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")

            # Perform the deletion operation and commit the transaction
            self.db.delete(patient)
            self.db.commit()

            # Return a success response with the deleted patient's ID
            return PatientDeleteResponse(
                message="Patient deleted successfully",
                patient_id=patient_id
            )

        # Let FastAPI propagate any known HTTP exceptions as-is
        except HTTPException:
            raise

        # Raise a 500 Internal Server Error for unexpected issues
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
