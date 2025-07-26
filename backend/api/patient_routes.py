# ---------------------------- External Imports ----------------------------

# FastAPI core components for building routes, handling requests, and raising exceptions
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy session class for database operations
from sqlalchemy.orm import Session

# OAuth2 scheme for extracting bearer token from the Authorization header
from fastapi.security import OAuth2PasswordBearer

# ---------------------------- Internal Imports ----------------------------

# Import database session provider function
from ..db.session import get_db

# Utility to decode and validate JWT tokens
from ..auth.auth_utils import verify_jwt_token

# Utility to determine user role and ID based on email
from ..auth.auth_user_check import determine_user_role_and_id

# SQLAlchemy Patient model for database operations
from ..models.patient_model import Patient

# Pydantic schemas for request and response validation
from ..schemas.patient_schema import (
    PatientCreate,           # Schema used for creating a new patient
    PatientRead,             # Schema used for reading patient data
    PatientUpdate,           # Schema used for updating patient data
    PatientDeleteResponse    # Schema used as a response on successful deletion
)

# ---------------------------- OAuth2 Setup ----------------------------

# Create an instance of OAuth2PasswordBearer to extract token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------------------------- Router Setup ----------------------------

# Create a FastAPI router instance for patient-related endpoints
router = APIRouter(
    prefix="/patient",     # Route prefix for all endpoints in this router
    tags=["Patient"],      # Tag name used in API docs
)

# ---------------------------- Route: Get Patient by ID ----------------------------

@router.get("/{patient_id}", response_model=PatientRead)
async def get_patient(
    patient_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get a patient's profile by ID.
    Only the patient themselves or an admin can access the data.
    """
    try:
        # Decode and verify JWT token to extract email
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")

        # Determine the user's role and ID
        role, user_id = determine_user_role_and_id(user_email, db)

        # Fetch the patient from DB by ID
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Allow only self-access or admin access
        if role != "admin" and patient.email != user_email:
            raise HTTPException(status_code=403, detail="Access denied")

        return patient

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Create Patient ----------------------------

@router.post("/", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Create a new patient account.
    """
    try:
        # Decode JWT token to verify user
        payload = verify_jwt_token(token)
        _ = payload.get("sub")

        # Check if patient already exists
        existing = db.query(Patient).filter(Patient.email == patient.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Patient already exists")

        # Create a new patient entry
        new_patient = Patient(**patient.dict())

        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)

        return new_patient

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Update Patient ----------------------------

@router.put("/{patient_id}", response_model=PatientRead)
async def update_patient(
    patient_id: int,
    update_data: PatientUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Update a patient's details.
    Only the patient themselves or an admin can perform this action.
    """
    try:
        # Verify JWT token and extract email
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")

        # Get the user's role
        role, _ = determine_user_role_and_id(user_email, db)

        # Fetch the patient to update
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Access control: patient themselves or admin
        if role != "admin" and patient.email != user_email:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update only provided fields
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(patient, key, value)

        db.commit()
        db.refresh(patient)

        return patient

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Delete Patient ----------------------------

@router.delete("/{patient_id}", response_model=PatientDeleteResponse)
async def delete_patient(
    patient_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Delete a patient by ID.
    Only accessible to admins.
    """
    try:
        # Verify JWT token and extract email
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")

        # Check role using utility
        role, _ = determine_user_role_and_id(user_email, db)

        # Allow only admin to delete
        if role != "admin":
            raise HTTPException(status_code=403, detail="Only admin can delete patients")

        # Fetch and delete the patient
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        db.delete(patient)
        db.commit()

        return PatientDeleteResponse(
            message="Patient deleted successfully",
            patient_id=patient_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Get All Patients ----------------------------

@router.get("/", response_model=list[PatientRead])
async def get_all_patients(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get all patient records.
    Admins see all; regular patients see only their own info.
    """
    try:
        # Extract user identity from token
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")

        # Determine role of the requester
        role, user_id = determine_user_role_and_id(user_email, db)

        # Admin: return all patients
        if role == "admin":
            return db.query(Patient).all()

        # Patient: return only their own record
        patient = db.query(Patient).filter(Patient.email == user_email).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        return [patient]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
