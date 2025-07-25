# ---------------------------- External Imports ----------------------------

# FastAPI dependencies for routing, authentication, error handling, and status codes
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# SQLAlchemy ORM Session for DB interactions
from sqlalchemy.orm import Session

# Python standard library for calendar weekday name conversions
import calendar

# ---------------------------- Internal Imports ----------------------------

# Appointment model (SQLAlchemy ORM)
from ..models.appointment_model import Appointment

# User model for doctor and patient references
from ..models.user_model import User

# Pydantic schemas for appointment input and output validation
from ..schemas.appointment_schema import AppointmentCreate, AppointmentUpdate, AppointmentResponse

# DB session dependency provider
from ..db.session import get_db

# JWT token verification utility
from ..auth.auth_utils import verify_jwt_token

# Admin-only access control utility
from ..auth.auth_user_check import admin_only

# Gmail API utility to send confirmation/cancellation emails
from ..google_integration.gmail_utils import send_email_via_gmail

# Google Calendar API helpers for event CRUD
from ..google_integration.calendar_utils import create_event, update_event, delete_event

# Utility to generate available appointment slots given constraints
from ..utils.slot_utils import generate_available_slots

# ---------------------------- OAuth2 Setup ----------------------------

# OAuth2PasswordBearer dependency to extract tokens from Authorization headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------------------------- Router Initialization ----------------------------

# Create FastAPI router with prefix and tags for grouping endpoints
router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)

# ---------------------------- Route: Get Appointment by ID ----------------------------

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,                      # Appointment ID path parameter
    token: str = Depends(oauth2_scheme),     # JWT token extracted via OAuth2 scheme
    db: Session = Depends(get_db)             # Database session dependency
):
    """
    Retrieve an appointment by ID.
    Access allowed only to admin, the appointment's doctor, or the patient.
    """
    try:
        # Verify JWT token and extract user info
        payload = verify_jwt_token(token)
        user_role = payload.get("role")
        user_id = payload.get("user_id")

        # Fetch appointment by ID
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Authorization check: only admin, appointment's doctor or patient can access
        if user_role == "admin" or \
           (user_role == "doctor" and appointment.doctor_id == user_id) or \
           (user_role == "patient" and appointment.patient_id == user_id):
            return appointment

        # Unauthorized access
        raise HTTPException(status_code=403, detail="You are not authorized to view this appointment")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Create Appointment ----------------------------

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,          # Appointment data validated by schema
    token: str = Depends(oauth2_scheme),     # JWT token dependency
    db: Session = Depends(get_db)             # Database session dependency
):
    """
    Create a new appointment.
    Only admin or patient roles allowed.
    Checks doctor availability and books Google Calendar event.
    """
    try:
        # Verify token and extract role and refresh token
        payload = verify_jwt_token(token)
        user_role = payload.get("role")
        refresh_token = payload.get("refresh_token")

        # Access control: only admin or patient can create
        if user_role not in ["admin", "patient"]:
            raise HTTPException(status_code=403, detail="Only admin or patient can create an appointment")

        # Validate doctor existence and role
        doctor = db.query(User).filter(User.id == appointment.doctor_id, User.role == "doctor").first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Determine weekday key (e.g., 'mon', 'tue') for availability lookup
        weekday_key = calendar.day_name[appointment.date.weekday()].lower()[:3]
        available_days = doctor.available_days or {}

        # Check if doctor is available on appointment day
        if weekday_key not in available_days:
            raise HTTPException(status_code=400, detail="Doctor not available on selected day")

        # Get time range and existing bookings to find free slots
        time_range = available_days[weekday_key]
        booked = db.query(Appointment).filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.date == appointment.date
        ).all()
        booked_times = [appt.start_time for appt in booked]

        # Generate available slots considering booked times
        available_slots = generate_available_slots(time_range, doctor.slot_duration or 30, booked_times)

        # Check if requested start_time is free
        if appointment.start_time not in available_slots:
            raise HTTPException(status_code=400, detail="Selected time slot is already booked or unavailable")

        # Create appointment record
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

        # Fetch patient info for email/calendar notifications
        patient = db.query(User).filter(User.id == new_appointment.patient_id).first()

        # Send confirmation email via Gmail
        send_email_via_gmail(token, refresh_token, patient.email, "Appointment Confirmation", new_appointment.id, db)

        # Create Google Calendar event for the appointment
        created_event = create_event(
            token,
            refresh_token,
            f"Appointment with Dr. {doctor.name}",
            f"{new_appointment.date}T{new_appointment.start_time}:00",
            f"{new_appointment.date}T{new_appointment.end_time}:00",
            patient.email
        )

        # Store Google Calendar event ID in appointment record
        new_appointment.event_id = created_event.get("id")
        db.commit()
        db.refresh(new_appointment)

        return new_appointment

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Update Appointment ----------------------------

