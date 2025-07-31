# ---------------------------- External Imports ----------------------------

# For parsing string date formats
from datetime import datetime

# To map weekday indices to names
import calendar

# To raise standard HTTP exceptions
from fastapi import HTTPException

# To define expected database session type
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Doctor model to fetch weekly available slots
from ...models.doctor_model import Doctor

# Appointment model for fetching existing bookings
from ...models.appointment_model import Appointment

# Utility function to remove already-booked slots
from ...utils.filter_booked_slots import filter_booked_slots

# ---------------------------- Service Function ----------------------------

# Async function to get available time slots for a doctor on a specific date
async def get_available_slots_by_doctor_id_service(
    doctor_id: int,
    date_str: str,
    db: Session
) -> list[str]:
    """
    Returns a list of available slot start times (as strings) for a doctor
    on a given date, using precomputed weekly slots and filtering out booked ones.

    Parameters:
    - doctor_id (int): ID of the doctor
    - date_str (str): Target date in YYYY-MM-DD format
    - db (Session): SQLAlchemy DB session

    Returns:
    - list[str]: Available slot start times
    """
    try:
        # Parse the input date string to a datetime.date object
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

        # Retrieve the doctor by ID from the database
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Derive the weekday key ('mon', 'tue', etc.) from the target date
        weekday_key = calendar.day_name[target_date.weekday()].lower()[:3]

        # Load the doctor's precomputed weekly slots dictionary
        weekly_slots = doctor.weekly_available_slots or {}

        # If the doctor is unavailable on that day, return empty list
        if weekday_key not in weekly_slots:
            return []

        # Extract all slot start times (as strings) for the given weekday
        all_slots = weekly_slots[weekday_key]

        # Query booked appointments for this doctor on the target date
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == target_date
        ).all()

        # Extract booked slot start times as time objects
        booked_times = [appt.start_time for appt in appointments]

        # Filter out booked slots from the precomputed slot list
        available_slots = filter_booked_slots(all_slots, booked_times)

        # Return the final list of available (unbooked) slot strings
        return available_slots

    except Exception as e:
        # Raise 500 error on any unexpected failure
        raise HTTPException(status_code=500, detail=str(e))
