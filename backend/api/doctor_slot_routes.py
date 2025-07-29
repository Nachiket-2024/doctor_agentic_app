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

# Doctor model to fetch precomputed weekly slots
from ..models.doctor_model import Doctor

# Appointment model representing bookings
from ..models.appointment_model import Appointment

# Utility to remove booked slots from precomputed ones
from ..utils.filter_booked_slots import filter_booked_slots


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

# Define an HTTP GET route to fetch available slots for a doctor on a given date
@router.get("/{doctor_id}/available-slots")
async def get_available_slots(
    doctor_id: int,                                     # Doctor's unique ID passed as a path parameter
    date_str: str = Query(..., description="Date in YYYY-MM-DD"),  # Target date for slot query (required query param)
    token: str = Depends(oauth2_scheme),                # Extract the bearer token from request headers
    db: Session = Depends(get_db)                       # Inject a database session into the route
):
    """
    Returns a list of available slot start times (as strings) for a doctor
    on a given date, using precomputed weekly slots and filtering out booked ones.
    """
    try:
        # -------- Parse the input date string to a datetime.date object --------
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

        # -------- Retrieve the doctor by ID from the database --------
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # -------- Derive the weekday key ('mon', 'tue', etc.) from the target date --------
        weekday_key = calendar.day_name[target_date.weekday()].lower()[:3]

        # -------- Load the doctor's precomputed weekly slots dictionary --------
        weekly_slots = doctor.weekly_available_slots or {}

        # -------- If the doctor is unavailable on that day, return empty list --------
        if weekday_key not in weekly_slots:
            return []

        # -------- Extract all slot start times (as strings) for the given weekday --------
        all_slots = weekly_slots[weekday_key]

        # -------- Query booked appointments for this doctor on the target date --------
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == target_date
        ).all()

        # -------- Extract booked slot start times as time objects --------
        booked_times = [appt.start_time for appt in appointments]

        # -------- Filter out booked slots from the precomputed slot list --------
        available_slots = filter_booked_slots(all_slots, booked_times)

        # -------- Return the final list of available (unbooked) slot strings --------
        return available_slots

    except Exception as e:
        # -------- If an unexpected error occurs, return a 500 error with details --------
        raise HTTPException(status_code=500, detail=str(e))
