from fastapi import APIRouter, HTTPException, Depends, Query  # Import necessary modules for routing, exceptions, and query parameters
from sqlalchemy.orm import Session  # For managing database sessions
from datetime import date  # For working with dates

# --- Import models and schemas ---
from ..models.doctor_model import Doctor  # Doctor DB model for doctor data
from ..models.patient_model import Patient  # Patient DB model for patient data
from ..schemas.doctor_schema import (
    DoctorCreate,  # Schema for creating a new doctor
    DoctorUpdate,  # Schema for updating doctor details
    Doctor as DoctorSchema  # Schema for representing doctor in API responses
)

from ..auth.auth_config import ADMIN_EMAILS  # Admin email list (imported from .env)
from ..auth.auth_routes import get_current_user_from_cookie  # Function to get current user from cookies

# --- Import database session provider ---
from ..db.session import get_db  # SQLAlchemy session for DB access

from ..utils.doctor_availability_generator import get_doctor_availability  # Function to get doctor availability

# Create a router to group all /doctors endpoints together
router = APIRouter(prefix="/doctors", tags=["Doctors"])  # Define the base path and the tag for doctor-related routes

# --- Create a new doctor (accessible only by admin) ---
@router.post("/", response_model=DoctorSchema)  # POST request to create a new doctor
def create_doctor(
    doctor: DoctorCreate,  # Data model for creating a new doctor
    db: Session = Depends(get_db),  # Dependency injection for DB session
    current_user: Doctor | Patient | str = Depends(get_current_user_from_cookie)  # Dependency injection for current user
):
    # Use the first admin email from the list (since you have only one admin)
    admin_email = ADMIN_EMAILS[0]

    # Check if current_user is the admin (i.e., 'admin' string) or if the email matches the admin's
    if current_user == "admin" or (isinstance(current_user, Doctor) and current_user.email == admin_email):
        db_doctor = Doctor(**doctor.model_dump())  # Create a new doctor object using the provided data
        db.add(db_doctor)  # Add the doctor object to the DB session
        db.commit()  # Commit the changes to the database
        db.refresh(db_doctor)  # Refresh the DB object to get the latest state
        return db_doctor  # Return the created doctor object
    
    raise HTTPException(status_code=403, detail="Access denied. Only admins can create doctors.")  # If not an admin, deny access


# --- Get all doctors (accessible by anyone) ---
@router.get("/", response_model=list[DoctorSchema])  # GET request to fetch all doctors
def get_doctors(db: Session = Depends(get_db), current_user: Doctor | Patient = Depends(get_current_user_from_cookie)):
    doctors = db.query(Doctor).all()  # Query the database for all doctors
    return doctors  # Return the list of doctors


# --- Get a doctor by ID (accessible by anyone) ---
@router.get("/{doctor_id}", response_model=DoctorSchema)  # GET request to fetch a specific doctor by ID
def get_doctor(
    doctor_id: int,  # The doctor ID to search for
    db: Session = Depends(get_db),  # DB session (dependency injection)
    current_user: Doctor | Patient = Depends(get_current_user_from_cookie)  # Current user (based on cookies)
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()  # Query the database for the doctor by ID
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")  # If doctor doesn't exist, raise error
    return doctor  # Return the doctor object


# --- Update an existing doctor (accessible only by admin) ---
@router.put("/{doctor_id}", response_model=DoctorSchema)  # PUT request to update a doctor by ID
def update_doctor(
    doctor_id: int,  # Doctor ID to be updated
    updated: DoctorUpdate,  # Updated doctor data
    db: Session = Depends(get_db),  # DB session (dependency injection)
    current_user: Doctor | Patient | str = Depends(get_current_user_from_cookie)  # Current user (can be doctor, patient, or admin)
):
    # Use the first admin email from the list (since you have only one admin)
    admin_email = ADMIN_EMAILS[0]

    # Check if current_user is the admin or if the email matches the admin's
    if current_user == "admin" or (isinstance(current_user, Doctor) and current_user.email == admin_email):
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()  # Find the doctor in the DB
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")  # If doctor doesn't exist, raise error

        # Update the doctor with the provided data
        for key, value in updated.model_dump(exclude_unset=True).items():
            setattr(doctor, key, value)  # Update doctor attributes

        db.commit()  # Commit the changes to the DB
        db.refresh(doctor)  # Refresh the doctor object to get the latest DB state
        return doctor  # Return the updated doctor object
    
    raise HTTPException(status_code=403, detail="Access denied. Only admins can update doctors.")  # If not an admin, deny access


# --- Delete a doctor (accessible only by admin) ---
@router.delete("/{doctor_id}")  # DELETE request to delete a doctor by ID
def delete_doctor(
    doctor_id: int,  # The doctor ID to be deleted
    db: Session = Depends(get_db),  # DB session (dependency injection)
    current_user: Doctor | Patient | str = Depends(get_current_user_from_cookie)  # Current user (can be doctor, patient, or admin)
):
    # Use the first admin email from the list (since you have only one admin)
    admin_email = ADMIN_EMAILS[0]

    # Check if current_user is the admin or if the email matches the admin's
    if current_user == "admin" or (isinstance(current_user, Doctor) and current_user.email == admin_email):
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()  # Find the doctor in the DB
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")  # If doctor doesn't exist, raise error
        
        db.delete(doctor)  # Delete the doctor from the DB session
        db.commit()  # Commit the changes to the DB

        return {"detail": "Doctor deleted"}  # Return success message
    
    raise HTTPException(status_code=403, detail="Access denied. Only admins can delete doctors.")  # If not an admin, deny access

# Route to get available slots for a doctor on a given date
@router.get("/{doctor_id}/availability", response_model=list[str])
def check_doctor_availability(doctor_id: int, date: date, db: Session = Depends(get_db)):
    """
    Get available time slots for the doctor on a given date.
    
    :param doctor_id: The ID of the doctor.
    :param date: The date to check availability.
    :param db: Database session (injected).
    :return: List of available time slots.
    """
    # Call the function to get available slots
    available_slots = get_doctor_availability(doctor_id, date, db)
    
    if not available_slots:
        raise HTTPException(status_code=404, detail="No available slots found.")
    
    return available_slots