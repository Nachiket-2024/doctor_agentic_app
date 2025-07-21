from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

# Import necessary models and schemas
from ..models.appointment_model import Appointment  # Import SQLAlchemy model
from ..models.user_model import User  # Import User model for doctor/patient
from ..schemas.appointment_schema import AppointmentCreate, AppointmentUpdate, AppointmentResponse  # Import Pydantic schemas
from ..db.session import get_db
from ..auth.auth_utils import verify_jwt_token
from ..auth.auth_user_check import admin_only  # Admin check for restricted routes
from ..google_integration.gmail_utils import send_email_via_gmail  # Gmail integration utility
from ..google_integration.calendar_utils import create_event, update_event, delete_event  # Google Calendar utils

# Initialize OAuth2PasswordBearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create the router for appointment-related routes
router = APIRouter(
    prefix="/appointments",  # All routes will be under /appointments
    tags=["Appointments"],  # Tag to categorize in Swagger docs
)

# ---------------------------- Route: Get Appointment by ID ----------------------------

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get appointment details by appointment_id.
    - Accessible by doctor for their appointments
    - Accessible by patient for their appointments
    - Accessible by admin for all appointments
    """
    try:
        # Verify JWT token and get the logged-in user's info
        payload = verify_jwt_token(token)
        user_role = payload.get("role")
        user_id = payload.get("user_id")

        # Fetch the appointment record by ID
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Admin can view all appointments
        if user_role == "admin":
            return appointment
        
        # Doctor can only view their own appointments
        if user_role == "doctor" and appointment.doctor_id == user_id:
            return appointment
        
        # Patient can only view their own appointments
        if user_role == "patient" and appointment.patient_id == user_id:
            return appointment
        
        # If user does not meet the criteria, return forbidden
        raise HTTPException(status_code=403, detail="You are not authorized to view this appointment")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Create Appointment ----------------------------

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Create a new appointment.
    - Admin or patient can create an appointment.
    - Doctor must already be registered in the system to create appointments.
    """
    try:
        # Verify JWT token and get the logged-in user's info
        payload = verify_jwt_token(token)
        user_role = payload.get("role")

        # Ensure that the user is either an admin or a patient
        if user_role == "admin":
            pass
        elif user_role == "patient":
            doctor = db.query(User).filter(User.id == appointment.doctor_id, User.role == "doctor").first()
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")
        else:
            raise HTTPException(status_code=403, detail="Only admin or patient can create an appointment")

        # Create the appointment
        new_appointment = Appointment(
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            date=appointment.date,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            status=appointment.status,
            reason=appointment.reason,
        )

        # Add and commit to the database
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)

        # Fetch the doctor and patient details
        doctor = db.query(User).filter(User.id == new_appointment.doctor_id).first()
        patient = db.query(User).filter(User.id == new_appointment.patient_id).first()

        # Send email confirmation via Gmail API
        send_email_via_gmail(patient.email, "Appointment Confirmation", new_appointment.id, db)

        # Add event to Google Calendar
        create_event(
            f"Appointment with Dr. {doctor.name}",
            f"{new_appointment.date}T{new_appointment.start_time}:00",
            f"{new_appointment.date}T{new_appointment.end_time}:00",
            patient.email
        )

        return new_appointment

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Update Appointment ----------------------------

@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Update appointment details (admin only).
    - Only admin can update an appointment.
    """
    try:
        # Verify JWT token and get the logged-in user's info
        admin_only(token, db)

        # Fetch the existing appointment
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Update appointment fields with provided data
        appointment.doctor_id = appointment_update.doctor_id if appointment_update.doctor_id else appointment.doctor_id
        appointment.patient_id = appointment_update.patient_id if appointment_update.patient_id else appointment.patient_id
        appointment.date = appointment_update.date if appointment_update.date else appointment.date
        appointment.start_time = appointment_update.start_time if appointment_update.start_time else appointment.start_time
        appointment.end_time = appointment_update.end_time if appointment_update.end_time else appointment.end_time
        appointment.status = appointment_update.status if appointment_update.status else appointment.status
        appointment.reason = appointment_update.reason if appointment_update.reason else appointment.reason

        # Commit changes to DB
        db.commit()
        db.refresh(appointment)

        # Fetch the doctor and patient details
        doctor = db.query(User).filter(User.id == appointment.doctor_id).first()
        patient = db.query(User).filter(User.id == appointment.patient_id).first()

        # Update the calendar event
        update_event(
            appointment_id,
            f"Updated Appointment with Dr. {doctor.name}",
            f"{appointment.date}T{appointment.start_time}:00",
            f"{appointment.date}T{appointment.end_time}:00",
            patient.email
        )

        # Send email with updated appointment details
        send_email_via_gmail(patient.email, "Updated Appointment", appointment.id, db)

        return appointment

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Delete Appointment ----------------------------

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Delete appointment (admin only).
    - Only admin can delete an appointment.
    """
    try:
        # Verify JWT token and check if the user is an admin
        admin_only(token, db)

        # Fetch the existing appointment
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Delete the appointment from the database
        db.delete(appointment)
        db.commit()

        # Fetch the doctor and patient details
        doctor = db.query(User).filter(User.id == appointment.doctor_id).first()
        patient = db.query(User).filter(User.id == appointment.patient_id).first()

        # Delete the calendar event
        delete_event(appointment_id)

        # Send cancellation email to patient
        send_email_via_gmail(patient.email, "Appointment Cancellation", appointment.id, db)

        return {"message": "Appointment deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
