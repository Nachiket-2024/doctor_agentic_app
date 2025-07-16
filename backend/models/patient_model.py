# --- Import necessary SQLAlchemy components ---
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from ..db.database import Base

# --- Define Patient model ---
class Patient(Base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)

    # --- Relationship with appointments ---
    appointments = relationship("Appointment", back_populates="patient")
