# ---------------------------- External Imports ----------------------------

# FastAPI tools for routing, dependency injection, and HTTP exceptions
from fastapi import APIRouter, Depends, HTTPException, Query

# SQLAlchemy Session to interact with the database
from sqlalchemy.orm import Session

# For parsing and handling dates
from datetime import datetime

# To convert weekday indices to names (e.g., 0 -> Monday)
import calendar

# OAuth2PasswordBearer to extract JWT token from requests
from fastapi.security import OAuth2PasswordBearer


# ---------------------------- Internal Imports ----------------------------

# Dependency to get a database session
from ..db.session import get_db

# Doctor model to fetch doctor availability and constraints
from ..models.doctor_model import Doctor

# Appointment model representing bookings
from ..models.appointment_model import Appointment

# Utility to generate available time slots given constraints
from ..utils.slot_utils import generate_available_slots


# ---------------------------- OAuth2 Setup ----------------------------

# Setup OAuth2 scheme to extract token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ---------------------------- APIRouter Setup ----------------------------

# Initialize FastAPI router with prefix and documentation tags
router = APIRouter(
    prefix="/doctor_slot",      # Base URL prefix for all routes in this router
    tags=["Doctor Slots"],      # Group routes under this tag in API docs
)


# ---------------------------- Route: Get Available Slots ----------------------------

@router.get("/{doctor_id}/available-slots")
async def get_available_slots(
    doctor_id: int,                                     # Doctor's unique ID as path parameter
    date_str: str = Query(..., description="Date in YYYY-MM-DD"),  # Date query parameter in ISO format
    token: str = Depends(oauth2_scheme),                # Extract JWT token from Authorization header
    db: Session = Depends(get_db)                       # Inject database session dependency
):
    """
    Return available time slots for a doctor on a specified date.

    Steps:
    - Parse input date string to date object.
    - Validate doctor existence.
    - Find doctor's available time ranges for the weekday.
    - Get all booked appointment times for the date.
    - Generate available slots excluding booked times.
    """
    try:
        # -------- Parse the input date string to a date object --------
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

        # -------- Query doctor by ID --------
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # -------- Get weekday key like 'mon', 'tue', etc. --------
        weekday_key = calendar.day_name[target_date.weekday()].lower()[:3]

        # -------- Retrieve the doctor's available days dictionary --------
        available_days = doctor.available_days or {}

        # -------- If no availability on the day, return empty list --------
        if weekday_key not in available_days:
            return []

        # -------- Extract the list of time ranges for that weekday --------
        time_ranges = available_days[weekday_key]

        # -------- If no time ranges are defined, return empty list --------
        if not time_ranges:
            return []

        # -------- Use the slot duration set by doctor --------
        slot_duration = doctor.slot_duration

        # -------- Query all appointments booked for the doctor on the target date --------
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == target_date
        ).all()

        # -------- Collect booked start times to exclude from available slots --------
        booked_times = [appt.start_time for appt in appointments]

        # -------- Generate available slots excluding booked times --------
        available_slots = generate_available_slots(time_ranges, slot_duration, booked_times)

        # -------- Return the list of available slots --------
        return available_slots

    except Exception as e:
        # -------- Handle unexpected errors with 500 Internal Server Error --------
        raise HTTPException(status_code=500, detail=str(e))
