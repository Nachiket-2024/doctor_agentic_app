# --- Import necessary SQLAlchemy components ---
from sqlalchemy import Column, String, Integer  # Column types
from sqlalchemy.orm import relationship  # To define model relationships
from ..db.base import Base  # Base declarative class from your DB config

# --- Define the Patient model ---
class Patient(Base):
    __tablename__ = 'patients'  # Name of the table in the database

    id = Column(Integer, primary_key=True, index=True)  # Unique patient ID
    name = Column(String, index=True)  # Patient's full name
    email = Column(String, unique=True, index=True)  # Unique email address
    phone = Column(String, nullable=True)  # Optional phone number

    # --- Relationship with appointments ---
    appointments = relationship("Appointment", back_populates="patient")  # Link to appointments
