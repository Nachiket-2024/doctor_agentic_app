# --- Import Pydantic for data validation ---
from pydantic import BaseModel
from datetime import date, time

# --- Define the Appointment schema ---
class AppointmentBase(BaseModel):
    doctor_id: int
    patient_id: int
    date: date
    start_time: time
    end_time: time
    status: str = 'scheduled'  # Default status is 'scheduled'
    reason: str | None = None  # Optional field using `| None`

# --- Schema for creating a new appointment ---
class AppointmentCreate(AppointmentBase):
    pass

# --- Schema for reading (output) an appointment ---
class Appointment(AppointmentBase):
    id: int

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy models
