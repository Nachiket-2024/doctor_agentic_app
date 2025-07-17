# --- Import necessary classes for data validation and datetime manipulation ---
from pydantic import BaseModel, field_validator, ConfigDict  # For Pydantic schema models and custom validation
import datetime  # Use full datetime module to avoid name conflicts with 'date' or 'time'
from typing import Annotated  # For optional field annotation (modern replacement for Optional)

# --- Shared schema: base structure for appointments used across create/read ---
class AppointmentBase(BaseModel):
    doctor_id: int  # ID of the doctor for the appointment
    patient_id: int  # ID of the patient
    date: datetime.date  # Date of the appointment
    start_time: datetime.time  # Start time of the appointment
    end_time: Annotated[datetime.time | None, None] = None  # Optional end time; auto-filled if not provided
    status: str = 'scheduled'  # Appointment status (default is 'scheduled')
    reason: Annotated[str | None, None] = None  # Optional reason or notes

    # --- Validator: automatically sets end_time = start_time + 30 minutes if not given ---
    @field_validator('end_time', mode='before')
    @classmethod
    def ensure_end_time(cls, v, values):
        if v is None and 'start_time' in values and 'date' in values:
            start = datetime.datetime.combine(values['date'], values['start_time'])
            return (start + datetime.timedelta(minutes=30)).time()
        return v

# --- Schema for creating a new appointment (used in POST) ---
class AppointmentCreate(AppointmentBase):
    pass  # No new fields needed — same as base

# --- Schema for updating existing appointments (used in PUT/PATCH) ---
class AppointmentUpdate(BaseModel):
    doctor_id: Annotated[int | None, None] = None  # Optional update to doctor_id
    patient_id: Annotated[int | None, None] = None  # Optional update to patient_id
    date: Annotated[datetime.date | None, None] = None  # Optional update to date
    start_time: Annotated[datetime.time | None, None] = None  # Optional update to start_time
    end_time: Annotated[datetime.time | None, None] = None  # Optional update to end_time
    status: Annotated[str | None, None] = None  # Optional update to status
    reason: Annotated[str | None, None] = None  # Optional update to reason

    # --- Validator: also auto-set end_time during update if missing ---
    @field_validator('end_time', mode='before')
    @classmethod
    def ensure_end_time(cls, v, values):
        if v is None and 'start_time' in values and 'date' in values:
            start = datetime.datetime.combine(values['date'], values['start_time'])
            return (start + datetime.timedelta(minutes=30)).time()
        return v

# --- Schema for reading appointment details (used in GET responses) ---
class Appointment(AppointmentBase):
    id: int  # Auto-incrementing ID of the appointment

    class Config(ConfigDict):
        from_attributes = True  # Enable ORM compatibility with SQLAlchemy models
