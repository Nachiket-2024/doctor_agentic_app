from pydantic import BaseModel, ConfigDict
from typing import Optional

# --- Base schema with shared fields for input/output ---
class PatientBase(BaseModel):
    name: str  # Full name of the patient
    email: str  # Email ID of the patient (must be unique)
    google_id: Optional[str] = None  # This will be populated by the backend, hence optional for create/update
    phone: Optional[str] = None  # Optional phone number
    age: Optional[int] = None
    role: str = "patient"

# --- Schema for creating a new patient ---
# No need to include google_id as it will be auto-filled in backend
class PatientCreate(PatientBase):
    google_id: Optional[str] = None  # Ensure this field is omitted in the frontend request

# --- Schema for updating an existing patient (partial update allowed) ---
class PatientUpdate(BaseModel):
    name: Optional[str] = None  # Optional update
    email: Optional[str] = None
    phone: Optional[str] = None
    google_id: Optional[str] = None  # Allow updating google_id if needed, although it's not common
    age: Optional[int] = None  # Optional age update

# --- Schema for reading a patient (response model) ---
class Patient(PatientBase):
    id: int  # Auto-generated unique ID of the patient

    class Config:
        from_attributes = True  # Enable ORM-to-Pydantic conversion
