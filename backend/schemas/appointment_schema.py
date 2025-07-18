from pydantic import BaseModel, field_validator, ConfigDict
import datetime
from typing import Annotated

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
    def ensure_end_time(cls, v, values: dict):
        if v is None:
            # Accessing values directly from the 'values' dictionary
            start_time = values.get('start_time')  # Accessing values from the dict
            date = values.get('date')

            if start_time and date:
                start = datetime.datetime.combine(date, start_time)
                return (start + datetime.timedelta(minutes=30)).time()

        return v

class AppointmentCreate(AppointmentBase):
    pass  # Inherits the same structure as AppointmentBase for creating appointments

class AppointmentUpdate(BaseModel):
    doctor_id: Annotated[int | None, None] = None  # Optional update to doctor_id
    patient_id: Annotated[int | None, None] = None  # Optional update to patient_id
    date: Annotated[datetime.date | None, None] = None  # Optional update to date
    start_time: Annotated[datetime.time | None, None] = None  # Optional update to start_time
    end_time: Annotated[datetime.time | None, None] = None  # Optional update to end_time
    status: Annotated[str | None, None] = None  # Optional update to status
    reason: Annotated[str | None, None] = None  # Optional update to reason

    @field_validator('end_time', mode='before')
    @classmethod
    def ensure_end_time(cls, v, values: dict):
        if v is None:
            # Accessing values directly from the 'values' dictionary
            start_time = values.get('start_time')  # Accessing values from the dict
            date = values.get('date')

            if start_time and date:
                start = datetime.datetime.combine(date, start_time)
                return (start + datetime.timedelta(minutes=30)).time()

        return v

class Appointment(AppointmentBase):
    id: int  # Auto-incrementing ID of the appointment

    class Config(ConfigDict):
        from_attributes = True  # Enable ORM compatibility with SQLAlchemy models
