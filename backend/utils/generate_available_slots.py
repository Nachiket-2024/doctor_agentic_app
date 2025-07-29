# ------------------------------------- External Imports -------------------------------------

# For working with dates, durations, and time objects
from datetime import datetime, timedelta, time

# ------------------------------------- Slot Builder Function -------------------------------------

# Function to generate all possible weekly slot start times (as strings) per weekday
def generate_all_weekly_slots(time_ranges_by_day: dict[str, list[str]], slot_duration: int) -> dict[str, list[str]]:
    """
    Generate a dictionary of available slot times (as strings) per weekday from time ranges.

    Args:
        time_ranges_by_day (Dict[str, List[str]]): Dict with weekdays as keys and time ranges as values.
            Example: {"mon": ["10:00-12:00", "14:00-16:00"], "tue": [], ...}
        slot_duration (int): Duration of each slot in minutes.

    Returns:
        Dict[str, List[str]]: Dictionary with weekdays as keys and slot start times in "HH:MM" format.
    """

    # Define all weekdays to ensure output is complete
    weekdays = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    # Initialize the weekly slot dictionary with empty lists for each day
    weekly_slots = {day: [] for day in weekdays}

    # Iterate over each day and its associated time ranges
    for day, ranges in time_ranges_by_day.items():
        # Skip if day is not a valid weekday key
        if day not in weekly_slots:
            continue

        # Process each time range for the given day
        for time_range in ranges:
            # Skip empty or incorrectly formatted time ranges
            if not time_range or "-" not in time_range:
                continue

            # Split the time range into start and end time strings
            start_str, end_str = time_range.strip().split("-")

            # Convert start and end strings to `time` objects
            start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
            end_time = datetime.strptime(end_str.strip(), "%H:%M").time()

            # Combine time with today’s date for datetime arithmetic
            current = datetime.combine(datetime.today(), start_time)
            end = datetime.combine(datetime.today(), end_time)

            # Define the slot increment as a timedelta
            delta = timedelta(minutes=slot_duration)

            # Generate slot times and format them as "HH:MM"
            while current + delta <= end:
                slot_str = current.time().strftime("%H:%M")
                weekly_slots[day].append(slot_str)
                current += delta

    # Return the final dictionary of weekday slot times as strings
    return weekly_slots
