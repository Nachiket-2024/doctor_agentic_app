# ---------------------------- External Imports ----------------------------

# Exception class for HTTP error responses
from fastapi import HTTPException

# Built-in Python library to map dates to day names
import calendar

# Time utility from datetime to create time objects
from datetime import time

# Built-in traceback module for debugging exceptions
import traceback

# SQLAlchemy ORM Session for DB interactions
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Appointment model from SQLAlchemy
from ...models.appointment_model import Appointment

# Doctor, Patient, Admin models
from ...models.doctor_model import Doctor
from ...models.patient_model import Patient
from ...models.admin_model import Admin

# Pydantic schema for creating appointments
from ...schemas.appointment_schema import AppointmentCreate

# Auth utility to extract user info from token
from ...auth.auth_user_check import get_user_from_token

# Gmail utility to send confirmation email
from ...google_integration.gmail_utils import send_email_via_gmail

# Google Calendar utility to create calendar events
from ...google_integration.calendar_utils import create_event

# Slot filter utility to exclude already booked slots
from ...utils.filter_booked_slots import filter_booked_slots

# ---------------------------- Function: Create Appointment ----------------------------

# Create a new appointment with validation, notifications, and calendar sync
async def create_appointment_entry(appointment: AppointmentCreate, token: str, db: Session):
    try:
        # Extract user role and ID from token
        _, user_role, _ = get_user_from_token(token, db)

        # Only patient or admin is allowed to create appointments
        if user_role not in ["admin", "patient"]:
            raise HTTPException(status_code=403, detail="Only admin or patient can create an appointment")

        # Fetch doctor info from DB
        doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Check if doctor is available on selected weekday
        weekday_key = calendar.day_name[appointment.date.weekday()].lower()[:3]
        available_days = doctor.available_days or {}
        if weekday_key not in available_days:
            raise HTTPException(status_code=400, detail="Doctor not available on selected day")

        # Load available slots from weekly availability
        weekly_slots = doctor.weekly_available_slots or {}
        day_slots = weekly_slots.get(weekday_key, [])

        # Fetch existing booked appointments for the doctor on the selected date
        booked = db.query(Appointment).filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.date == appointment.date
        ).all()

        # Extract already booked times to filter out
        booked_times = [appt.start_time for appt in booked]
        available_slots = filter_booked_slots(day_slots, booked_times)

        # Ensure requested time is still available
        if appointment.start_time.strftime("%H:%M") not in available_slots:
            raise HTTPException(status_code=400, detail="Selected time slot is already booked or unavailable")

        # Auto-calculate end_time if not provided
        if not appointment.end_time:
            start_time_minutes = appointment.start_time.hour * 60 + appointment.start_time.minute
            end_time_minutes = start_time_minutes + doctor.slot_duration
            hours = end_time_minutes // 60
            minutes = end_time_minutes % 60
            appointment.end_time = time(hours, minutes)

        # Create new appointment object and persist to DB
        new_appointment = Appointment(
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            date=appointment.date,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            status=appointment.status,
            reason=appointment.reason,
        )
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)

        # Fetch patient details for notifications
        patient = db.query(Patient).filter(Patient.id == new_appointment.patient_id).first()

        # Get default admin to use as email sender
        admin = db.query(Admin).filter(Admin.id == 1).first()

        # Send email confirmation to patient
        await send_email_via_gmail(
            admin.id,
            patient.email,
            "Appointment Confirmation",
            new_appointment.id,
            db,
            email_type="created"
        )

        # Add to Google Calendar and store event ID
        created_event = await create_event(
            patient.id,
            db,
            f"Appointment with {doctor.name}",
            f"{new_appointment.date}T{new_appointment.start_time.isoformat()}",
            f"{new_appointment.date}T{new_appointment.end_time.isoformat()}",
            patient.email
        )
        new_appointment.event_id = created_event.get("id")
        db.commit()
        db.refresh(new_appointment)

        return new_appointment

    # Re-raise HTTP errors
    except HTTPException as http_exc:
        raise http_exc

    # Log and raise unknown exceptions
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
