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
from ...auth.auth_user_check import AuthUserCheck

# Gmail utility to send confirmation email
from ...google_integration.gmail_service import GmailService

# Google Calendar utility to create calendar events
from ...google_integration.google_calender_service import GoogleCalendarService

# Slot filter utility to exclude already booked slots
from ...utils.slot_availability_utils import SlotAvailabilityUtils

# ---------------------------- Class: AppointmentService ----------------------------

class CreateAppointmentService:
    """
    Service class responsible for managing appointment-related business logic.
    """

    # Constructor accepts a database session object
    def __init__(self, db: Session):
        # Store the DB session instance for reuse across methods
        self.db = db

    # ---------------------------- Method: Create Appointment Entry ----------------------------

    async def create_appointment(self, appointment: AppointmentCreate, token: str):
        """
        Creates a new appointment with all validations, slot availability checks,
        Google Calendar sync, and email notifications.

        Args:
            appointment (AppointmentCreate): Data for the new appointment
            token (str): JWT token from the request header

        Returns:
            Appointment: The newly created appointment object
        """

        try:
            # Extract user identity and role from token using auth utility
            _, user_role, _ = AuthUserCheck.get_user_from_token(token, self.db)

            # Enforce that only patients or admins can book appointments
            if user_role not in ["admin", "patient"]:
                raise HTTPException(status_code=403, detail="Only admin or patient can create an appointment")

            # Query the doctor from the DB using the given doctor_id
            doctor = self.db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()

            # Raise 404 if doctor is not found
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")

            # Convert the appointment date to a weekday string (e.g., 'mon')
            weekday_key = calendar.day_name[appointment.date.weekday()].lower()[:3]

            # Get doctor’s available days
            available_days = doctor.available_days or {}

            # If selected weekday is not available, raise error
            if weekday_key not in available_days:
                raise HTTPException(status_code=400, detail="Doctor not available on selected day")

            # Load all weekly available slot times from the doctor profile
            weekly_slots = doctor.weekly_available_slots or {}

            # Extract slot list for the current weekday
            day_slots = weekly_slots.get(weekday_key, [])

            # Query DB for existing appointments on the same day for this doctor
            booked = self.db.query(Appointment).filter(
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.date == appointment.date
            ).all()

            # Extract already booked start times to exclude from available list
            booked_times = [appt.start_time for appt in booked]

            # Use utility to filter out booked times from all available slots
            available_slots = SlotAvailabilityUtils.filter_booked_slots(day_slots, booked_times)

            # Convert desired start time to string format for lookup
            requested_slot = appointment.start_time.strftime("%H:%M")

            # Raise error if requested slot is not available
            if requested_slot not in available_slots:
                raise HTTPException(status_code=400, detail="Selected time slot is already booked or unavailable")

            # If end_time is not provided, auto-calculate based on slot_duration
            if not appointment.end_time:
                start_time_minutes = appointment.start_time.hour * 60 + appointment.start_time.minute
                end_time_minutes = start_time_minutes + doctor.slot_duration
                hours = end_time_minutes // 60
                minutes = end_time_minutes % 60
                appointment.end_time = time(hours, minutes)

            # Create new appointment ORM object using validated inputs
            new_appointment = Appointment(
                doctor_id=appointment.doctor_id,
                patient_id=appointment.patient_id,
                date=appointment.date,
                start_time=appointment.start_time,
                end_time=appointment.end_time,
                status=appointment.status,
                reason=appointment.reason,
            )

            # Persist appointment object to the database
            self.db.add(new_appointment)
            self.db.commit()
            self.db.refresh(new_appointment)

            # Fetch the patient object to send confirmation and calendar invite
            patient = self.db.query(Patient).filter(Patient.id == new_appointment.patient_id).first()

            # Get admin (usually sender of emails & owner of calendar events)
            admin = self.db.query(Admin).filter(Admin.id == 1).first()

            # Send confirmation email to the patient
            await GmailService(db=self.db, user_id=admin.id).send_email_via_gmail(
                patient.email,
                "Appointment Confirmation",
                new_appointment.id,
                email_type="created"
            )

            # Create Google Calendar event for the appointment
            created_event = await GoogleCalendarService(db=self.db, user_id=patient.id, user_role="patient").create_event(
                f"Appointment with {doctor.name}",
                f"{new_appointment.date}T{new_appointment.start_time.isoformat()}",
                f"{new_appointment.date}T{new_appointment.end_time.isoformat()}",
                patient.email
            )

            # Save Google event ID to appointment record
            new_appointment.event_id = created_event.get("id")
            self.db.commit()
            self.db.refresh(new_appointment)

            # Return the finalized appointment object
            return new_appointment

        # Re-raise known HTTP exceptions as-is
        except HTTPException as http_exc:
            raise http_exc

        # Catch any unexpected exception, print traceback, and raise 500
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
