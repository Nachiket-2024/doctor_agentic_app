# ------------------------------------- External Imports -------------------------------------
# Import BaseModel and ConfigDict for schema creation and ORM compatibility
from pydantic import BaseModel, ConfigDict

# ------------------------------------- Base Schema for Doctor -------------------------------------
# Base schema containing fields shared across other schemas
class DoctorBase(BaseModel):
    # Full name of the doctor (required)
    name: str

    # Unique email address of the doctor (required)
    email: str

    # Optional phone number for contact
    phone_number: str | None = None

    # Specialization or medical department
    specialization: str | None = None

    # Weekly availability schedule as JSON, e.g., {"mon": ["09:00-12:00", "14:00-17:00"]}
    available_days: dict | None = None

    # Duration (in minutes) for each appointment
    slot_duration: int | None = None

    # Precomputed weekly time slots per weekday, e.g., {"mon": ["09:00", "09:30"], "tue": [...]}
    weekly_available_slots: dict | None = None

    # ---------------- Google OAuth Token Fields ----------------
    # Access token to authorize Google Calendar or Gmail APIs
    access_token: str | None = None

    # Refresh token to obtain a new access token
    refresh_token: str | None = None

    # Expiry time of token (ISO 8601 format)
    token_expiry: str | None = None

    # Enable ORM compatibility
    class Config(ConfigDict):
        from_attributes = True

# ------------------------------------- Schema for Creating Doctor -------------------------------------
# Schema used when creating a new doctor via API
class DoctorCreate(DoctorBase):
    # Inherits all fields from DoctorBase
    pass

# ------------------------------------- Schema for Reading Doctor -------------------------------------
# Schema used when reading doctor data from the database or returning from API
class DoctorRead(DoctorBase):
    # Unique doctor ID assigned by the database
    id: int

    # ORM compatibility configuration
    class Config(ConfigDict):
        from_attributes = True

# ------------------------------------- Schema for Updating Doctor -------------------------------------
# Schema used for partial updates of doctor fields
class DoctorUpdate(BaseModel):
    # Optional updated full name
    name: str | None = None

    # Optional updated email
    email: str | None = None

    # Optional updated phone number
    phone_number: str | None = None

    # Optional updated specialization
    specialization: str | None = None

    # Optional updated availability (JSON format)
    available_days: dict | None = None

    # Optional updated appointment duration
    slot_duration: int | None = None

    # Optional updated precomputed weekly slots per weekday
    weekly_available_slots: dict | None = None

    # Optional updated Google access token
    access_token: str | None = None

    # Optional updated refresh token
    refresh_token: str | None = None

    # Optional updated token expiry time
    token_expiry: str | None = None

    # ORM compatibility configuration
    class Config(ConfigDict):
        from_attributes = True

# ------------------------------------- Schema for Doctor Deletion Response -------------------------------------
# Schema returned when a doctor is successfully deleted
class DoctorDeleteResponse(BaseModel):
    # Message confirming the deletion
    message: str

    # ID of the deleted doctor
    doctor_id: int
