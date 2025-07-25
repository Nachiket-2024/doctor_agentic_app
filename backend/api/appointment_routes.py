# ---------------------------- Imports ----------------------------
from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI utilities
from sqlalchemy.orm import Session  # For database session
from fastapi.security import OAuth2PasswordBearer  # For token auth
from datetime import datetime  # For date and time handling
import calendar  # To convert weekday index to name

# ---------------------------- Internal Modules ----------------------------
from ..models.appointment_model import Appointment  # Appointment SQLAlchemy model
from ..models.user_model import User  # User model for doctors/patients
from ..schemas.appointment_schema import AppointmentCreate, AppointmentUpdate, AppointmentResponse  # Pydantic schemas
from ..db.session import get_db  # Dependency to get DB session
from ..auth.auth_utils import verify_jwt_token  # JWT token verifier
from ..auth.auth_user_check import admin_only  # Auth guard for admin-only access
from ..google_integration.gmail_utils import send_email_via_gmail  # Gmail utility
from ..google_integration.calendar_utils import create_event, update_event, delete_event  # Calendar sync utilities
from ..utils.slot_utils import generate_available_slots  # Slot generator logic

# ---------------------------- OAuth2 Setup ----------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Token URL for dependency injection

# ---------------------------- Router Setup ----------------------------
router = APIRouter(
    prefix="/appointments",  # Base path
    tags=["Appointments"],  # Swagger tag
)

# ---------------------------- Get Appointment By ID ----------------------------
@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = verify_jwt_token(token)
        user_role = payload.get("role")
        user_id = payload.get("user_id")

        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if user_role == "admin":
            return appointment
        if user_role == "doctor" and appointment.doctor_id == user_id:
            return appointment
        if user_role == "patient" and appointment.patient_id == user_id:
            return appointment

        raise HTTPException(status_code=403, detail="You are not authorized to view this appointment")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Create Appointment ----------------------------
@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = verify_jwt_token(token)
        user_role = payload.get("role")
        refresh_token = payload.get("refresh_token")

        if user_role not in ["admin", "patient"]:
            raise HTTPException(status_code=403, detail="Only admin or patient can create an appointment")

        doctor = db.query(User).filter(User.id == appointment.doctor_id, User.role == "doctor").first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        weekday_key = calendar.day_name[appointment.date.weekday()].lower()[:3]
        available_days = doctor.available_days or {}
        if weekday_key not in available_days:
            raise HTTPException(status_code=400, detail="Doctor not available on selected day")

        time_range = available_days[weekday_key]
        booked = db.query(Appointment).filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.date == appointment.date
        ).all()
        booked_times = [appt.start_time for appt in booked]
        available_slots = generate_available_slots(time_range, doctor.slot_duration or 30, booked_times)

        if appointment.start_time not in available_slots:
            raise HTTPException(status_code=400, detail="Selected time slot is already booked or unavailable")

        new_appointment = Appointment(
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            date=appointment.date,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            status=appointment.status,
            reason=appointment.reason,
        )

        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)

        patient = db.query(User).filter(User.id == new_appointment.patient_id).first()

        send_email_via_gmail(token, refresh_token, patient.email, "Appointment Confirmation", new_appointment.id, db)
        create_event(
            f"Appointment with Dr. {doctor.name}",
            f"{new_appointment.date}T{new_appointment.start_time}:00",
            f"{new_appointment.date}T{new_appointment.end_time}:00",
            patient.email
        )

        return new_appointment

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Update Appointment ----------------------------
@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = verify_jwt_token(token)
        admin_only(token, db)
        refresh_token = payload.get("refresh_token")

        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        doctor_id = appointment_update.doctor_id or appointment.doctor_id
        date = appointment_update.date or appointment.date
        start_time = appointment_update.start_time or appointment.start_time

        doctor = db.query(User).filter(User.id == doctor_id).first()
        weekday_key = calendar.day_name[date.weekday()].lower()[:3]
        available_days = doctor.available_days or {}

        if weekday_key not in available_days:
            raise HTTPException(status_code=400, detail="Doctor not available on selected day")

        time_range = available_days[weekday_key]
        booked = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == date,
            Appointment.id != appointment_id
        ).all()
        booked_times = [appt.start_time for appt in booked]
        available_slots = generate_available_slots(time_range, doctor.slot_duration or 30, booked_times)

        if start_time not in available_slots:
            raise HTTPException(status_code=400, detail="Selected time slot is already booked or unavailable")

        appointment.doctor_id = doctor_id
        appointment.patient_id = appointment_update.patient_id or appointment.patient_id
        appointment.date = date
        appointment.start_time = start_time
        appointment.end_time = appointment_update.end_time or appointment.end_time
        appointment.status = appointment_update.status or appointment.status
        appointment.reason = appointment_update.reason or appointment.reason

        db.commit()
        db.refresh(appointment)

        patient = db.query(User).filter(User.id == appointment.patient_id).first()

        update_event(
            appointment_id,
            f"Updated Appointment with Dr. {doctor.name}",
            f"{appointment.date}T{appointment.start_time}:00",
            f"{appointment.date}T{appointment.end_time}:00",
            patient.email
        )
        send_email_via_gmail(token, refresh_token, patient.email, "Updated Appointment", appointment.id, db)

        return appointment

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Get All Appointments ----------------------------
@router.get("/", response_model=list[AppointmentResponse])
async def get_all_appointments(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Retrieve all appointments. 
    - Admins see everything.
    - Doctors see only their appointments.
    - Patients see only their appointments.
    """
    try:
        payload = verify_jwt_token(token)
        user_role = payload.get("role")
        user_id = payload.get("user_id")

        if user_role == "admin":
            return db.query(Appointment).all()
        elif user_role == "doctor":
            return db.query(Appointment).filter(Appointment.doctor_id == user_id).all()
        elif user_role == "patient":
            return db.query(Appointment).filter(Appointment.patient_id == user_id).all()
        else:
            raise HTTPException(status_code=403, detail="Not authorized to view appointments.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Delete Appointment ----------------------------
@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = verify_jwt_token(token)
        admin_only(token, db)
        refresh_token = payload.get("refresh_token")

        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        db.delete(appointment)
        db.commit()

        patient = db.query(User).filter(User.id == appointment.patient_id).first()
        delete_event(appointment_id)
        send_email_via_gmail(token, refresh_token, patient.email, "Appointment Cancellation", appointment.id, db)

        return  # Will automatically return 204 No Content

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
