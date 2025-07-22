# --- Import Pydantic base class and typing tools ---
from pydantic import BaseModel, EmailStr, ConfigDict  # Import Pydantic model types

# --- Unified schema for users (Doctor or Patient) ---
class UserBase(BaseModel):
    name: str  # User's full name
    email: EmailStr  # Valid email address
    role: str  # Either 'doctor' or 'patient'

    # Optional fields explicitly allowing None values
    phone_number: str | None = None  # Optional phone number
    google_id: str | None = None  # Optional Google ID
    specialization: str | None = None  # Optional specialization (for doctors)
    available_days: str | None = None  # Optional availability (for doctors)
    slot_duration: int | None = None  # Optional slot duration (for doctors)
    age: int | None = None  # Optional age (for patients)

    # Enables ORM object parsing
    class Config(ConfigDict):
        from_attributes = True

# Schema for user creation (same fields, no need to change)
class UserCreate(UserBase):
    pass

# Schema for returning user data (must allow nullable values)
class UserResponse(UserBase):
    id: int  # Include user ID in response

    class Config(ConfigDict):
        from_attributes = True