@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,                    # Appointment ID to update
    appointment_update: AppointmentUpdate, # Partial update data validated by schema
    token: str = Depends(oauth2_scheme),    # JWT token dependency
    db: Session = Depends(get_db)            # Database session dependency
):
    """
    Update an existing appointment.
    Only admin users can perform update.
    Updates Google Calendar event and sends notification email.
    """
    try:
        # Verify token and confirm admin role
        payload = verify_jwt_token(token)
        admin_only(token, db)
        refresh_token = payload.get("refresh_token")

        # Retrieve existing appointment record
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Determine new doctor and appointment date/time
        doctor_id = appointment_update.doctor_id or appointment.doctor_id
        date = appointment_update.date or appointment.date
        start_time = appointment_update.start_time or appointment.start_time

        # Validate doctor availability on updated day
        doctor = db.query(User).filter(User.id == doctor_id).first()
        weekday_key = calendar.day_name[date.weekday()].lower()[:3]
        available_days = doctor.available_days or {}
        if weekday_key not in available_days:
            raise HTTPException(status_code=400, detail="Doctor not available on selected day")

        # Check for booked time conflicts excluding current appointment
        time_range = available_days[weekday_key]
        booked = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == date,
            Appointment.id != appointment_id
        ).all()
        booked_times = [appt.start_time for appt in booked]

        # Generate free slots and validate start_time availability
        available_slots = generate_available_slots(time_range, doctor.slot_duration or 30, booked_times)
        if start_time not in available_slots:
            raise HTTPException(status_code=400, detail="Selected time slot is already booked or unavailable")

        # Apply updates to appointment record
        appointment.doctor_id = doctor_id
        appointment.patient_id = appointment_update.patient_id or appointment.patient_id
        appointment.date = date
        appointment.start_time = start_time
        appointment.end_time = appointment_update.end_time or appointment.end_time
        appointment.status = appointment_update.status or appointment.status
        appointment.reason = appointment_update.reason or appointment.reason

        # Commit updates and refresh record
        db.commit()
        db.refresh(appointment)

        # Fetch patient info for notifications
        patient = db.query(User).filter(User.id == appointment.patient_id).first()

        # Update Google Calendar event if exists
        if appointment.event_id:
            update_event(
                token,
                refresh_token,
                appointment.event_id,
                f"Updated Appointment with Dr. {doctor.name}",
                f"{appointment.date}T{appointment.start_time}:00",
                f"{appointment.date}T{appointment.end_time}:00",
                patient.email
            )

        # Send update notification email
        send_email_via_gmail(token, refresh_token, patient.email, "Updated Appointment", appointment.id, db)

        return appointment

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Delete Appointment ----------------------------

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,                 # Appointment ID to delete
    token: str = Depends(oauth2_scheme), # JWT token dependency
    db: Session = Depends(get_db)         # Database session dependency
):
    """
    Delete an appointment by ID.
    Only admin users can delete.
    Deletes associated Google Calendar event and sends cancellation email.
    """
    try:
        # Verify token and confirm admin role
        payload = verify_jwt_token(token)
        admin_only(token, db)
        refresh_token = payload.get("refresh_token")

        # Fetch appointment to delete
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Fetch patient info for notification
        patient = db.query(User).filter(User.id == appointment.patient_id).first()

        # Delete Google Calendar event if exists
        if appointment.event_id:
            delete_event(token, refresh_token, appointment.event_id)

        # Send cancellation email notification
        send_email_via_gmail(token, refresh_token, patient.email, "Appointment Cancellation", appointment.id, db)

        # Delete appointment record from DB and commit
        db.delete(appointment)
        db.commit()

        # Return None, FastAPI returns 204 No Content automatically
        return

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# ---------------------------- Route: Get All Appointments ----------------------------

@router.get("/", response_model=list[AppointmentResponse])
async def get_all_appointments(
    token: str = Depends(oauth2_scheme),   # JWT token dependency
    db: Session = Depends(get_db)           # Database session dependency
):
    """
    Retrieve all appointments visible to the requester based on role:
    - Admin: all appointments
    - Doctor: only their appointments
    - Patient: only their appointments
    """
    try:
        # Decode token to extract user info
        payload = verify_jwt_token(token)
        user_role = payload.get("role")
        user_id = payload.get("user_id")

        # Return appointments based on user role
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
