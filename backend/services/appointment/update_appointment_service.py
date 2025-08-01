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
from ...auth.auth_user_check import AuthUserCheck

# Google Calendar utility to update calendar event
from ...google_integration.google_calender_service import GoogleCalendarService

# Gmail utility to send email notifications
from ...google_integration.gmail_service import GmailService

# Function to filter out already booked slots
from ...utils.slot_availability_utils import SlotAvailabilityUtils

# ---------------------------- Class: UpdateAppointmentService ----------------------------

class UpdateAppointmentService:
    """
    Service class to handle appointment updates, including time validation,
    Google Calendar synchronization, and email notifications.
    """

    # Constructor to inject the database session
    def __init__(self, db: Session):
        # Store DB session for use in methods
        self.db = db

    # ---------------------------- Method: Update Appointment ----------------------------

    async def update_appointment(self, appointment_id: int, appointment_update: AppointmentUpdate, token: str):
        """
        Update an existing appointment, validate time availability, sync with calendar,
        and notify the patient via email.

        Args:
            appointment_id (int): The ID of the appointment to update
            appointment_update (AppointmentUpdate): Data for the update
            token (str): JWT token for the requesting user

        Returns:
            Appointment: Updated appointment object

        Raises:
            HTTPException: On unauthorized access, validation errors, or DB failures
        """

        try:
            # Extract user identity and role from token
            _, user_role, _ = AuthUserCheck.get_user_from_token(token, self.db)

            # Restrict access to admins only
            if user_role != "admin":
                raise HTTPException(status_code=403, detail="Only admin can update appointments")

            # Fetch the existing appointment
            appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if not appointment:
                raise HTTPException(status_code=404, detail="Appointment not found")

            # Extract new values or fallback to existing
            doctor_id = appointment_update.doctor_id or appointment.doctor_id
            date = appointment_update.date or appointment.date
            start_time = appointment_update.start_time or appointment.start_time

            # Retrieve doctor's schedule and availability
            doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
            weekday_key = calendar.day_name[date.weekday()].lower()[:3]
            available_days = doctor.available_days or {}

            # Verify doctor is available that day
            if weekday_key not in available_days:
                raise HTTPException(status_code=400, detail="Doctor not available on selected day")

            # Retrieve available slots for that day
            weekly_slots = doctor.weekly_available_slots or {}
            day_slots = weekly_slots.get(weekday_key, [])

            # Filter out already booked time slots (excluding the current appointment)
            booked = self.db.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == date,
                Appointment.id != appointment_id
            ).all()
            booked_times = [appt.start_time for appt in booked]
            available_slots = SlotAvailabilityUtils.filter_booked_slots(day_slots, booked_times)

            # Validate requested time slot
            if start_time.strftime("%H:%M") not in available_slots:
                raise HTTPException(status_code=400, detail="Selected time slot is already booked or unavailable")

            # Update appointment fields
            appointment.doctor_id = doctor_id
            appointment.patient_id = appointment_update.patient_id or appointment.patient_id
            appointment.date = date
            appointment.start_time = start_time
            appointment.status = appointment_update.status or appointment.status
            appointment.reason = appointment_update.reason or appointment.reason

            # Calculate end time if not provided
            if not appointment_update.end_time:
                start_time_minutes = start_time.hour * 60 + start_time.minute
                end_time_minutes = start_time_minutes + doctor.slot_duration
                hours = end_time_minutes // 60
                minutes = end_time_minutes % 60
                appointment.end_time = time(hours, minutes)
            else:
                appointment.end_time = appointment_update.end_time

            # Commit DB update
            self.db.commit()
            self.db.refresh(appointment)

            # Fetch related patient and admin info for notifications
            patient = self.db.query(Patient).filter(Patient.id == appointment.patient_id).first()
            admin = self.db.query(Admin).filter(Admin.id == 1).first()

            # Update the calendar event if it exists
            if appointment.event_id:
                await GoogleCalendarService(db=self.db, user_id=patient.id, user_role="patient").update_event(
                    appointment.event_id,
                    f"Updated Appointment with {doctor.name}",
                    f"{appointment.date}T{appointment.start_time.isoformat()}",
                    f"{appointment.date}T{appointment.end_time.isoformat()}",
                    patient.email
                )

            # Send email notification to patient
            await GmailService(db=self.db, user_id=admin.id).send_email_via_gmail(
                patient.email,
                "Updated Appointment",
                appointment.id,
                email_type="updated"
            )

            # Return updated appointment object
            return appointment

        # Re-raise HTTP-related errors
        except HTTPException as http_exc:
            raise http_exc

        # Handle unexpected server-side errors
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
