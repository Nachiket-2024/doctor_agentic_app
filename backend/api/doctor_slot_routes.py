# ---------------------------- Imports ----------------------------

from fastapi import APIRouter, Depends, HTTPException, Query  # FastAPI tools for routing, dependencies, errors
from sqlalchemy.orm import Session                            # SQLAlchemy session to interact with DB
from datetime import datetime                                 # For date parsing and conversion
import calendar                                               # For mapping weekday index to name

# ---------------------------- Internal Imports ----------------------------

from ..db.session import get_db                               # DB session dependency
from ..models.user_model import User                          # Doctor model (in User table)
from ..models.appointment_model import Appointment            # Appointment model
from ..utils.slot_utils import generate_available_slots       # Slot generation utility

# ---------------------------- APIRouter Setup ----------------------------

router = APIRouter(
    prefix="/doctor_slot",      # Base URL prefix for this router
    tags=["Doctor Slots"],      # Used for grouping in docs
)

# ---------------------------- Route: Get Available Slots ----------------------------

@router.get("/{doctor_id}/available-slots")
async def get_available_slots(
    doctor_id: int,
    date_str: str = Query(..., description="Date in YYYY-MM-DD"),  # Date to check slots for
    db: Session = Depends(get_db)                                  # Inject DB session
):
    """
    Return available time slots for a doctor on a given date.
    """
    try:
        # Parse the input date string (e.g. "2025-07-26")
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

        # Fetch the doctor by ID and ensure their role is 'doctor'
        doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Determine the weekday string, e.g., "mon", "tue"
        weekday_key = calendar.day_name[target_date.weekday()].lower()[:3]

        # Load the available_days dict from the doctor record (default to empty if null)
        available_days = doctor.available_days or {}

        # If the doctor is not available on the given weekday, return empty slot list
        if weekday_key not in available_days:
            return []

        # Extract the list of time ranges for that weekday
        time_ranges = available_days[weekday_key]  # Should be a list like ["09:00-12:00", "14:00-17:00"]

        # If there are no time ranges defined for the day, return empty list
        if not time_ranges:
            return []

        # Use the slot duration set by doctor, or fallback to 30 minutes
        slot_duration = doctor.slot_duration or 30

        # Fetch all appointments already booked for that doctor on the target date
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == target_date
        ).all()

        # Collect all the booked start times (these will be skipped in slot generation)
        booked_times = [appt.start_time for appt in appointments]

        # Call the utility function to get list of available slots
        available_slots = generate_available_slots(time_ranges, slot_duration, booked_times)

        # Return the generated slot list
        return available_slots

    except Exception as e:
        # Return any unexpected errors as HTTP 500
        raise HTTPException(status_code=500, detail=str(e))
