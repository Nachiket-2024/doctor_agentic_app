from pydantic import BaseModel, field_validator, ConfigDict
import datetime
from typing import Annotated

# Base model for Appointment
class AppointmentBase(BaseModel):
    doctor_id: int  # ID of the doctor for the appointment
    patient_id: int  # ID of the patient
    date: datetime.date  # Date of the appointment
    start_time: datetime.time  # Start time of the appointment
    end_time: Annotated[datetime.time | None, None] = None  # Optional end time; auto-filled if not provided
    status: str = 'scheduled'  # Appointment status (default is 'scheduled')
    reason: Annotated[str | None, None] = None  # Optional reason or notes

# Schema for creating appointments
class AppointmentCreate(AppointmentBase):
    pass  # Inherits the same structure as AppointmentBase for creating appointments

# Schema for updating existing appointments
class AppointmentUpdate(BaseModel):
    doctor_id: Annotated[int | None, None] = None  # Optional update to doctor_id
    patient_id: Annotated[int | None, None] = None  # Optional update to patient_id
    date: Annotated[datetime.date | None, None] = None  # Optional update to date
    start_time: Annotated[datetime.time | None, None] = None  # Optional update to start_time
    end_time: Annotated[datetime.time | None, None] = None  # Optional update to end_time
    status: Annotated[str | None, None] = None  # Optional update to status
    reason: Annotated[str | None, None] = None  # Optional update to reason

# Schema for reading appointment data (with appointment ID) for response
class AppointmentResponse(AppointmentBase):
    id: int  # Auto-incrementing ID of the appointment

    class Config(ConfigDict):
        from_attributes = True  # To allow Pydantic models to work with SQLAlchemy models
