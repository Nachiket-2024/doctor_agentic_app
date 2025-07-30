# ------------------------------------- External Imports -------------------------------------

# For type annotations
from datetime import date

# For data validation
from pydantic import BaseModel

# ------------------------------------- Tool Input Schema -------------------------------------

# Schema for checking a doctor's availability
class CheckAvailabilityInput(BaseModel):
    doctor_id: int
    date: date

# ------------------------------------- Tool Output Schema -------------------------------------

# Schema for available time slots (e.g., ["10:00", "10:30"])
class CheckAvailabilityOutput(BaseModel):
    available_slots: list[str]
