# ------------------------------------- External Imports -------------------------------------
# Required SQLAlchemy column types for table definitions
from sqlalchemy import Column, Integer, String

# ------------------------------------- Internal Imports -------------------------------------
# Import base ORM model for table inheritance
from ..db.base import Base

# ------------------------------------- Patient Model -------------------------------------
# Define the Patient model class inheriting from SQLAlchemy Base
class Patient(Base):
    """
    Patient model for storing patient-specific user information,
    including Google integration fields for Calendar/Gmail access.
    """

    # Name of the table in the database
    __tablename__ = 'patients'

    # Primary key: unique ID for each patient (auto-incremented)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Full name of the patient (required field)
    name = Column(String, nullable=False)

    # Unique email address for the patient (used for login and identification)
    email = Column(String, unique=True, nullable=False)

    # Optional phone number for the patient
    phone_number = Column(String, nullable=True)

    # Age of the patient (optional)
    age = Column(Integer, nullable=True)

    # ---------------- Google OAuth Token Fields ----------------
    # Access token for authorized Google API requests (required after OAuth login)
    access_token = Column(String, nullable=True)

    # Refresh token to obtain new access tokens when the current one expires
    refresh_token = Column(String, nullable=True)

    # Optional ISO 8601 timestamp string representing token expiry time
    token_expiry = Column(String, nullable=True)
