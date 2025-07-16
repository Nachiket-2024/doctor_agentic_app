from datetime import datetime, timedelta

# --- Generate time slots between start and end with given duration ---
def generate_available_slots(start_str: str, end_str: str, slot_minutes: int) -> list[str]:
    slots = []
    start = datetime.strptime(start_str, "%H:%M")
    end = datetime.strptime(end_str, "%H:%M")

    while start + timedelta(minutes=slot_minutes) <= end:
        slots.append(start.strftime("%H:%M"))
        start += timedelta(minutes=slot_minutes)

    return slots
