from pydantic import BaseModel, ConfigDict
from typing import Annotated

# --- Base schema with shared fields for input/output ---
class PatientBase(BaseModel):
    name: str  # Full name of the patient
    email: str  # Email ID of the patient (must be unique)
    google_id: str  # Unique Google ID assigned to the user
    phone: Annotated[str | None, None] = None  # Optional phone number
    age: int | None = None
    role: str = "patient"

# --- Schema for creating a new patient ---
class PatientCreate(PatientBase):
    pass  # Inherits all fields from PatientBase

# --- Schema for updating an existing patient (partial update allowed) ---
class PatientUpdate(BaseModel):
    name: Annotated[str | None, None] = None  # Optional update
    email: Annotated[str | None, None] = None
    phone: Annotated[str | None, None] = None
    google_id: Annotated[str | None, None] = None  # Allow updating google_id if needed
    age: Annotated[int | None, None] = None  # Optional age update

# --- Schema for reading a patient (response model) ---
class Patient(PatientBase):
    id: int  # Auto-generated unique ID of the patient

    class Config(ConfigDict):
        from_attributes = True  # Enable ORM-to-Pydantic conversion
