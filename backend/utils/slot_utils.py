# ---------------------------- Imports ----------------------------
from datetime import datetime, timedelta, time  # For working with dates, time ranges, and slot durations

# ---------------------------- Slot Generation Function ----------------------------

def generate_available_slots(time_ranges: list[str], slot_duration: int, booked_times: list[time]) -> list[time]:
    """
    Generate available time slots from one or more time ranges, excluding already booked ones.

    Args:
        time_ranges (List[str]): A list of time ranges like ["10:00-12:00", "14:00-16:00"]
        slot_duration (int): Duration of each appointment slot in minutes
        booked_times (List[time]): List of start times that are already booked

    Returns:
        List[time]: List of available start times (as time objects)
    """

    # Initialize a list to hold all available slots across all ranges
    slots = []

    # Loop through each time range in the list
    for time_range in time_ranges:
        # Split the time range string into start and end times (e.g. "09:00-12:00")
        start_str, end_str = time_range.strip().split("-")

        # Convert the start and end time strings into time objects
        start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
        end_time = datetime.strptime(end_str.strip(), "%H:%M").time()

        # Convert to datetime objects so we can do arithmetic with timedelta
        current = datetime.combine(datetime.today(), start_time)
        end = datetime.combine(datetime.today(), end_time)

        # Define the time delta for a single slot
        delta = timedelta(minutes=slot_duration)

        # Loop to generate slots in this range
        while current + delta <= end:
            # Extract only the time part for the slot
            slot_start = current.time()

            # Add slot if it hasn't been booked already
            if slot_start not in booked_times:
                slots.append(slot_start)

            # Move to the next slot time
            current += delta

    # Return the full list of available slots across all time ranges
    return slots
