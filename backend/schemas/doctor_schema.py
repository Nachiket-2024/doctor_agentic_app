# --- Import Pydantic base class and typing tools ---
from pydantic import BaseModel  # Base class for Pydantic models
from typing import Annotated  # Modern way to represent optional fields

# --- Base schema with common doctor fields ---
class DoctorBase(BaseModel):
    name: str  # Doctor's full name
    specialization: str  # Doctor's field of expertise

    # Available days and times, e.g. {"Monday": ["10:00", "14:00"]}
    available_days: dict[str, list[str]]  # Dictionary of day -> list of time slots (as strings)

    slot_duration: Annotated[int | None, None] = 30  # Optional slot duration in minutes (default: 30)

# --- Schema for creating a new doctor ---
class DoctorCreate(DoctorBase):
    pass  # Inherits all fields from DoctorBase

# --- Schema for updating an existing doctor (partial updates allowed) ---
class DoctorUpdate(BaseModel):
    name: Annotated[str | None, None] = None
    specialization: Annotated[str | None, None] = None
    available_days: Annotated[dict[str, list[str]] | None, None] = None
    slot_duration: Annotated[int | None, None] = None

# --- Schema for reading doctor data from the database ---
class Doctor(DoctorBase):
    id: int  # Auto-generated doctor ID

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy ORM models
