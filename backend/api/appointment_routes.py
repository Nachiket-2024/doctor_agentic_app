# ---------------------------- External Imports ----------------------------

# FastAPI dependencies for routing, authentication, error handling, and status codes
from fastapi import APIRouter, Depends, HTTPException, status

# OAuth2 token extractor from request headers
from fastapi.security import OAuth2PasswordBearer

# SQLAlchemy ORM Session for DB interactions
from sqlalchemy.orm import Session

# Built-in Python library to map dates to day names
import calendar

# Built-in traceback module for debugging exceptions
import traceback

# Time utility from datetime to create time objects
from datetime import time

# ---------------------------- Internal Imports ----------------------------

# SQLAlchemy model for appointments
from ..models.appointment_model import Appointment

# SQLAlchemy model for users (doctors and patients)
from ..models.user_model import User

# Pydantic schemas for input and output validation of appointments
from ..schemas.appointment_schema import AppointmentCreate, AppointmentUpdate, AppointmentResponse

# Dependency to get DB session from context
from ..db.session import get_db

# JWT utility to decode and verify access tokens
from ..auth.auth_utils import verify_jwt_token

# Authorization check utility for admin-only endpoints
from ..auth.auth_user_check import admin_only

# Gmail integration for sending emails
from ..google_integration.gmail_utils import send_email_via_gmail

# Google Calendar integration for event CRUD operations
from ..google_integration.calendar_utils import create_event, update_event, delete_event

# Utility to generate available time slots based on availability
from ..utils.slot_utils import generate_available_slots

# Asynchronous token refresh utility for Google APIs
from ..auth.google_token_service import get_valid_google_access_token

# ---------------------------- OAuth2 Setup ----------------------------

# Token URL to be used by OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------------------------- Router Initialization ----------------------------

# Initialize router instance with tag and path prefix
router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)

# ---------------------------- Route: Get Appointment by ID ----------------------------

# Get a specific appointment based on its ID
@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Decode JWT to get user identity and role
        payload = verify_jwt_token(token)
        user_role = payload.get("role")
        user_id = payload.get("id")

        # Retrieve appointment from DB
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Authorize access based on user role
        if user_role == "admin" or \
           (user_role == "doctor" and appointment.doctor_id == user_id) or \
           (user_role == "patient" and appointment.patient_id == user_id):
            return appointment

        raise HTTPException(status_code=403, detail="You are not authorized to view this appointment")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Create Appointment ----------------------------

# Endpoint to create a new appointment
@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Decode JWT to get user role and ID
        payload = verify_jwt_token(token)
        user_role = payload.get("role")
        user_id = payload.get("id")

        # Only patients or admins can create appointments
        if user_role not in ["admin", "patient"]:
            raise HTTPException(status_code=403, detail="Only admin or patient can create an appointment")

        # Fetch doctor info from DB
        doctor = db.query(User).filter(User.id == appointment.doctor_id, User.role == "doctor").first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Check if doctor is available on the selected day
        weekday_key = calendar.day_name[appointment.date.weekday()].lower()[:3]
        available_days = doctor.available_days or {}
        if weekday_key not in available_days:
            raise HTTPException(status_code=400, detail="Doctor not available on selected day")

        # Generate time slots and validate chosen time
        time_range = available_days[weekday_key]
        booked = db.query(Appointment).filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.date == appointment.date
        ).all()
        booked_times = [appt.start_time for appt in booked]
        available_slots = generate_available_slots(time_range, doctor.slot_duration, booked_times)
        if appointment.start_time not in available_slots:
            raise HTTPException(status_code=400, detail="Selected time slot is already booked or unavailable")

        # Auto-compute end_time if not given
        if not appointment.end_time:
            start_time_minutes = appointment.start_time.hour * 60 + appointment.start_time.minute
            end_time_minutes = start_time_minutes + doctor.slot_duration
            hours = end_time_minutes // 60
            minutes = end_time_minutes % 60
            appointment.end_time = time(hours, minutes)

        # Create and persist appointment object
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

        # Retrieve patient info for email/calendar purposes
        patient = db.query(User).filter(User.id == new_appointment.patient_id).first()

        # Get valid Google access and refresh tokens for calendar API
        access_token, refresh_token = await get_valid_google_access_token(user_id, db)

        # Send email to patient confirming appointment
        await send_email_via_gmail(user_id, patient.email, "Appointment Confirmation", new_appointment.id, db)

        # Create Google Calendar event for the appointment
        created_event = await create_event(
            user_id,
            db,
            f"Appointment with {doctor.name}",
            f"{new_appointment.date}T{new_appointment.start_time.isoformat()}",
            f"{new_appointment.date}T{new_appointment.end_time.isoformat()}",
            patient.email
        )

        # Save the calendar event ID in DB
        new_appointment.event_id = created_event.get("id")
        db.commit()
        db.refresh(new_appointment)

        return new_appointment

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Update Appointment ----------------------------

