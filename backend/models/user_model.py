# ------------------------------------- External Imports -------------------------------------

# Importing required SQLAlchemy types for defining columns and data types  
from sqlalchemy import Column, Integer, String, JSON

# ------------------------------------- Internal Imports -------------------------------------

# Importing the base class for ORM models  
from ..db.base import Base

# ------------------------------------- User Model -------------------------------------

# Define the User model class which inherits from SQLAlchemy's Base  
class User(Base):
    """
    User model represents all users in the system including patients, doctors, and admins.
    """

    # Define the name of the table in the database  
    __tablename__ = 'users'

    # Primary key: unique ID for each user, auto-incremented  
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Name of the user (required)  
    name = Column(String, nullable=False)

    # Email address of the user (must be unique and not null)  
    email = Column(String, unique=True, nullable=False)

    # Role of the user (default is 'patient', can be 'doctor', 'admin', etc.)  
    role = Column(String, default="patient", nullable=False)

    # ---------------- Optional / Role-Specific Fields ----------------

    # Phone number of the user (optional)  
    phone_number = Column(String, nullable=True)

    # Google ID if signed in via Google OAuth (optional)  
    google_id = Column(String, nullable=True)

    # Specialization area for doctors (optional)  
    specialization = Column(String, nullable=True)

    # JSON structure to store available working days and time ranges for doctors (optional)  
    available_days = Column(JSON, nullable=True)

    # Duration (in minutes) for one appointment slot for doctors (optional)  
    slot_duration = Column(Integer, nullable=True)

    # Age of the user, typically for patients (optional)  
    age = Column(Integer, nullable=True)
