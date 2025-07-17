# --- FastAPI and SQLAlchemy imports ---
from fastapi import APIRouter, HTTPException, Depends  # For routing, exceptions, and dependency injection
from sqlalchemy.orm import Session  # For interacting with the database
from datetime import datetime  # For combining date and time objects

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

# --- Import DB session dependency ---
from ..db.session import get_db  # Provides SQLAlchemy session for DB access

# --- Import Google integrations ---
from ..google_integration.calendar_utils import create_event  # Function to create a Google Calendar event
from ..google_integration.email_utils import send_email_via_gmail  # Gmail API email sender

# --- Define the appointment router ---
router = APIRouter(
    prefix="/appointments",  # Base route prefix
    tags=["Appointments"]    # OpenAPI docs tag
)

# --- Create a new appointment ---
@router.post("/", response_model=AppointmentSchema)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    # Check if doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Check if patient exists
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Create and save the new appointment
    new_appointment = Appointment(**appointment.model_dump())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    # Generate datetime strings for calendar & email
    try:
        start_dt = datetime.combine(appointment.date, appointment.start_time).isoformat()
        end_dt = datetime.combine(appointment.date, appointment.end_time).isoformat()
        summary = f"Appointment with Dr. {doctor.name}"

        # --- Google Calendar Event ---
        create_event(
            summary=summary,
            start_time=start_dt,
            end_time=end_dt,
            email=patient.email
        )

        # --- Gmail Confirmation Email ---
        subject = "Appointment Confirmation"
        body = f"""
Dear {patient.name},

Your appointment with Dr. {doctor.name} is confirmed.

Date: {appointment.date}
Time: {appointment.start_time.strftime('%I:%M %p')} – {appointment.end_time.strftime('%I:%M %p')}
Doctor: {doctor.name} ({doctor.specialization})

Thank you,
Agentic Health System
"""
        send_email_via_gmail(to_email=patient.email, subject=subject, body=body)

    except Exception as e:
        print("Google Integration Error:", e)  # Replace with proper logging if needed

    return new_appointment

# --- Get all appointments ---
@router.get("/", response_model=list[AppointmentSchema])
def get_appointments(db: Session = Depends(get_db)):
    return db.query(Appointment).all()

# --- Get appointment by ID ---
@router.get("/{appointment_id}", response_model=AppointmentSchema)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt

# --- Update appointment by ID ---
@router.put("/{appointment_id}", response_model=AppointmentSchema)
def update_appointment(appointment_id: int, updated: AppointmentUpdate, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    for key, value in updated.model_dump(exclude_unset=True).items():
        setattr(appt, key, value)
    
    db.commit()
    db.refresh(appt)
    return appt

# --- Delete appointment by ID ---
@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appt)
    db.commit()
    return {"detail": "Appointment deleted"}
