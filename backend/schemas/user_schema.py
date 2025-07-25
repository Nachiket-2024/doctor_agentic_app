# ------------------------------------- External Imports -------------------------------------

# Import BaseModel for creating Pydantic schemas  
# Import EmailStr for validating email addresses  
# Import ConfigDict for schema configuration  
from pydantic import BaseModel, EmailStr, ConfigDict

# ------------------------------------- User Base Schema -------------------------------------

# Base schema containing common user fields  
class UserBase(BaseModel):
    # User's full name (required)  
    name: str

    # User's email address, validated as email (required)  
    email: EmailStr

    # Role of the user, e.g., 'doctor', 'patient', 'admin' (required)  
    role: str

    # Optional phone number of the user (nullable)  
    phone_number: str | None = None

    # Optional Google ID associated with the user (nullable)  
    google_id: str | None = None

    # Optional specialization (applicable for doctors) (nullable)  
    specialization: str | None = None

    # Optional JSON structure with available days and time slots (nullable)  
    available_days: dict | None = None

    # Optional slot duration in minutes (nullable)  
    slot_duration: int | None = None

    # Optional age of the user (nullable)  
    age: int | None = None

    # Enable ORM parsing for SQLAlchemy models  
    class Config(ConfigDict):
        from_attributes = True

# ------------------------------------- User Creation Schema -------------------------------------

# Schema for creating a new user  
class UserCreate(UserBase):
    # Inherits all fields from UserBase  
    pass

# ------------------------------------- User Update Schema -------------------------------------

# Schema for updating an existing user (all fields optional)  
class UserUpdate(BaseModel):
    # Optional updated name  
    name: str | None = None

    # Optional updated email  
    email: EmailStr | None = None

    # Optional updated role  
    role: str | None = None

    # Optional updated phone number  
    phone_number: str | None = None

    # Optional updated Google ID  
    google_id: str | None = None

    # Optional updated specialization  
    specialization: str | None = None

    # Optional updated available days dictionary  
    available_days: dict | None = None

    # Optional updated slot duration  
    slot_duration: int | None = None

    # Optional updated age  
    age: int | None = None

    # Enable ORM parsing for SQLAlchemy models  
    class Config(ConfigDict):
        from_attributes = True

# ------------------------------------- User Response Schema -------------------------------------

# Schema used for returning user data in responses  
class UserResponse(UserBase):
    # User ID field to include in response  
    id: int

    # Enable ORM parsing for SQLAlchemy models  
    class Config(ConfigDict):
        from_attributes = True
