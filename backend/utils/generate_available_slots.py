# ------------------------------------- External Imports -------------------------------------

# For working with dates, durations, and time objects
from datetime import datetime, timedelta, time

# ------------------------------------- Slot Builder Function -------------------------------------

# Function to generate all possible time slots from given time ranges grouped by weekday
def generate_all_weekly_slots(weekly_time_ranges: dict[str, list[str]], slot_duration: int) -> dict[str, list[str]]:
    """
    Generate all possible weekly slot start times from a dict of daily time ranges.

    Args:
        weekly_time_ranges (Dict[str, List[str]]): e.g., {"mon": ["10:00-12:00", "14:00-16:00"], "tue": ["09:00-11:00"], ...}
        slot_duration (int): Duration of each slot in minutes

    Returns:
        Dict[str, List[str]]: Dictionary mapping weekday keys to available slot strings
    """

    # Initialize output dictionary to hold day-wise slot lists
    weekly_slots: dict[str, list[str]] = {}

    # Iterate over each weekday and its list of time ranges
    for weekday, time_ranges in weekly_time_ranges.items():

        # Initialize list to store slots for current weekday
        day_slots: list[str] = []

        # Skip if no time ranges provided for the day
        if not time_ranges:
            weekly_slots[weekday] = []
            continue

        # Iterate over each time range string like "10:00-12:00"
        for time_range in time_ranges:

            # Skip if the time range is empty or invalid
            if not time_range or "-" not in time_range:
                continue

            # Split into start and end time strings
            start_str, end_str = time_range.strip().split("-")

            # Parse start and end time strings to time objects
            start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
            end_time = datetime.strptime(end_str.strip(), "%H:%M").time()

            # Combine with today's date to allow arithmetic
            current = datetime.combine(datetime.today(), start_time)
            end = datetime.combine(datetime.today(), end_time)

            # Define the time increment using timedelta
            delta = timedelta(minutes=slot_duration)

            # Loop to generate all slot times within this range
            while current + delta <= end:
                # Format the time object as "HH:MM" and append to list
                day_slots.append(current.strftime("%H:%M"))

                # Move to next time slot
                current += delta

        # Assign the collected slots to the weekday in the dictionary
        weekly_slots[weekday] = day_slots

    # Return the full dictionary of weekly slot timings
    return weekly_slots
