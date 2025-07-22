# Importing necessary SQLAlchemy classes
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

# Importing Base class from the db.base module
from ..db.base import Base

class User(Base):
    # The table name in the database
    __tablename__ = 'users'
    
    # Unique ID for the user (primary key)
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User's name (cannot be null)
    name = Column(String, nullable=False)
    
    # User's email (must be unique, cannot be null)
    email = Column(String, unique=True, nullable=False)
    
    # User's role (default to 'patient', can be 'doctor', 'patient', 'admin', etc.)
    role = Column(String, default="patient", nullable=False)
    
    # Optional fields, defaulting to None if not provided
    phone_number = Column(String, nullable=True)  # Optional phone number
    google_id = Column(String, nullable=True)  # Optional Google ID
    specialization = Column(String, nullable=True)  # Optional, specific to doctors
    available_days = Column(String, nullable=True)  # Optional, time slots for doctors
    slot_duration = Column(Integer, nullable=True)  # Optional, slot duration for doctors
    age = Column(Integer, nullable=True)  # Optional, age for patients
