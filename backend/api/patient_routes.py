# --- FastAPI and SQLAlchemy imports ---
from fastapi import APIRouter, HTTPException, Depends  # Routing and error handling
from sqlalchemy.orm import Session  # DB session management

# --- Import patient model and schemas ---
from ..models.patient_model import Patient
from ..schemas.patient_schema import (
    PatientCreate,
    PatientUpdate,
    Patient as PatientSchema
)

# --- Import database session provider ---
from ..db.session import get_db

# --- Define router with prefix and tag ---
router = APIRouter(prefix="/patients", tags=["Patients"])

# --- Create a new patient ---
@router.post("/", response_model=PatientSchema)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = Patient(**patient.model_dump())  # Convert Pydantic model to DB model
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient  # Return the created patient

# --- Get all patients ---
@router.get("/", response_model=list[PatientSchema])
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()  # Return all patients in the DB

# --- Get a single patient by ID ---
@router.get("/{patient_id}", response_model=PatientSchema)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient  # Return patient if found

# --- Update an existing patient (partial update supported) ---
@router.put("/{patient_id}", response_model=PatientSchema)
def update_patient(patient_id: int, updated: PatientUpdate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Only update fields that were provided (exclude unset ones)
    for key, value in updated.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return patient  # Return updated patient

# --- Delete a patient by ID ---
@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()
    return {"detail": "Patient deleted"}  # Return confirmation message
