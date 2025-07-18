# --- Import necessary SQLAlchemy components ---
from sqlalchemy import Column, String, Integer, JSON  # Column types including JSON for availability
from sqlalchemy.orm import relationship  # For defining ORM relationships
from ..db.base import Base  # SQLAlchemy base model

# --- Define Doctor model ---
class Doctor(Base):
    __tablename__ = 'doctors'  # Database table name

    id = Column(Integer, primary_key=True, index=True)  # Unique doctor ID
    name = Column(String, index=True)  # Doctor's full name
    specialization = Column(String, index=True)  # Doctor's field of specialization
    available_days = Column(JSON)  # JSON structure to store available days & slots
    slot_duration = Column(Integer, default=30)  # Duration per appointment in minutes (default: 30)
    email = Column(String, unique=True, index=True)  # Doctor's email
    phone_number = Column(String, nullable=True)  # Optional phone number
    google_id = Column(String, unique=True, nullable=True)  # Google ID (added field)

    # --- Add role to Doctor ---
    role = Column(String, default="doctor")

    # --- Relationship with appointments ---
    appointments = relationship("Appointment", back_populates="doctor")  # Link to Appointment model
