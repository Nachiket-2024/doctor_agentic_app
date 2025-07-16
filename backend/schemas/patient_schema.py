# --- Import Pydantic for data validation ---
from pydantic import BaseModel  # Base class for defining request/response models
from typing import Annotated  # Modern typing annotation helper

# --- Base schema with shared fields for input/output ---
class PatientBase(BaseModel):
    name: str  # Full name of the patient
    email: str  # Email ID of the patient (must be unique)
    phone: Annotated[str | None, None] = None  # Optional phone number

# --- Schema for creating a new patient ---
class PatientCreate(PatientBase):
    pass  # Inherits all fields from PatientBase

# --- Schema for updating an existing patient (partial update allowed) ---
class PatientUpdate(BaseModel):
    name: Annotated[str | None, None] = None  # Optional update
    email: Annotated[str | None, None] = None
    phone: Annotated[str | None, None] = None

# --- Schema for reading a patient (response model) ---
class Patient(PatientBase):
    id: int  # Auto-generated unique ID of the patient

    class Config:
        from_attributes = True  # Enable ORM-to-Pydantic conversion
