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
from ...auth.auth_user_check import get_user_from_token

# ---------------------------- Service Function ----------------------------

# Define an async function to handle patient creation logic
async def create_patient_service(
    patient_data: PatientCreate,  # Pydantic model containing patient creation fields
    token: str,                   # Bearer token from the request header
    db: Session                   # SQLAlchemy DB session
):
    try:
        # Validate the token and extract user identity (auth required but no role restriction)
        _, _, _ = get_user_from_token(token, db)

        # Check if a patient already exists with the same email
        existing = db.query(Patient).filter(Patient.email == patient_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Patient already exists")

        # Create a new Patient object from validated input
        new_patient = Patient(**patient_data.model_dump())

        # Add the new patient to the session
        db.add(new_patient)

        # Commit the transaction to persist changes
        db.commit()

        # Refresh to get the new patient's DB-generated fields (e.g., ID)
        db.refresh(new_patient)

        # Return the newly created patient record
        return new_patient

    # Let FastAPI propagate any known HTTP errors as-is
    except HTTPException as http_exc:
        raise http_exc

    # Catch and re-raise any unexpected server-side errors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
