from fastapi import APIRouter, HTTPException, Depends  # For routing, exceptions, and dependency injection
from sqlalchemy.orm import Session  # For interacting with the database
from typing import Annotated  # For type annotations
from datetime import datetime, timedelta  # For working with dates and times

# --- Import models ---
from ..models.appointment_model import Appointment  # Import the Appointment model for DB interaction
from ..models.doctor_model import Doctor  # Import the Doctor model for DB interaction
from ..models.patient_model import Patient  # Import the Patient model for DB interaction

# --- Import schemas ---
from ..schemas.appointment_schema import (
    AppointmentCreate,  # Schema for creating new appointments
    AppointmentUpdate,  # Schema for updating appointments
    Appointment as AppointmentSchema  # Schema for representing appointments in API responses
)

from ..auth.auth_config import ADMIN_EMAILS  # Import admin emails from .env file

# --- Import DB session dependency ---
from ..db.session import get_db  # Provides SQLAlchemy session for DB access

# --- Import Google integrations ---
from ..google_integration.calendar_utils import create_event  # Function to create a Google Calendar event
from ..google_integration.email_utils import send_email_via_gmail  # Gmail API email sender function

# --- Import Auth utils ---
from ..auth.auth_routes import get_current_user_from_cookie  # Auth protection for routes (fetches current user)

# --- Define the appointment router ---
router = APIRouter(
    prefix="/appointments",  # Base route prefix
    tags=["Appointments"]    # OpenAPI docs tag for appointment-related routes
)

# --- Create an appointment ---
@router.post("/", response_model=AppointmentSchema)  # POST endpoint to create a new appointment
def create_appointment(
    appointment: AppointmentCreate,  # Data model for appointment creation
    db: Session = Depends(get_db),  # Dependency injection for database session
    current_user: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)] = None  # Current user for auth
):
    # Admins can create appointments for anyone, and patients can only create appointments for themselves
    if isinstance(current_user, Patient) and current_user.id == appointment.patient_id:
        pass  # Proceed if the patient is creating their own appointment
    elif isinstance(current_user, str) and current_user == "admin":
        pass  # Admin can create any appointment
    elif current_user.email in ADMIN_EMAILS:
        pass  # Admin email check
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to create appointments for others.")  # Deny access if conditions are not met

    # Proceed with appointment creation
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()  # Query doctor by ID
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")  # Raise error if doctor not found

    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()  # Query patient by ID
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")  # Raise error if patient not found

    # Create the new appointment entry in the database
    new_appointment = Appointment(**appointment.model_dump())  # Create appointment object
    db.add(new_appointment)  # Add to DB session
    db.commit()  # Commit changes to DB
    db.refresh(new_appointment)  # Refresh to get the latest state of the object

    # --- Google Calendar Integration ---
    try:
        # Ensure end_time is properly calculated if not passed
        if not appointment.end_time:
            appointment_end_time = datetime.combine(appointment.date, appointment.start_time) + timedelta(minutes=30)
        else:
            appointment_end_time = datetime.combine(appointment.date, appointment.end_time)

        appointment_start_time = datetime.combine(appointment.date, appointment.start_time)

        # Create a calendar event for the doctor
        event_result = create_event(
            summary=f"Appointment with {patient.name}",
            start_time=appointment_start_time.isoformat(),
            end_time=appointment_end_time.isoformat(),
            email=doctor.email
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating calendar event: {str(e)}")  # Handle errors in calendar creation

    # --- Gmail Integration ---
    try:
        # Send appointment confirmation email to the patient
        send_email_via_gmail(
            to_email=patient.email,
            subject="Appointment Confirmation",
            appointment_details={  # Email details
                'patient_name': patient.name,
                'doctor_name': doctor.name,
                'appointment_date': appointment.date.strftime('%Y-%m-%d'),
                'appointment_time': appointment.start_time.strftime('%I:%M %p')
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")  # Handle errors in email sending

    return new_appointment  # Return the created appointment


# --- Get all appointments ---
@router.get("/", response_model=list[AppointmentSchema])  # GET endpoint to fetch all appointments
def get_appointments(
    db: Session = Depends(get_db),  # Dependency injection for DB session
    current_user: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)] = None  # Current user for authentication
):
    # Admins can view all appointments, doctors and patients can only see theirs
    if isinstance(current_user, str) and current_user == "admin":
        # Admin can access all appointments
        return db.query(Appointment).all()
    elif current_user.email in ADMIN_EMAILS:
        # Check admin email for additional access
        return db.query(Appointment).all()
    elif isinstance(current_user, Doctor):
        # Doctors can only see their own appointments
        return db.query(Appointment).filter(Appointment.doctor_id == current_user.id).all()
    elif isinstance(current_user, Patient):
        # Patients can only see their own appointments
        return db.query(Appointment).filter(Appointment.patient_id == current_user.id).all()


# --- Get appointment by ID ---
@router.get("/{appointment_id}", response_model=AppointmentSchema)  # GET endpoint to fetch appointment by ID
def get_appointment(
    appointment_id: int,  # Appointment ID parameter
    db: Session = Depends(get_db),  # Dependency injection for DB session
    current_user: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)] = None  # Current user for authentication
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()  # Fetch the appointment by ID
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")  # Raise error if appointment not found
    
    # Admins, doctors (for their patients), and patients (for themselves) can view appointments
    if isinstance(current_user, str) and current_user == "admin":
        return appt
    elif current_user.email in ADMIN_EMAILS or current_user.id == appt.doctor_id or current_user.id == appt.patient_id:
        return appt
    else:
        raise HTTPException(status_code=403, detail="Access denied. You can only view your own appointments.")  # Deny access if not allowed


