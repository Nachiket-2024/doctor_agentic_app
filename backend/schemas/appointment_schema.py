# ------------------------------------- External Imports -------------------------------------
# Import BaseModel and ConfigDict for Pydantic schema creation and configuration  
from pydantic import BaseModel, ConfigDict

# Import datetime module to handle date and time fields  
import datetime

# Import Annotated type hinting utility for optional fields  
from typing import Annotated

# ------------------------------------- Base Schema for Appointment -------------------------------------
# Define shared schema fields for appointment creation and reading  
class AppointmentBase(BaseModel):
    # ID of the doctor assigned to the appointment (required)  
    doctor_id: int

    # ID of the patient for the appointment (required)  
    patient_id: int

    # Date of the appointment (required)  
    date: datetime.date

    # Start time of the appointment (required)  
    start_time: datetime.time

    # Optional end time of appointment  
    end_time: Annotated[datetime.time | None, None] = None

    # Status of the appointment (default: 'scheduled')  
    status: str = 'scheduled'

    # Optional reason or notes for the appointment  
    reason: Annotated[str | None, None] = None

    # Optional Google Calendar event ID for calendar syncing  
    event_id: Annotated[str | None, None] = None

# ------------------------------------- Schema for Creating Appointments -------------------------------------
# Schema used when creating a new appointment  
class AppointmentCreate(AppointmentBase):
    # Inherits all fields from AppointmentBase  
    pass

# ------------------------------------- Schema for Updating Appointments -------------------------------------
# Schema used for updating existing appointments (all fields optional)  
class AppointmentUpdate(BaseModel):
    # Optional update to doctor ID  
    doctor_id: Annotated[int | None, None] = None

    # Optional update to patient ID  
    patient_id: Annotated[int | None, None] = None

    # Optional update to appointment date  
    date: Annotated[datetime.date | None, None] = None

    # Optional update to start time  
    start_time: Annotated[datetime.time | None, None] = None

    # Optional update to end time  
    end_time: Annotated[datetime.time | None, None] = None

    # Optional update to appointment status  
    status: Annotated[str | None, None] = None

    # Optional update to appointment reason  
    reason: Annotated[str | None, None] = None

    # Optional update to Google Calendar event ID  
    event_id: Annotated[str | None, None] = None

# ------------------------------------- Schema for Reading Appointments -------------------------------------
# Schema used to return appointment data in API responses  
class AppointmentResponse(AppointmentBase):
    # Auto-generated unique ID of the appointment  
    id: int

    # Enable compatibility with ORM models (e.g., SQLAlchemy)  
    class Config(ConfigDict):
        from_attributes = True
