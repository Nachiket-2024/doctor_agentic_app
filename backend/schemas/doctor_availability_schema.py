from pydantic import BaseModel
from datetime import date, time

class DoctorAvailabilityBase(BaseModel):
    date: date  # Date of the slot
    start_time: time  # Start time of the slot
    is_booked: bool = False  # Default is False, indicating slot is available

    class Config:
        orm_mode = True  # This tells Pydantic to work with SQLAlchemy models


class DoctorAvailabilityResponse(DoctorAvailabilityBase):
    doctor_id: int  # Doctor ID to which the availability belongs

    class Config:
        orm_mode = True


class DoctorAvailabilityCreate(DoctorAvailabilityBase):
    # This class is for creating new slots, you don't need to provide 'doctor_id' for this.
    pass
