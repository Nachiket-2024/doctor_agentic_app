from sqlalchemy import Column, Integer, ForeignKey, String, Date, Time
from sqlalchemy.orm import relationship
from ..db.base import Base  # Base class for all SQLAlchemy models
from .user_model import User

class Appointment(Base):
    __tablename__ = 'appointments'  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Unique ID for the appointment
    doctor_id = Column(Integer, ForeignKey(User.id))  # Foreign key to users table (doctor)
    patient_id = Column(Integer, ForeignKey(User.id))  # Foreign key to users table (patient)
    date = Column(Date)  # Appointment date
    start_time = Column(Time)  # Start time of the appointment
    end_time = Column(Time, nullable=True)  # End time of the appointment (nullable)
    status = Column(String, default='scheduled')  # Status like scheduled, cancelled, etc.
    reason = Column(String)  # Optional reason or notes for the appointment

    # --- Define relationships with User model ---
    doctor = relationship("User", foreign_keys=[doctor_id])  # Link to doctor
    patient = relationship("User", foreign_keys=[patient_id])  # Link to patient
