# --- Import necessary SQLAlchemy components ---
from sqlalchemy import Column, Integer, ForeignKey, String, Date, Time
from sqlalchemy.orm import relationship
from ..db.database import Base

# --- Define Appointment model ---
class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    status = Column(String, default='scheduled')  # Can be 'scheduled', 'cancelled', 'rescheduled', etc.
    reason = Column(String)

    # --- Relationships ---
    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
