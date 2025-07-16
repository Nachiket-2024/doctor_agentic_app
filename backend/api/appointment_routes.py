# --- Import FastAPI and dependencies ---
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

# --- Import models, schemas, and db session ---
from ..models.appointment_model import Appointment
from ..schemas.appointment_schema import AppointmentCreate, Appointment as AppointmentSchema
from ..db.session import get_db

# --- Create the router instance ---
router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

# --- Route to create a new appointment ---
@router.post("/", response_model=AppointmentSchema)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).filter(
        Appointment.date == appointment.date,
        Appointment.start_time == appointment.start_time,
        Appointment.doctor_id == appointment.doctor_id
    ).first()
    if db_appointment:
        raise HTTPException(status_code=400, detail="Appointment already exists at this time.")

    new_appointment = Appointment(**appointment.model_dump())  # ✅ Updated for Pydantic v2
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

# --- Route to update an appointment ---
@router.put("/{appointment_id}", response_model=AppointmentSchema)
def update_appointment(appointment_id: int, appointment: AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    for key, value in appointment.model_dump().items():
        setattr(db_appointment, key, value)

    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# --- Route to get an appointment by ID ---
@router.get("/{appointment_id}", response_model=AppointmentSchema)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment
