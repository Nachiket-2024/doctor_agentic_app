# --- Import necessary SQLAlchemy components ---
from sqlalchemy import Column, Integer, Boolean, Date, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..db.base import Base

class DoctorAvailability(Base):
    __tablename__ = 'doctor_availability'

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))  # ForeignKey referencing the doctor
    date = Column(Date, nullable=False)  # Availability date
    start_time = Column(Time, nullable=False)  # Available time slot (renamed from slot_time to start_time)
    is_booked = Column(Boolean, default=False)  # Is the slot booked

    doctor = relationship("Doctor", backref="availabilities")  # Relationship to Doctor model

    __table_args__ = (
        UniqueConstraint('doctor_id', 'date', 'start_time', name='unique_slot_per_day'),  # Ensure no duplicate slots
    )
