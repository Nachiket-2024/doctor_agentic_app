from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from ..db.base import Base

class Patient(Base):
    __tablename__ = 'patients'  # Name of the table in the database

    id = Column(Integer, primary_key=True, index=True)  # Unique patient ID
    name = Column(String, index=True, nullable=False)  # Patient's full name, must be provided
    email = Column(String, unique=True, index=True, nullable=False)  # Unique email address, required
    google_id = Column(String, unique=True, index=True, nullable=True)  # Google ID, can be empty if not logged in via Google
    phone = Column(String, nullable=True)  # Optional phone number
    age = Column(Integer, nullable=True)  # Age of the patient, optional

    role = Column(String, default="patient")  # Set role as "patient" by default

    # Relationship with appointments
    appointments = relationship("Appointment", back_populates="patient")  # Link to appointments
