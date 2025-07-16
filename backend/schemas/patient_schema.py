# --- Import Pydantic for data validation ---
from pydantic import BaseModel

# --- Define the Patient schema ---
class PatientBase(BaseModel):
    name: str
    email: str
    phone: str | None = None  # Optional phone number

# --- Schema for creating a new patient ---
class PatientCreate(PatientBase):
    pass

# --- Schema for reading (output) a patient ---
class Patient(PatientBase):
    id: int

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy models
