# ------------------------------------- External Imports -------------------------------------

# Import time class for type hinting
from datetime import time

# ------------------------------------- Booked Slot Filter Function -------------------------------------

# Function to remove booked times from available slots
def filter_booked_slots(all_slots: list[str], booked_times: list[time]) -> list[str]:
    """
    Filter out booked slot times from the full list of available slot strings.

    Args:
        all_slots (List[str]): Precomputed slot times as strings like ["10:00", "10:30"]
        booked_times (List[time]): Already booked start times as time objects

    Returns:
        List[str]: Available slot times with booked ones removed
    """

    # Convert booked time objects to string format for comparison
    booked_set = set(bt.strftime("%H:%M") for bt in booked_times)

    # Return only those slots which are not booked
    return [slot for slot in all_slots if slot not in booked_set]
