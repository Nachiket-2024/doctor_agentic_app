# ------------------------------------- External Imports -------------------------------------

# Required SQLAlchemy column types for table definitions
from sqlalchemy import Column, Integer, String, JSON

# ------------------------------------- Internal Imports -------------------------------------

# Import base ORM model for table inheritance
from ..db.base import Base

# ------------------------------------- Doctor Model -------------------------------------

# Define the Doctor model class inheriting from SQLAlchemy Base
class Doctor(Base):
    """
    Doctor model for storing doctor-specific user information, 
    including Google integration fields and weekly slot metadata.
    """

    # Name of the table in the database
    __tablename__ = 'doctors'

    # Primary key: unique ID for each doctor (auto-incremented)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Full name of the doctor (required field)
    name = Column(String, nullable=False)

    # Unique email address for the doctor (used for login and identification)
    email = Column(String, unique=True, nullable=False)

    # Optional phone number for the doctor
    phone_number = Column(String, nullable=True)

    # Medical specialization or department (e.g., Cardiology, Dermatology)
    specialization = Column(String, nullable=True)

    # Weekly availability schedule in JSON format 
    # Example: {"mon": ["09:00-12:00", "14:00-17:00"], "tue": [...], ...}
    available_days = Column(JSON, nullable=True)

    # Appointment duration in minutes (used for slot interval calculations)
    slot_duration = Column(Integer, nullable=True)

    # Precomputed weekly slot start times in JSON format for each weekday
    # Example: {"mon": ["09:00", "09:30", "10:00"], "tue": ["10:00", ...], ...}
    weekly_available_slots = Column(JSON, nullable=True)

    # ---------------- Google OAuth Token Fields ----------------

    # Access token for authorized Google API requests (set after Google login)
    access_token = Column(String, nullable=True)

    # Refresh token to obtain new access tokens when the current one expires
    refresh_token = Column(String, nullable=True)

    # Optional ISO 8601 timestamp string representing token expiry time
    token_expiry = Column(String, nullable=True)
