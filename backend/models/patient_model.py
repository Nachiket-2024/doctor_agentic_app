from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from ..db.base import Base

class Patient(Base):
    __tablename__ = 'patients'  # Name of the table in the database

    id = Column(Integer, primary_key=True, index=True)  # Unique patient ID
    name = Column(String, index=True)  # Patient's full name
    email = Column(String, unique=True, index=True)  # Unique email address
    google_id = Column(String, unique=True, index=True)  # Google ID
    phone = Column(String, nullable=True)  # Optional phone number
    age = Column(Integer)  # Age of the patient

    # Relationship with appointments
    appointments = relationship("Appointment", back_populates="patient")  # Link to appointments
