# ---------------------------- External Imports ----------------------------

# Import HTTPException for raising errors in response
from fastapi import HTTPException

# SQLAlchemy session for interacting with the database
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import Patient model for querying and updating patient records
from ...models.patient_model import Patient

# Import the schema used for validating update data
from ...schemas.patient_schema import PatientUpdate

# Utility to extract authenticated user info from token
from ...auth.auth_user_check import get_user_from_token

# ---------------------------- Service Function ----------------------------

# Async function to update a patient's record
async def update_patient_service(
    patient_id: int,                   # ID of the patient to update
    update_data: PatientUpdate,       # Fields to be updated
    token: str,                       # JWT token from request
    db: Session                       # Active database session
):
    # Extract email and role from the token
    user_email, role, _ = get_user_from_token(token, db)

    # Query the database for the patient with the specified ID
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    # If no patient is found, raise a 404 error
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # If the user is not an admin and not the patient themselves, deny access
    if role != "admin" and patient.email != user_email:
        raise HTTPException(status_code=403, detail="Access denied")

    # Loop through each field to be updated and apply the changes to the patient object
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)

    # Commit the changes to the database
    db.commit()

    # Refresh the patient instance to reflect the updated state
    db.refresh(patient)

    # Return the updated patient object
    return patient
