# --- Import necessary SQLAlchemy components ---
from sqlalchemy import Column, String, Integer, JSON
from sqlalchemy.orm import relationship
from ..db.database import Base

# --- Define Doctor model ---
class Doctor(Base):
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialization = Column(String, index=True)
    available_days = Column(JSON)  # JSON for storing availability schedule
    slot_duration = Column(Integer, default=30)  # Default to 30 minutes per slot

    # --- Relationship with appointments ---
    appointments = relationship("Appointment", back_populates="doctor")
