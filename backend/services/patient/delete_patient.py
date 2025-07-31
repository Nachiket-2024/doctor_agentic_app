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
from ...auth.auth_user_check import get_user_from_token

# ---------------------------- Service Function ----------------------------

# Define the async service function to delete a patient by ID
async def delete_patient_service(
    patient_id: int,      # Unique ID of the patient to delete
    token: str,           # Bearer token extracted from the request
    db: Session           # SQLAlchemy database session
) -> PatientDeleteResponse:
    """
    Delete a patient from the database if the requesting user is an admin.
    Returns a confirmation response on success.
    Raises 403 if unauthorized, or 404 if patient not found.
    """

    # Extract the user's role using the centralized auth utility
    _, role, _ = get_user_from_token(token, db)

    # Check if the user is authorized to perform deletion
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete patients")

    # Query the database to fetch the patient record by ID
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    # Raise a 404 error if no such patient exists
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Perform the deletion operation and commit the transaction
    db.delete(patient)
    db.commit()

    # Return a success response with the deleted patient's ID
    return PatientDeleteResponse(
        message="Patient deleted successfully",
        patient_id=patient_id
    )
