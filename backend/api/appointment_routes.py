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
from ..db.database_session_manager import DatabaseSessionManager

# Service function to get appointment by id
from ..services.appointment.get_appointment_by_id_service import GetAppointmentByIDService

# Service function to create a new appointment
from ..services.appointment.create_appointment_service import CreateAppointmentService

# Service function to update an appointment
from ..services.appointment.update_appointment_service import UpdateAppointmentService

# Service function to delete an appointment
from ..services.appointment.delete_appointment_service import DeleteAppointmentService

# Service function to get all appointments
from ..services.appointment.get_all_appointments_service import GetAllAppointmentsService

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
    db: Session = Depends(DatabaseSessionManager().get_db)
):
    return await GetAppointmentByIDService(db).get_appointment_by_id(appointment_id, token)


# ---------------------------- Route: Create Appointment ----------------------------

# Endpoint to create a new appointment
@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(DatabaseSessionManager().get_db)
):
    return await CreateAppointmentService(db).create_appointment(appointment, token)


# ---------------------------- Route: Update Appointment ----------------------------

# Update an existing appointment and modify Google Calendar if needed
@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(DatabaseSessionManager().get_db)
):
    return await UpdateAppointmentService(db).update_appointment(appointment_id, appointment_update, token)


# ---------------------------- Route: Delete Appointment ----------------------------

# Delete an appointment and remove its calendar entry if present
@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(DatabaseSessionManager().get_db)
):
    return await DeleteAppointmentService(db).delete_appointment(appointment_id, token)


# ---------------------------- Route: Get All Appointments ----------------------------

# Retrieve appointments depending on user role (admin/doctor/patient)
@router.get("/", response_model=list[AppointmentResponse])
async def get_all_appointments(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(DatabaseSessionManager().get_db)
):
    return await GetAllAppointmentsService(db).get_all_appointments(token)
