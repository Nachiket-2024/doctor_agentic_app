# ------------------------------------- External Imports -------------------------------------

# Import necessary SQLAlchemy column types for defining model attributes  
from sqlalchemy import Column, Integer, ForeignKey, String, Date, Time

# Import relationship function for ORM relationship mapping between tables  
from sqlalchemy.orm import relationship

# ------------------------------------- Internal Imports -------------------------------------

# Import the base class that all SQLAlchemy models inherit from  
from ..db.base import Base

# Import the Patient model to link appointments to patients  
from .patient_model import Patient

# Import the Doctor model to link appointments to doctors  
from .doctor_model import Doctor

# ------------------------------------- Appointment Model -------------------------------------

# Define the Appointment model class that inherits from Base  
class Appointment(Base):

    # Define the table name in the database for this model  
    __tablename__ = 'appointments'

    # Primary key column uniquely identifying each appointment record  
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key referencing the doctor’s user ID in the doctors table  
    doctor_id = Column(Integer, ForeignKey(Doctor.id))

    # Foreign key referencing the patient’s user ID in the patients table  
    patient_id = Column(Integer, ForeignKey(Patient.id))

    # Date column storing the appointment date  
    date = Column(Date)

    # Time column storing the appointment start time  
    start_time = Column(Time)

    # Time column storing the appointment end time (nullable if unknown)  
    end_time = Column(Time, nullable=True)

    # String column to store status of appointment (default is 'scheduled')  
    status = Column(String, default='scheduled')

    # Optional string column to store the reason or notes for the appointment  
    reason = Column(String)

    # Optional string column to store the Google Calendar event ID for syncing  
    event_id = Column(String, nullable=True)

    # --------------------- ORM Relationships ---------------------

    # Relationship to access doctor details via doctor_id foreign key  
    doctor = relationship("Doctor", foreign_keys=[doctor_id])

    # Relationship to access patient details via patient_id foreign key  
    patient = relationship("Patient", foreign_keys=[patient_id])
