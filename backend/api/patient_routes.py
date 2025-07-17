from fastapi import APIRouter, HTTPException, Depends  # Routing and error handling
from sqlalchemy.orm import Session  # DB session management

# Import patient model and schemas
from ..models.patient_model import Patient
from ..schemas.patient_schema import (
    PatientCreate,
    PatientUpdate,
    Patient as PatientSchema
)

# Import database session provider
from ..db.session import get_db

# Import the function to get the current user (and their role) from the cookie
from ..auth.auth_routes import get_current_user_from_cookie  # Assuming this function is in auth_routes

# Import admin emails from .env
from ..auth.auth_config import ADMIN_EMAILS

# Define router with prefix and tag
router = APIRouter(prefix="/patients", tags=["Patients"])

# Create a new patient (anyone can create themselves)
@router.post("/", response_model=PatientSchema)
def create_patient(
    patient: PatientCreate, 
    db: Session = Depends(get_db), 
    current_user: Patient = Depends(get_current_user_from_cookie)
):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can create their own profile.")
    
    # Proceed with creation of the patient
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient  # Return the created patient

# Get all patients (accessible by admin only)
@router.get("/", response_model=list[PatientSchema])
def get_patients(
    db: Session = Depends(get_db), 
    current_user: Patient = Depends(get_current_user_from_cookie)
):
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Only admins can access all patient data.")
    
    return db.query(Patient).all()  # Return all patients in the DB

# Get a single patient by ID (accessible by admin, doctor, and the patient themselves)
@router.get("/{patient_id}", response_model=PatientSchema)
def get_patient(
    patient_id: int, 
    db: Session = Depends(get_db), 
    current_user: Patient = Depends(get_current_user_from_cookie)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Allow admins and doctors to view any patient, and allow the patient to view themselves
    if current_user.email in ADMIN_EMAILS or current_user.role == "doctor" or current_user.id == patient_id:
        return patient
    else:
        raise HTTPException(status_code=403, detail="Access denied.")

# Update an existing patient (patients can update themselves, admins can update anyone)
@router.put("/{patient_id}", response_model=PatientSchema)
def update_patient(
    patient_id: int, 
    updated: PatientUpdate, 
    db: Session = Depends(get_db), 
    current_user: Patient = Depends(get_current_user_from_cookie)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # If patient is trying to update their own record, or if admin is updating any record
    if current_user.email in ADMIN_EMAILS or current_user.id == patient_id:
        for key, value in updated.model_dump(exclude_unset=True).items():
            setattr(patient, key, value)

        db.commit()
        db.refresh(patient)
        return patient  # Return updated patient
    else:
        raise HTTPException(status_code=403, detail="Access denied. You can only update your own profile.")

# Delete a patient by ID (only accessible by admin)
@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int, 
    db: Session = Depends(get_db), 
    current_user: Patient = Depends(get_current_user_from_cookie)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Only admin can delete a patient record
    if current_user.email in ADMIN_EMAILS:
        db.delete(patient)
        db.commit()
        return {"detail": "Patient deleted"}  # Return confirmation message
    else:
        raise HTTPException(status_code=403, detail="Access denied. Only admins can delete patient records.")
