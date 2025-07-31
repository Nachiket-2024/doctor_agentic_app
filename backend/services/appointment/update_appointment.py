# ---------------------------- External Imports ----------------------------

# Exception class for HTTP error responses
from fastapi import HTTPException

# SQLAlchemy ORM Session for DB interactions
from sqlalchemy.orm import Session

# Built-in Python library to map weekday indices to names
import calendar

# Built-in datetime utility to construct time objects
from datetime import time

# ---------------------------- Internal Imports ----------------------------

# SQLAlchemy model for appointments
from ...models.appointment_model import Appointment

# SQLAlchemy models for doctor, patient, and admin
from ...models.doctor_model import Doctor
from ...models.patient_model import Patient
from ...models.admin_model import Admin

# Pydantic schema for updating appointments
from ...schemas.appointment_schema import AppointmentUpdate

# Utility function to extract user identity from token
from ...auth.auth_user_check import get_user_from_token

# Google Calendar utility to update calendar event
from ...google_integration.calendar_utils import update_event

# Gmail utility to send email notifications
from ...google_integration.gmail_utils import send_email_via_gmail

# Function to filter out already booked slots
from ...utils.filter_booked_slots import filter_booked_slots

# ---------------------------- Function: Update Appointment ----------------------------

# Update an appointment and modify Google Calendar and notify user
async def update_appointment_entry(appointment_id: int, appointment_update: AppointmentUpdate, token: str, db: Session):
    try:
        # Extract user identity and role from token
        _, user_role, _ = get_user_from_token(token, db)

        # Restrict access to admins only
        if user_role != "admin":
            raise HTTPException(status_code=403, detail="Only admin can update appointments")

        # Fetch the existing appointment from the DB
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Extract fields from input or use existing ones
        doctor_id = appointment_update.doctor_id or appointment.doctor_id
        date = appointment_update.date or appointment.date
        start_time = appointment_update.start_time or appointment.start_time

        # Retrieve the doctor's data and availability
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        weekday_key = calendar.day_name[date.weekday()].lower()[:3]
        available_days = doctor.available_days or {}

        # Check if doctor is available on that weekday
        if weekday_key not in available_days:
            raise HTTPException(status_code=400, detail="Doctor not available on selected day")

        # Retrieve all slots available for that day
        weekly_slots = doctor.weekly_available_slots or {}
        day_slots = weekly_slots.get(weekday_key, [])

        # Filter out slots already booked by other appointments
        booked = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == date,
            Appointment.id != appointment_id
        ).all()
        booked_times = [appt.start_time for appt in booked]
        available_slots = filter_booked_slots(day_slots, booked_times)

        # Check if the updated start time is available
        if start_time.strftime("%H:%M") not in available_slots:
            raise HTTPException(status_code=400, detail="Selected time slot is already booked or unavailable")

        # Update appointment details
        appointment.doctor_id = doctor_id
        appointment.patient_id = appointment_update.patient_id or appointment.patient_id
        appointment.date = date
        appointment.start_time = start_time
        appointment.status = appointment_update.status or appointment.status
        appointment.reason = appointment_update.reason or appointment.reason

        # Recalculate or use given end time
        if not appointment_update.end_time:
            start_time_minutes = start_time.hour * 60 + start_time.minute
            end_time_minutes = start_time_minutes + doctor.slot_duration
            hours = end_time_minutes // 60
            minutes = end_time_minutes % 60
            appointment.end_time = time(hours, minutes)
        else:
            appointment.end_time = appointment_update.end_time

        # Save updated appointment to DB
        db.commit()
        db.refresh(appointment)

        # Fetch patient and admin info for email notification
        patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
        admin = db.query(Admin).filter(Admin.id == 1).first()

        # Update calendar event if already created
        if appointment.event_id:
            await update_event(
                patient.id,
                db,
                appointment.event_id,
                f"Updated Appointment with {doctor.name}",
                f"{appointment.date}T{appointment.start_time.isoformat()}",
                f"{appointment.date}T{appointment.end_time.isoformat()}",
                patient.email
            )

        # Send email notification to patient
        await send_email_via_gmail(admin.id, patient.email, "Updated Appointment", appointment.id, db, email_type="updated")

        # Return updated appointment object
        return appointment

    # Re-raise known HTTP errors
    except HTTPException as http_exc:
        raise http_exc

    # Handle unexpected server errors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
