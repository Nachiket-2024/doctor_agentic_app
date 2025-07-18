from fastapi import APIRouter, HTTPException, Depends  # Routing and error handling
from sqlalchemy.orm import Session  # DB session management

# Import patient model and schemas
from ..models.patient_model import Patient  # Import the Patient DB model
from ..schemas.patient_schema import (
    PatientCreate,  # Schema for creating a new patient
    PatientUpdate,  # Schema for updating patient details
    Patient as PatientSchema  # Schema for representing the patient in the API response
)

# Import database session provider
from ..db.session import get_db  # Function to get the database session

# Import the function to get the current user (and their role) from the cookie
from ..auth.auth_routes import get_current_user_from_cookie  # Assuming this function is in auth_routes

# Import admin emails from .env
from ..auth.auth_config import ADMIN_EMAILS  # Admin email list (from environment)

# Define router with prefix and tag
router = APIRouter(prefix="/patients", tags=["Patients"])  # Creating a new router for patient-related routes

# Create a new patient (admins can create any patient, patients can create their own profile)
@router.post("/", response_model=PatientSchema)  # POST request to create a new patient
def create_patient(
    patient: PatientCreate,  # Patient data to create a new patient (from the client)
    db: Session = Depends(get_db),  # DB session (dependency injection)
    current_user: Patient = Depends(get_current_user_from_cookie)  # Current user (based on cookie)
):
    # Use the first admin email from the list (since you have only one admin)
    admin_email = ADMIN_EMAILS[0]

    # Check if current_user is admin or the user is creating their own profile
    if isinstance(current_user, str) and current_user == "admin":
        # Admin can create any patient
        db_patient = Patient(**patient.model_dump())  # Create the patient object using the schema data
        db.add(db_patient)  # Add to DB session
        db.commit()  # Commit changes
        db.refresh(db_patient)  # Refresh to get the latest DB state
        return db_patient  # Return the created patient
    elif current_user.email == admin_email or current_user.id == patient.id:
        # Patients can only create their own profile, admins can create any patient
        db_patient = Patient(**patient.model_dump())  # Create the patient object using the schema data
        db.add(db_patient)  # Add to DB session
        db.commit()  # Commit changes
        db.refresh(db_patient)  # Refresh to get the latest DB state
        return db_patient  # Return the created patient
    else:
        raise HTTPException(status_code=403, detail="Access denied. You can only create your own profile.")

# Update an existing patient (patients can update themselves, admins can update anyone)
@router.put("/{patient_id}", response_model=PatientSchema)  # PUT request to update an existing patient by ID
def update_patient(
    patient_id: int,  # The ID of the patient to be updated
    updated: PatientUpdate,  # Updated data (from the client)
    db: Session = Depends(get_db),  # DB session (dependency injection)
    current_user: Patient = Depends(get_current_user_from_cookie)  # Current user (based on cookie)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()  # Query the DB for the patient
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")  # If patient doesn't exist, raise error

    # Use the first admin email from the list (since you have only one admin)
    admin_email = ADMIN_EMAILS[0]

    # Admins can update any patient, but a patient can only update their own profile
    if isinstance(current_user, str) and current_user == "admin":
        # Admin can update any patient
        for key, value in updated.model_dump(exclude_unset=True).items():
            setattr(patient, key, value)  # Update patient attributes

        db.commit()  # Commit changes
        db.refresh(patient)  # Refresh to get the latest DB state
        return patient  # Return updated patient
    elif current_user.email == admin_email or current_user.id == patient_id:
        # Patient can only update their own profile, admin can update any
        for key, value in updated.model_dump(exclude_unset=True).items():
            setattr(patient, key, value)  # Update patient attributes

        db.commit()  # Commit changes
        db.refresh(patient)  # Refresh to get the latest DB state
        return patient  # Return updated patient
    else:
        raise HTTPException(status_code=403, detail="Access denied. You can only update your own profile.")

# Get all patients (accessible by admin only)
@router.get("/", response_model=list[PatientSchema])  # GET request to get all patients
def get_patients(
    db: Session = Depends(get_db),  # DB session (dependency injection)
    current_user: Patient = Depends(get_current_user_from_cookie)  # Current user (based on cookie)
):
    # Use the first admin email from the list (since you have only one admin)
    admin_email = ADMIN_EMAILS[0]

    # Only admin can access all patient data
    if isinstance(current_user, str) and current_user == "admin":
        # Admin can access all patient data
        return db.query(Patient).all()  # Return all patients in the DB
    elif current_user.email == admin_email:
        return db.query(Patient).all()  # Return all patients in the DB
    else:
        raise HTTPException(status_code=403, detail="Only admins can access all patient data.")

# Get a single patient by ID (accessible by admin, doctor, and the patient themselves)
@router.get("/{patient_id}", response_model=PatientSchema)  # GET request to get a specific patient by ID
def get_patient(
    patient_id: int,  # The ID of the patient to be retrieved
    db: Session = Depends(get_db),  # DB session (dependency injection)
    current_user: Patient = Depends(get_current_user_from_cookie)  # Current user (based on cookie)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()  # Query the DB for the patient
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")  # If patient doesn't exist, raise error

    # Use the first admin email from the list (since you have only one admin)
    admin_email = ADMIN_EMAILS[0]

    # Allow admins, doctors, and the patient themselves to access the record
    if isinstance(current_user, str) and current_user == "admin":
        return patient  # Admin can access any patient data
    elif current_user.email == admin_email or current_user.role == "doctor" or current_user.id == patient_id:
        return patient  # Admins, doctors, or the patient themselves can access the data
    else:
        raise HTTPException(status_code=403, detail="Access denied.")  # Access denied if not allowed

# Delete a patient by ID (only accessible by admin)
@router.delete("/{patient_id}")  # DELETE request to delete a patient by ID
def delete_patient(
    patient_id: int,  # The ID of the patient to be deleted
    db: Session = Depends(get_db),  # DB session (dependency injection)
    current_user: Patient = Depends(get_current_user_from_cookie)  # Current user (based on cookie)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()  # Query the DB for the patient
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")  # If patient doesn't exist, raise error

    # Use the first admin email from the list (since you have only one admin)
    admin_email = ADMIN_EMAILS[0]

    # Only admin can delete a patient record
    if isinstance(current_user, str) and current_user == "admin":
        db.delete(patient)  # Delete the patient from DB session
        db.commit()  # Commit changes
        return {"detail": "Patient deleted"}  # Return confirmation message
    elif current_user.email == admin_email:
        db.delete(patient)  # Delete the patient from DB session
        db.commit()  # Commit changes
        return {"detail": "Patient deleted"}  # Return confirmation message
    else:
        raise HTTPException(status_code=403, detail="Access denied. Only admins can delete patient records.")  # Access denied if not allowed
