from fastapi import APIRouter, HTTPException, Depends  # For routing, exceptions, and dependency injection
from sqlalchemy.orm import Session  # For interacting with the database
from datetime import datetime  # For combining date and time objects
from typing import Annotated  # For type annotations

# --- Import models ---
from ..models.appointment_model import Appointment  # Appointment DB model
from ..models.doctor_model import Doctor  # Doctor DB model
from ..models.patient_model import Patient  # Patient DB model

# --- Import schemas ---
from ..schemas.appointment_schema import (
    AppointmentCreate,
    AppointmentUpdate,
    Appointment as AppointmentSchema
)

from ..auth.auth_config import ADMIN_EMAILS  # Import admin emails from the .env file

# --- Import DB session dependency ---
from ..db.session import get_db  # Provides SQLAlchemy session for DB access

# --- Import Google integrations ---
from ..google_integration.calendar_utils import create_event  # Function to create a Google Calendar event
from ..google_integration.email_utils import send_email_via_gmail  # Gmail API email sender

# --- Import Auth utils ---
from ..auth.auth_routes import get_current_user_from_cookie  # Auth protection for routes

# --- Define the appointment router ---
router = APIRouter(
    prefix="/appointments",  # Base route prefix
    tags=["Appointments"]    # OpenAPI docs tag
)

@router.post("/", response_model=AppointmentSchema)
def create_appointment(
    appointment: AppointmentCreate, 
    db: Session = Depends(get_db),
    current_user: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)] = None
):
    # Allow patients to create appointments for themselves
    if isinstance(current_user, Patient) and current_user.id == appointment.patient_id:
        # Patient can only create their own appointment
        pass
    # Admin can create appointments for any patient
    elif current_user.email in ADMIN_EMAILS:
        # Admin can create appointments for any patient
        pass
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to create appointments for others.")

    # Proceed with appointment creation
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    new_appointment = Appointment(**appointment.model_dump())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    # Additional integrations (Google Calendar, Email) ...

    return new_appointment

# --- Get all appointments ---
@router.get("/", response_model=list[AppointmentSchema])
def get_appointments(
    db: Session = Depends(get_db),
    current_user: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)] = None
):
    # Admins can view all appointments, doctors and patients can only see theirs
    if current_user.email in ADMIN_EMAILS:
        return db.query(Appointment).all()
    elif isinstance(current_user, Doctor):
        return db.query(Appointment).filter(Appointment.doctor_id == current_user.id).all()
    elif isinstance(current_user, Patient):
        return db.query(Appointment).filter(Appointment.patient_id == current_user.id).all()

# --- Get appointment by ID ---
@router.get("/{appointment_id}", response_model=AppointmentSchema)
def get_appointment(
    appointment_id: int, 
    db: Session = Depends(get_db),
    current_user: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)] = None
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Admins, doctors (for their patients), and patients (for themselves) can view appointments
    if current_user.email in ADMIN_EMAILS or current_user.id == appt.doctor_id or current_user.id == appt.patient_id:
        return appt
    else:
        raise HTTPException(status_code=403, detail="Access denied. You can only view your own appointments.")

# --- Update appointment by ID ---
@router.put("/{appointment_id}", response_model=AppointmentSchema)
def update_appointment(
    appointment_id: int, 
    updated: AppointmentUpdate, 
    db: Session = Depends(get_db),
    current_user: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)] = None
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Only allow the patient who created the appointment or the doctor for their appointment to update
    if current_user.email in ADMIN_EMAILS or current_user.id == appt.doctor_id or current_user.id == appt.patient_id:
        for key, value in updated.model_dump(exclude_unset=True).items():
            setattr(appt, key, value)

        db.commit()
        db.refresh(appt)
        return appt
    else:
        raise HTTPException(status_code=403, detail="Access denied. You can only update your own appointment.")

# --- Delete appointment by ID ---
@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int, 
    db: Session = Depends(get_db),
    current_user: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)] = None
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Only allow admins or the doctor who created the appointment to delete it
    if current_user.email in ADMIN_EMAILS or current_user.id == appt.doctor_id:
        db.delete(appt)
        db.commit()
        return {"detail": "Appointment deleted"}
    else:
        raise HTTPException(status_code=403, detail="Access denied. You can only delete your own appointments.")
