from datetime import datetime, timedelta  # Importing datetime for time manipulation and timedelta for time arithmetic

# --- Generate time slots between start and end with given duration ---
def generate_available_slots(start_str: str, end_str: str, slot_minutes: int) -> list[str]:
    """
    Generates available time slots between a given start and end time with a specified duration.
    """
    slots = []  # Initialize an empty list to store the generated time slots

    # Convert start and end time strings to datetime objects (to work with them easily)
    start = datetime.strptime(start_str, "%H:%M")  # Parse start time string to datetime
    end = datetime.strptime(end_str, "%H:%M")  # Parse end time string to datetime

    # Loop through the time range, generating slots of the specified duration
    while start + timedelta(minutes=slot_minutes) <= end:  # Check if the next slot fits within the end time
        slot = start.strftime("%H:%M")  # Format the start time to a string (e.g., "14:00")
        slots.append(slot)  # Add the formatted time slot to the list
        start += timedelta(minutes=slot_minutes)  # Move the start time forward by the duration

    return slots  # Return the list of generated time slots
