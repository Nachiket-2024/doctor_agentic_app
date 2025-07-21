# --- Import Pydantic base class and typing tools ---
from pydantic import BaseModel, EmailStr, ConfigDict

# --- Unified schema for users (Doctor or Patient) ---
class UserBase(BaseModel):
    name: str  # User's full name
    email: EmailStr  # User's email (must be valid format)
    role: str  # Role can be 'doctor' or 'patient'
    
    # Optional fields, all are nullable (None by default)
    phone_number: str = None  # Phone number (optional)
    google_id: str = None  # Google ID (optional)
    specialization: str = None  # Doctor's specialization (optional)
    available_days: str = None  # Available days and time slots (optional)
    slot_duration: int = None  # Slot duration for doctors (optional)
    age: int = None  # Patient's age (optional)

    class Config(ConfigDict):
        from_attributes = True  # Enables compatibility with ORM objects

# Schema for creating a new user
class UserCreate(UserBase):
    # Additional fields for creating a user can be added here (currently inheriting UserBase)
    pass

# Schema for returning user data (read-only, might exclude sensitive fields)
class UserResponse(UserBase):
    id: int  # Adding the ID field, as it's returned in the response

    # Pydantic's method to convert the model into a dictionary (optional)
    class Config(ConfigDict):
        from_attributes = True  # Enables compatibility with ORM objects
