# ---------------------------- External Imports ----------------------------
# FastAPI tools for routing, dependency injection, and HTTP exceptions
from fastapi import APIRouter, Depends, Query

# SQLAlchemy Session to interact with the database
from sqlalchemy.orm import Session

# OAuth2PasswordBearer to extract JWT token from requests
from fastapi.security import OAuth2PasswordBearer

# ---------------------------- Internal Imports ----------------------------
# Dependency to get a database session
from ..db.database_session_manager import DatabaseSessionManager

# Import the modular service to get available slots
from ..services.doctor_slot.doctor_slot_availability_service import DoctorSlotAvailabilityService

# ---------------------------- OAuth2 Setup ----------------------------
# Setup OAuth2 scheme to extract token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------------------------- APIRouter Setup ----------------------------
# Initialize FastAPI router with prefix and documentation tags
router = APIRouter(
    prefix="/doctor_slot",      # Base URL prefix for all routes in this router
    tags=["Doctor Slots"],      # Group routes under this tag in API docs
)

# ---------------------------- Route: Get Available Slots ----------------------------
# Define an HTTP GET route to fetch available slots for a doctor on a given date
@router.get("/{doctor_id}/available-slots", 
            operation_id="get_available_slots_by_doctor_id", 
            summary="Get Available Slots by Doctor ID"
            )

async def get_available_slots(
    doctor_id: int,                                     # Doctor's unique ID passed as a path parameter
    date_str: str = Query(..., description="Date in YYYY-MM-DD"),  # Target date for slot query (required query param)
    token: str = Depends(oauth2_scheme),                # Extract the bearer token from request headers
    db: Session = Depends(DatabaseSessionManager().get_db)                       # Inject a database session into the route
):
    """
    Returns a list of available slot start times (as strings) for a doctor
    on a given date, using precomputed weekly slots and filtering out booked ones.
    """
    return await DoctorSlotAvailabilityService(db).get_available_slots_by_doctor_id(doctor_id, date_str)