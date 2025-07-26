# ------------------------------------- External Imports -------------------------------------

# Import BaseModel and ConfigDict for schema creation and ORM compatibility
from pydantic import BaseModel, ConfigDict

# ------------------------------------- Base Schema for Patient -------------------------------------

# Base schema containing common fields used in other schemas
class PatientBase(BaseModel):
    # Full name of the patient (required)
    name: str

    # Unique email address of the patient
    email: str

    # Optional phone number (can be None)
    phone_number: str | None = None

    # Optional age of the patient
    age: int | None = None

    # ---------------- Google OAuth Token Fields ----------------

    # Access token for Google Calendar or Gmail APIs
    access_token: str | None = None

    # Refresh token for renewing access token
    refresh_token: str | None = None

    # Expiry timestamp or ISO format string
    token_expiry: str | None = None

    # Enable ORM compatibility
    class Config(ConfigDict):
        from_attributes = True

# ------------------------------------- Schema for Creating Patient -------------------------------------

# Used when creating a new patient via API
class PatientCreate(PatientBase):
    # Inherits all fields from PatientBase for input validation
    pass

# ------------------------------------- Schema for Reading Patient -------------------------------------

# Schema used when returning patient data via API
class PatientRead(PatientBase):
    # Auto-generated unique identifier for the patient
    id: int

    # ORM configuration
    class Config(ConfigDict):
        from_attributes = True

# ------------------------------------- Schema for Updating Patient -------------------------------------

# Used when updating patient info (partial updates allowed)
class PatientUpdate(BaseModel):
    # Optional name update
    name: str | None = None

    # Optional email update
    email: str | None = None

    # Optional phone number update
    phone_number: str | None = None

    # Optional age update
    age: int | None = None

    # ---------------- Optional Google Token Updates ----------------

    # Optional access token update
    access_token: str | None = None

    # Optional refresh token update
    refresh_token: str | None = None

    # Optional token expiry update
    token_expiry: str | None = None

    # Enable ORM compatibility
    class Config(ConfigDict):
        from_attributes = True

# ------------------------------------- Schema for Patient Delete Response -------------------------------------

# Response schema used after successful patient deletion
class PatientDeleteResponse(BaseModel):
    # Message confirming deletion
    message: str

    # ID of the deleted patient
    patient_id: int