# Update an existing appointment and modify Google Calendar if needed
@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Verify JWT and admin access
        payload = verify_jwt_token(token)
        admin_only(token, db)
        user_id = payload.get("id")

        # Fetch existing appointment
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Determine new doctor/date/time based on input or defaults
        doctor_id = appointment_update.doctor_id or appointment.doctor_id
        date = appointment_update.date or appointment.date
        start_time = appointment_update.start_time or appointment.start_time

        # Validate doctor's availability on new date
        doctor = db.query(User).filter(User.id == doctor_id).first()
        weekday_key = calendar.day_name[date.weekday()].lower()[:3]
        available_days = doctor.available_days or {}
        if weekday_key not in available_days:
            raise HTTPException(status_code=400, detail="Doctor not available on selected day")

        # Generate updated available slots and check conflict
        time_range = available_days[weekday_key]
        booked = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == date,
            Appointment.id != appointment_id
        ).all()
        booked_times = [appt.start_time for appt in booked]
        available_slots = generate_available_slots(time_range, doctor.slot_duration, booked_times)
        if start_time not in available_slots:
            raise HTTPException(status_code=400, detail="Selected time slot is already booked or unavailable")

        # Update appointment fields
        appointment.doctor_id = doctor_id
        appointment.patient_id = appointment_update.patient_id or appointment.patient_id
        appointment.date = date
        appointment.start_time = start_time
        appointment.status = appointment_update.status or appointment.status
        appointment.reason = appointment_update.reason or appointment.reason

        # Recalculate end time if not explicitly provided
        if not appointment_update.end_time:
            start_time_minutes = start_time.hour * 60 + start_time.minute
            end_time_minutes = start_time_minutes + doctor.slot_duration
            hours = end_time_minutes // 60
            minutes = end_time_minutes % 60
            appointment.end_time = time(hours, minutes)
        else:
            appointment.end_time = appointment_update.end_time

        # Persist changes to DB
        db.commit()
        db.refresh(appointment)

        # Fetch patient info
        patient = db.query(User).filter(User.id == appointment.patient_id).first()
        access_token, refresh_token = await get_valid_google_access_token(user_id, db)

        # Update calendar event if exists
        if appointment.event_id:
            await update_event(
                user_id,
                db,
                appointment.event_id,
                f"Updated Appointment with Dr. {doctor.name}",
                f"{appointment.date}T{appointment.start_time.isoformat()}",
                f"{appointment.date}T{appointment.end_time.isoformat()}",
                patient.email
            )

        # Notify patient via email
        await send_email_via_gmail(user_id, patient.email, "Updated Appointment", appointment.id, db)

        return appointment

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Delete Appointment ----------------------------

# Delete an appointment and remove its calendar entry if present
@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Authenticate and check admin access
        payload = verify_jwt_token(token)
        admin_only(token, db)
        user_id = payload.get("id")

        # Locate appointment in DB
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Fetch patient email for notification
        patient = db.query(User).filter(User.id == appointment.patient_id).first()
        access_token, refresh_token = await get_valid_google_access_token(user_id, db)

        # Delete from Google Calendar if synced
        if appointment.event_id:
            await delete_event(user_id, db, appointment.event_id)

        # Notify patient about cancellation
        await send_email_via_gmail(user_id, patient.email, "Appointment Cancellation", appointment.id, db)

        # Remove appointment from DB
        db.delete(appointment)
        db.commit()

        return

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Get All Appointments ----------------------------

# Retrieve appointments depending on user role (admin/doctor/patient)
@router.get("/", response_model=list[AppointmentResponse])
async def get_all_appointments(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Decode and extract user role and ID
        payload = verify_jwt_token(token)
        user_role = payload.get("role")
        user_id = payload.get("id")

        # Return appointments based on access rights
        if user_role == "admin":
            return db.query(Appointment).all()
        elif user_role == "doctor":
            return db.query(Appointment).filter(Appointment.doctor_id == user_id).all()
        elif user_role == "patient":
            return db.query(Appointment).filter(Appointment.patient_id == user_id).all()
        else:
            raise HTTPException(status_code=403, detail="Not authorized to view appointments.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
