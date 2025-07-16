# --- Import necessary SQLAlchemy components ---
from sqlalchemy import Column, Integer, ForeignKey, String, Date, Time  # For column types and constraints
from sqlalchemy.orm import relationship  # For defining relationships between tables
from ..db.base import Base  # Base class for all SQLAlchemy models

# --- Define the Appointment SQLAlchemy model ---
class Appointment(Base):
    __tablename__ = 'appointments'  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Unique ID for the appointment
    doctor_id = Column(Integer, ForeignKey('doctors.id'))  # Foreign key to doctors table
    patient_id = Column(Integer, ForeignKey('patients.id'))  # Foreign key to patients table
    date = Column(Date)  # Appointment date
    start_time = Column(Time)  # Start time of the appointment
    end_time = Column(Time)  # End time of the appointment
    status = Column(String, default='scheduled')  # Status like scheduled, cancelled, etc.
    reason = Column(String)  # Optional reason or notes for the appointment

    # --- Define relationships with Doctor and Patient models ---
    doctor = relationship("Doctor", back_populates="appointments")  # Link to Doctor model
    patient = relationship("Patient", back_populates="appointments")  # Link to Patient model
