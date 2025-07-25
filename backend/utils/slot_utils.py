# ------------------------------------- External Imports -------------------------------------

# For working with dates, durations, and time objects  
from datetime import datetime, timedelta, time

# ------------------------------------- Slot Generation Function -------------------------------------

# Function to generate available time slots excluding booked times  
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

    # Loop through each time range string provided  
    for time_range in time_ranges:
        # Split the time range into start and end strings (e.g., "09:00-12:00")  
        start_str, end_str = time_range.strip().split("-")

        # Convert the start string into a time object  
        start_time = datetime.strptime(start_str.strip(), "%H:%M").time()

        # Convert the end string into a time object  
        end_time = datetime.strptime(end_str.strip(), "%H:%M").time()

        # Combine the time objects with today's date to allow arithmetic  
        current = datetime.combine(datetime.today(), start_time)
        end = datetime.combine(datetime.today(), end_time)

        # Define the slot size using timedelta  
        delta = timedelta(minutes=slot_duration)

        # Loop to generate slots until reaching the end time  
        while current + delta <= end:
            # Get the time component only (without date)  
            slot_start = current.time()

            # Include this slot if it's not already booked  
            if slot_start not in booked_times:
                slots.append(slot_start)

            # Move to the next slot  
            current += delta

    # Return the list of generated available slot times  
    return slots
