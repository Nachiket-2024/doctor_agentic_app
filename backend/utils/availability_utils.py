import logging
from datetime import datetime, timedelta

# Create a logger with the name 'availability_utils'
logger = logging.getLogger("availability_utils")
logger.setLevel(logging.DEBUG)  # Capture DEBUG and above logs

# JSON format configuration (to match your existing log format)
formatter = logging.Formatter('{"asctime": "%(asctime)s", "levelname": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}')

# StreamHandler to output logs to the console
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# --- Generate time slots between start and end with given duration ---
def generate_available_slots(start_str: str, end_str: str, slot_minutes: int) -> list[str]:
    slots = []
    start = datetime.strptime(start_str, "%H:%M")
    end = datetime.strptime(end_str, "%H:%M")

    # Log slot generation attempt
    logger.info(f"Generating slots from {start} to {end}, with {slot_minutes}-minute duration.")

    while start + timedelta(minutes=slot_minutes) <= end:
        slot = start.strftime("%H:%M")
        logger.info(f"Generated slot: {slot}")  # Logs the generated slot
        slots.append(slot)
        start += timedelta(minutes=slot_minutes)

    return slots
