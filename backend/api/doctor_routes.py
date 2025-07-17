from fastapi import APIRouter, HTTPException, Depends, Query  # Routing and exception handling
from sqlalchemy.orm import Session  # DB session management
from datetime import datetime  # Date and time utilities
from typing import Annotated  # Type annotations

# --- Import models and schemas ---
from ..models.doctor_model import Doctor  # Doctor DB model
from ..models.appointment_model import Appointment  # Appointment DB model
from ..schemas.doctor_schema import (
    DoctorCreate,
    DoctorUpdate,
    Doctor as DoctorSchema
)

from ..auth.auth_config import ADMIN_EMAILS # Import admin emails from .env file

# --- Import database session provider ---
from ..db.session import get_db  # SQLAlchemy session for DB access

# --- Import slot generation utility ---
from ..utils.availability_utils import generate_available_slots

# --- Import Auth utils ---
from ..auth.auth_routes import get_current_user_from_cookie  # Auth protection for routes

# --- Set up the router ---
router = APIRouter(prefix="/doctors", tags=["Doctors"])

# --- Create a new doctor (accessible only by admin) ---
@router.post("/", response_model=DoctorSchema)
def create_doctor(
    doctor: DoctorCreate, 
    db: Session = Depends(get_db), 
    current_user: Annotated[Doctor, Depends(get_current_user_from_cookie)] = None
):
    
    # --- DEBUG: Print current user and admin list ---
    print(f"current_user: {current_user}")
    print(f"current_user.email: {getattr(current_user, 'email', None)}")

    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Access denied. Only admins can create doctors.")
    
    db_doctor = Doctor(**doctor.model_dump())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

# --- Get all doctors (accessible by anyone) ---
@router.get("/", response_model=list[DoctorSchema])
def get_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).all()

# --- Get a doctor by ID (accessible by anyone) ---
@router.get("/{doctor_id}", response_model=DoctorSchema)
def get_doctor(
    doctor_id: int, 
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

# --- Update an existing doctor (accessible only by admin) ---
@router.put("/{doctor_id}", response_model=DoctorSchema)
def update_doctor(
    doctor_id: int, 
    updated: DoctorUpdate, 
    db: Session = Depends(get_db), 
    current_user: Annotated[Doctor, Depends(get_current_user_from_cookie)] = None
):
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Access denied. Only admins can update doctor details.")
    
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    for key, value in updated.model_dump(exclude_unset=True).items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)
    return doctor

# --- Delete a doctor (accessible only by admin) ---
@router.delete("/{doctor_id}")
def delete_doctor(
    doctor_id: int, 
    db: Session = Depends(get_db), 
    current_user: Annotated[Doctor, Depends(get_current_user_from_cookie)] = None
):
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Access denied. Only admins can delete doctors.")

    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    db.delete(doctor)
    db.commit()
    return {"detail": "Doctor deleted"}

# --- Get doctor's availability on a specific date (accessible by anyone) ---
@router.get("/{doctor_id}/availability")
def get_doctor_availability(
    doctor_id: int,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    weekday_key = target_date.strftime("%a").lower()[:3]  # e.g., 'mon', 'tue'
    print(f"target_date: {target_date}, weekday_key: {weekday_key}")

    available_slots = []

    # Check if doctor is available that day
    if weekday_key not in doctor.available_days:
        return {"available_slots": []}

    # Get all appointments already booked on this date
    booked_times = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == target_date
    ).all()

    booked_set = set()

    for appt in booked_times:
        print(f"Type of appt.start_time: {type(appt.start_time)}")  # Check type
        if isinstance(appt.start_time, datetime):  # Check if it's a datetime object
            formatted_time = appt.start_time.strftime("%H:%M")
            booked_set.add(formatted_time)
        else:
            # Convert if needed
            appt.start_time = datetime.strptime(appt.start_time, "%Y-%m-%d %H:%M:%S")
            formatted_time = appt.start_time.strftime("%H:%M")
            booked_set.add(formatted_time)

    print(f"Booked slots: {booked_set}")

    # Generate all possible slots based on doctor's schedule
    for time_range in doctor.available_days[weekday_key]:
        if isinstance(time_range, list) and len(time_range) == 2:
            start_str, end_str = time_range
            slots = generate_available_slots(start_str, end_str, doctor.slot_duration)
            # Filter out booked ones
            free_slots = [slot for slot in slots if slot not in booked_set]
            available_slots.extend(free_slots)

    return {"available_slots": available_slots}
