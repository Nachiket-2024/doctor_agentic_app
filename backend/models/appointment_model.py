from sqlalchemy import Column, Integer, ForeignKey, String, Date, Time  # For column types and constraints
from sqlalchemy.orm import relationship  # For defining relationships between tables
from ..db.base import Base  # Base class for all SQLAlchemy models

# --- Define the Appointment SQLAlchemy model ---
class Appointment(Base):
    __tablename__ = 'appointments'  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Unique ID for the appointment
    doctor_id = Column(Integer, ForeignKey('users.id'))  # Foreign key to users table (doctor)
    patient_id = Column(Integer, ForeignKey('users.id'))  # Foreign key to users table (patient)
    date = Column(Date)  # Appointment date
    start_time = Column(Time)  # Start time of the appointment
    end_time = Column(Time, nullable=True)  # End time of the appointment (nullable)
    status = Column(String, default='scheduled')  # Status like scheduled, cancelled, etc.
    reason = Column(String)  # Optional reason or notes for the appointment

    # --- Define relationships with User model ---
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="appointments")  # Link to doctor
    patient = relationship("User", foreign_keys=[patient_id], back_populates="appointments")  # Link to patient

    # --- Custom validation to ensure correct roles ---
    @property
    def is_valid_appointment(self):
        # Ensure one is a doctor and the other is a patient
        return self.doctor.role == "doctor" and self.patient.role == "patient"