@router.put("/{appointment_id}", response_model=AppointmentSchema)  # PUT endpoint to update an existing appointment
def update_appointment(
    appointment_id: int,  # Appointment ID to be updated
    updated: AppointmentUpdate,  # Data model for appointment updates
    db: Session = Depends(get_db),  # DB session dependency
    current_user: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)] = None  # Current user for authentication
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()  # Fetch the appointment by ID
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")  # Raise error if appointment not found

    # Only allow the patient who created the appointment or the doctor for their appointment to update
    if isinstance(current_user, str) and current_user == "admin":
        pass  # Admin can update any appointment
    elif current_user.email in ADMIN_EMAILS or current_user.id == appt.doctor_id or current_user.id == appt.patient_id:
        pass  # Patients and doctors can update their own appointments
    else:
        raise HTTPException(status_code=403, detail="Access denied. You can only update your own appointment.")  # Deny access if not allowed

    # Update the fields as per the changes in the request
    for key, value in updated.model_dump(exclude_unset=True).items():
        setattr(appt, key, value)

    # Commit the changes to the DB
    db.commit()
    db.refresh(appt)

    # Fetch the patient object (to access name and email)
    patient = db.query(Patient).filter(Patient.id == appt.patient_id).first()

    # --- Google Calendar Integration --- (Update the calendar event)
    try:
        # Ensure end_time is properly calculated if not passed
        if not updated.end_time:
            updated_end_time = datetime.combine(updated.date, updated.start_time) + timedelta(minutes=30)
        else:
            updated_end_time = datetime.combine(updated.date, updated.end_time)

        updated_start_time = datetime.combine(updated.date, updated.start_time)

        # Update the calendar event for the doctor if the time has changed
        event_result = create_event(
            summary=f"Updated Appointment with {patient.name}",
            start_time=updated_start_time.isoformat(),
            end_time=updated_end_time.isoformat(),
            email=appt.doctor.email
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating calendar event: {str(e)}")  # Handle errors in calendar creation

    # --- Gmail Integration --- (Send updated email confirmation)
    try:
        # Compose the updated email body
        email_body = f"""
        Dear {patient.name},

        Your appointment with Dr. {appt.doctor.name} has been updated.

        Updated Appointment Details:
        - Date: {updated.date.strftime('%Y-%m-%d')}
        - Time: {updated.start_time.strftime('%I:%M %p')} to {updated_end_time.strftime('%I:%M %p')}
        
        If you need further assistance, please contact us.

        Best Regards,
        Your Health Team
        """
        send_email_via_gmail(
            to_email=patient.email,
            subject="Appointment Update Confirmation",
            body=email_body  # Send updated email confirmation to patient
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending update email: {str(e)}")

    return appt  # Return updated appointment


# --- Delete appointment by ID ---
@router.delete("/{appointment_id}")  # DELETE endpoint to delete an appointment by ID
def delete_appointment(
    appointment_id: int,  # Appointment ID to be deleted
    db: Session = Depends(get_db),  # DB session dependency
    current_user: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)] = None  # Current user for authentication
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()  # Fetch the appointment by ID
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")  # Raise error if appointment not found

    # Only allow admins or the doctor who created the appointment to delete it
    if isinstance(current_user, str) and current_user == "admin":
        # Admin can delete any appointment
        db.delete(appt)
        db.commit()
        return {"detail": "Appointment deleted"}
    elif current_user.email in ADMIN_EMAILS or current_user.id == appt.doctor_id:
        # Admin or the doctor can delete the appointment
        db.delete(appt)
        db.commit()
        return {"detail": "Appointment deleted"}
    else:
        raise HTTPException(status_code=403, detail="Access denied. You can only delete your own appointments.")  # Deny access if not allowed
