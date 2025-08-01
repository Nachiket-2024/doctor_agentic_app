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
from ...utils.slot_availability_utils import SlotAvailabilityUtils

# ---------------------------- Class: DoctorSlotAvailabilityService ----------------------------

class DoctorSlotAvailabilityService:
    """
    Service to retrieve available slots for a doctor on a specific date,
    based on weekly availability and existing appointments.
    """

    # ---------------------------- Constructor ----------------------------

    def __init__(self, db: Session):
        # Initialize with the provided database session
        self.db = db

    # ---------------------------- Method: get_available_slots ----------------------------

    async def get_available_slots_by_doctor_id(
        self,
        doctor_id: int,
        date_str: str
    ) -> list[str]:
        """
        Get a list of available slot start times for a doctor on a given date.

        Args:
            doctor_id (int): ID of the doctor.
            date_str (str): Date in YYYY-MM-DD format.

        Returns:
            list[str]: List of available slot start time strings.
        """
        try:
            # Parse the input date string to a datetime.date object
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format")

            # Retrieve the doctor by ID from the database
            doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()

            # Raise 404 if doctor is not found
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")

            # Derive the weekday key (e.g., 'mon', 'tue') from the target date
            weekday_key = calendar.day_name[target_date.weekday()].lower()[:3]

            # Load precomputed weekly slots for the doctor
            weekly_slots = doctor.weekly_available_slots or {}

            # If the doctor has no slots on that weekday, return an empty list
            if weekday_key not in weekly_slots:
                return []

            # Retrieve all potential slots for that weekday
            all_slots = weekly_slots[weekday_key]

            # Query all appointments for this doctor on the given date
            appointments = self.db.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == target_date
            ).all()

            # Extract booked start times from existing appointments
            booked_times = [appt.start_time for appt in appointments]

            # Filter out booked times from all available slots
            available_slots = SlotAvailabilityUtils.filter_booked_slots(all_slots, booked_times)

            # Return the final list of available (unbooked) slot strings
            return available_slots

        # Raise internal server error for any unexpected failure
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
