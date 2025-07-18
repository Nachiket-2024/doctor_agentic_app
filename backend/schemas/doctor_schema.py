# --- Import Pydantic base class and typing tools ---
from pydantic import BaseModel, ConfigDict  # Base class for Pydantic models
from typing import Annotated  # Modern way to represent optional fields

# --- Base schema with common doctor fields ---
class DoctorBase(BaseModel):
    name: str  # Doctor's full name
    specialization: str  # Doctor's field of expertise

    # Available days and times, e.g. {"Monday": ["10:00", "14:00"]}
    available_days: dict[str, list[str]]  # Dictionary of day -> list of time slots (as strings)

    slot_duration: Annotated[int | None, None] = 30  # Optional slot duration in minutes (default: 30)

    email: str  # Doctor's email for communication
    phone_number: Annotated[str | None, None] = None  # Optional phone number
    
    google_id: Annotated[str | None, None] = None  # Google ID (optional for new doctors)

    role: str = "doctor"

# --- Schema for creating a new doctor ---
class DoctorCreate(DoctorBase):
    pass  # Inherits all fields from DoctorBase, including google_id

# --- Schema for updating an existing doctor (partial updates allowed) ---
class DoctorUpdate(BaseModel):
    name: Annotated[str | None, None] = None
    specialization: Annotated[str | None, None] = None
    available_days: Annotated[dict[str, list[str]] | None, None] = None
    slot_duration: Annotated[int | None, None] = None
    email: Annotated[str | None, None] = None
    phone_number: Annotated[str | None, None] = None
    google_id: Annotated[str | None, None] = None  # Allow updating google_id if needed

# --- Schema for reading doctor data from the database ---
class Doctor(DoctorBase):
    id: int  # Auto-generated doctor ID

    class Config(ConfigDict):
        from_attributes = True  # Enables compatibility with SQLAlchemy ORM models
