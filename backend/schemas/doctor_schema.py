# --- Import Pydantic for data validation ---
from pydantic import BaseModel
from typing import List, Optional

# --- Define the Doctor schema ---
class DoctorBase(BaseModel):
    name: str
    specialization: str
    available_days: dict  # e.g. {"mon": ["10:00", "14:00"], "tue": [...]}
    slot_duration: Optional[int] = 30  # Default 30 minutes

# --- Schema for creating a new doctor ---
class DoctorCreate(DoctorBase):
    pass

# --- Schema for reading (output) a doctor ---
class Doctor(DoctorBase):
    id: int

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy models
