from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.appointment_model import Appointment
from ..models.doctor_model import Doctor
from ..models.doctor_availability_model import DoctorAvailability

def generate_slots(doctor_id, db):
    """
    Generate time slots for the doctor based on available days and slot duration.

    :param doctor_id: The ID of the doctor.
    :param db: The database session.
    :return: A dictionary with days as keys and lists of slot times as values.
    """
    # Fetch doctor details (available_days and slot_duration)
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    
    available_days = doctor.available_days  # {"mon": ["10:00", "14:00"], ...}
    slot_duration = doctor.slot_duration  # Slot duration (in minutes)

    generated_slots = {}

    # Loop over the available days and generate the slots
    for day, time_range in available_days.items():
        start_time_str, end_time_str = time_range
        start_time = datetime.strptime(start_time_str, "%H:%M")
        end_time = datetime.strptime(end_time_str, "%H:%M")
        
        slots_for_day = []

        # Generate slots from start_time to end_time using slot_duration
        current_time = start_time
        while current_time < end_time:
            slots_for_day.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=slot_duration)
        
        generated_slots[day] = slots_for_day

    # Store the generated slots in the database for the next 2 weeks
    for i in range(2):  # For the next two weeks
        for day, slots in generated_slots.items():
            for slot_time in slots:
                # Adjust the date to get the exact weekday (i.e., 'mon', 'tue', etc.)
                date_for_slot = get_date_for_weekday(day, i)  # A helper function to compute the exact date
                new_slot = DoctorAvailability(
                    doctor_id=doctor_id,
                    date=date_for_slot,
                    start_time=slot_time,  # Assuming this is in HH:MM format for now
                    is_booked=False  # Initially, all slots are unbooked
                )
                db.add(new_slot)

    db.commit()

    return generated_slots


def get_date_for_weekday(weekday, week_offset):
    """
    Helper function to get the actual date for a specific weekday (e.g., 'mon', 'tue')
    considering a 2-week period starting from today.

    :param weekday: The day of the week (e.g., 'mon', 'tue').
    :param week_offset: 0 for this week, 1 for next week.
    :return: The date corresponding to that weekday.
    """
    # Mapping of weekdays to indices (0 for Monday, 6 for Sunday)
    weekdays = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    today = datetime.today()
    current_weekday = today.weekday()  # Today’s weekday as integer (0=Mon, 6=Sun)
    target_weekday = weekdays[weekday]

    # Calculate the difference in days to the target weekday
    delta_days = target_weekday - current_weekday
    if delta_days < 0:  # If the target weekday is in the next week
        delta_days += 7

    # Add the week offset (0 for this week, 1 for next week)
    target_date = today + timedelta(days=delta_days + (week_offset * 7))

    return target_date.date()


def get_doctor_availability(doctor_id, date, db):
    """
    Get available slots for a doctor on a given date, removing booked slots.

    :param doctor_id: The ID of the doctor.
    :param date: The date to check availability.
    :param db: The database session.
    :return: A list of available slots after removing booked slots.
    """
    # Retrieve all the appointments for the doctor on this date
    booked_slots = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == date
    ).all()

    # Retrieve all generated slots for this doctor for this date
    available_slots = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.date == date,
        DoctorAvailability.is_booked == False  # Only consider unbooked slots
    ).all()

    # List of available times before booking
    available_times = [slot.start_time for slot in available_slots]

    # Remove the booked slots from the available times
    for appointment in booked_slots:
        booked_start_time = appointment.start_time.strftime("%H:%M")
        if booked_start_time in available_times:
            available_times.remove(booked_start_time)

    return available_times
