# ------------------------------------- External Imports -------------------------------------

# For working with dates and weekdays
from datetime import date
import calendar

# SQLAlchemy session type
from sqlalchemy.orm import Session

# ------------------------------------- Internal Imports -------------------------------------

# Models for doctor and appointment
from ..models.doctor_model import Doctor
from ..models.appointment_model import Appointment

# Utility to filter out booked slots
from ..utils.filter_booked_slots import filter_booked_slots


# ------------------------------------- Core Availability Logic -------------------------------------

# Core function to fetch available slots for MCP/LLM use
def get_available_slots_logic(doctor_id: int, target_date: date, db: Session) -> list[str]:
    """
    Returns a list of available time slots for a doctor on a given date.

    Args:
        doctor_id (int): ID of the doctor.
        target_date (date): The date for which to fetch availability.
        db (Session): SQLAlchemy session for DB operations.

    Returns:
        list[str]: List of available time slot strings (e.g., ["10:00", "10:30"]).
    """

    # Fetch the doctor object using the provided doctor ID
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise ValueError("Doctor not found")

    # Extract weekday string key like "mon", "tue", etc.
    weekday_key = calendar.day_name[target_date.weekday()].lower()[:3]

    # Load weekly slots JSON from the doctor model (may be empty)
    weekly_slots = doctor.weekly_available_slots or {}

    # If doctor is unavailable that day, return an empty list
    if weekday_key not in weekly_slots:
        return []

    # Get all precomputed time slot strings for that weekday
    all_slots = weekly_slots[weekday_key]

    # Fetch all appointments for the doctor on the given date
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == target_date
    ).all()

    # Extract just the start times from the booked appointments
    booked_times = [appt.start_time for appt in appointments]

    # Filter out booked times from the full list of slots
    return filter_booked_slots(all_slots, booked_times)
