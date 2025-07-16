# --- Import FastAPI and dependencies ---
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

# --- Import models, schemas, and db session ---
from ..models.doctor_model import Doctor
from ..schemas.doctor_schema import DoctorCreate, Doctor as DoctorSchema
from ..db.session import get_db

# --- Create the router instance ---
router = APIRouter(
    prefix="/doctors",  # Prefix for all doctor routes
    tags=["Doctors"]    # Tag for API docs
)

# --- Route to create a new doctor ---
@router.post("/", response_model=DoctorSchema)
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    # Check for duplicate doctor name
    db_doctor = db.query(Doctor).filter(Doctor.name == doctor.name).first()
    if db_doctor:
        raise HTTPException(status_code=400, detail="Doctor already exists")

    # Create and save new doctor
    new_doctor = Doctor(**doctor.model_dump())
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor

# --- Route to get a doctor by ID ---
@router.get("/{doctor_id}", response_model=DoctorSchema)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    db_doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor
