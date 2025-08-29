# ---------------------------- External Imports ----------------------------
# Import HTTPException for raising API errors
from fastapi import HTTPException

# Import SQLAlchemy session for database operations
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------
# Import the Patient SQLAlchemy model
from ...models.patient_model import Patient

# Import the schema used to validate patient creation requests
from ...schemas.patient_schema import PatientCreate

# Import centralized auth function to extract identity from JWT token
from ...auth.auth_user_check import AuthUserCheck

# ---------------------------- Class: CreatePatientService ----------------------------
class CreatePatientService:
    """
    Service class to handle logic related to creating a new patient.
    """

    # ---------------------------- Constructor ----------------------------
    def __init__(self, db: Session):
        # Store the provided SQLAlchemy session
        self.db = db

    # ---------------------------- Method: create_patient ----------------------------
    async def create_patient(
        self,
        patient_data: PatientCreate,  # Pydantic model containing patient creation fields
        token: str                    # Bearer token from the request header
    ):
        """
        Create a new patient if they don't already exist.
        """
        try:
            # Validate the token and extract user identity (auth required but no role restriction)
            _, _, _ = AuthUserCheck.get_user_from_token(token, self.db)

            # Check if a patient already exists with the same email
            existing = self.db.query(Patient).filter(Patient.email == patient_data.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Patient already exists")

            # Create a new Patient object from validated input
            new_patient = Patient(**patient_data.model_dump())

            # Add the new patient to the session
            self.db.add(new_patient)

            # Commit the transaction to persist changes
            self.db.commit()

            # Refresh to get the new patient's DB-generated fields (e.g., ID)
            self.db.refresh(new_patient)

            # Return the newly created patient record
            return new_patient

        # Let FastAPI propagate any known HTTP errors as-is
        except HTTPException as http_exc:
            raise http_exc

        # Catch and re-raise any unexpected server-side errors
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
