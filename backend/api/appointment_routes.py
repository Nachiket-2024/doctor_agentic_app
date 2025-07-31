# ---------------------------- External Imports ----------------------------

# FastAPI dependencies for routing, authentication, error handling, and status codes
from fastapi import APIRouter, Depends, status

# OAuth2 token extractor from request headers
from fastapi.security import OAuth2PasswordBearer

# SQLAlchemy ORM Session for DB interactions
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Pydantic schemas for input and output validation of appointments
from ..schemas.appointment_schema import AppointmentCreate, AppointmentUpdate, AppointmentResponse

# Dependency to get DB session from context
from ..db.session import get_db

# Service function to get appointment by id
from ..services.appointment.get_appointment_by_id import get_appointment_by_id

# Service function to create a new appointment
from ..services.appointment.create_appointment import create_appointment_entry

# Service function to update an appointment
from ..services.appointment.update_appointment import update_appointment_entry

# Service function to delete an appointment
from ..services.appointment.delete_appointment import delete_appointment_entry

# Service function to get all appointments
from ..services.appointment.get_all_appointments import get_all_appointments_entry

# ---------------------------- OAuth2 Setup ----------------------------

# Token URL to be used by OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------------------------- Router Initialization ----------------------------

# Initialize router instance with tag and path prefix
router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)

# ---------------------------- Route: Get Appointment by ID ----------------------------

# Get a specific appointment based on its ID
@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    return await get_appointment_by_id(appointment_id, token, db)


# ---------------------------- Route: Create Appointment ----------------------------

# Endpoint to create a new appointment
@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    return await create_appointment_entry(appointment, token, db)


# ---------------------------- Route: Update Appointment ----------------------------

# Update an existing appointment and modify Google Calendar if needed
@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    return await update_appointment_entry(appointment_id, appointment_update, token, db)


# ---------------------------- Route: Delete Appointment ----------------------------

# Delete an appointment and remove its calendar entry if present
@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    return await delete_appointment_entry(appointment_id, token, db)


# ---------------------------- Route: Get All Appointments ----------------------------

# Retrieve appointments depending on user role (admin/doctor/patient)
@router.get("/", response_model=list[AppointmentResponse])
async def get_all_appointments(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    return await get_all_appointments_entry(token, db)
