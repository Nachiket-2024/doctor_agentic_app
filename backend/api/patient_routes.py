# ---------------------------- External Imports ----------------------------

# FastAPI core components for building routes, handling requests, and raising exceptions
from fastapi import APIRouter, Depends, status

# SQLAlchemy session class for database operations
from sqlalchemy.orm import Session

# OAuth2 scheme for extracting bearer token from the Authorization header
from fastapi.security import OAuth2PasswordBearer

# ---------------------------- Internal Imports ----------------------------

# Import database session provider function
from ..db.session import get_db

# Pydantic schemas for request and response validation
from ..schemas.patient_schema import (
    PatientCreate,           # Schema used for creating a new patient
    PatientRead,             # Schema used for reading patient data
    PatientUpdate,           # Schema used for updating patient data
    PatientDeleteResponse    # Schema used as a response on successful deletion
)

# Import the modularized service function to get a patient by ID
from ..services.patient.get_patient_by_id import get_patient_by_id_service

# Import the modularized service function to create a new patient
from ..services.patient.create_patient import create_patient_service

# Import the modularized update service function to update patient data
from ..services.patient.update_patient import update_patient_service

# Import the modularized delete service function to delete a patient
from ..services.patient.delete_patient import delete_patient_service

# Import the modularized service function to fetch all patients
from ..services.patient.get_all_patients import get_all_patients_service

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

# Define route to retrieve a specific patient's profile by ID
@router.get("/{patient_id}", response_model=PatientRead)
async def get_patient(
    patient_id: int,                                # Patient ID from path
    token: str = Depends(oauth2_scheme),            # Extract token from header
    db: Session = Depends(get_db)                   # Inject DB session
):
    """
    Get a patient's profile by ID.
    Only the patient themselves or an admin can access the data.
    """
    # Call the modular service to handle patient retrieval logic
    return await get_patient_by_id_service(patient_id, token, db)


# ---------------------------- Route: Create Patient ----------------------------

# Endpoint to create a new patient profile
@router.post("/", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,                         # Payload for creating patient
    token: str = Depends(oauth2_scheme),            # Extract token from header
    db: Session = Depends(get_db)                   # Inject DB session
):
    # Call the modular service to handle patient creation
    return await create_patient_service(patient, token, db)


# ---------------------------- Route: Update Patient ----------------------------

# Endpoint to update an existing patient's profile
@router.put("/{patient_id}", response_model=PatientRead)
async def update_patient(
    patient_id: int,                                # ID of patient to update
    update_data: PatientUpdate,                     # Update data as Pydantic model
    token: str = Depends(oauth2_scheme),            # Extract token from header
    db: Session = Depends(get_db)                   # Inject DB session
):
    # Call the modular service to handle patient update logic
    return await update_patient_service(patient_id, update_data, token, db)


# ---------------------------- Route: Delete Patient ----------------------------

# Endpoint to delete a patient (admin-only access)
@router.delete("/{patient_id}", response_model=PatientDeleteResponse)
async def delete_patient(
    patient_id: int,                                # ID of patient to delete
    token: str = Depends(oauth2_scheme),            # Extract token from header
    db: Session = Depends(get_db)                   # Inject DB session
):
    """
    Delete a patient by ID.
    Only accessible to admins.
    """
    # Call the modular service to handle patient deletion
    return await delete_patient_service(patient_id, token, db)


# ---------------------------- Route: Get All Patients ----------------------------

# Endpoint to retrieve all patients (admin gets all; patient gets only self)
@router.get("/", response_model=list[PatientRead])
async def get_all_patients(
    token: str = Depends(oauth2_scheme),            # Extract token from header
    db: Session = Depends(get_db)                   # Inject DB session
):
    """
    Get all patient records.
    Admins see all; regular patients see only their own info.
    """
    # Call the modular service to return one or more patients based on role
    return await get_all_patients_service(token, db)
