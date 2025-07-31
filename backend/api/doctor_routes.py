# ---------------------------- External Imports ----------------------------

# Import FastAPI core components for routing, dependency injection, and HTTP status codes
from fastapi import APIRouter, Depends, status

# Import Session class for database operations using SQLAlchemy ORM
from sqlalchemy.orm import Session

# Import OAuth2 dependency to extract the access token from request headers
from fastapi.security import OAuth2PasswordBearer

# ---------------------------- Internal Imports ----------------------------

# Import Pydantic schemas for Doctor for input validation and response formatting
from ..schemas.doctor_schema import DoctorCreate, DoctorRead, DoctorUpdate, DoctorDeleteResponse

# Import the function to retrieve a database session via dependency injection
from ..db.session import get_db

# Import service function to retrieve a doctor by ID
from ..services.doctor.get_doctor_by_id import get_doctor_by_id_service

# Import service function to create a new doctor
from ..services.doctor.create_doctor import create_doctor_service

# Import service function to update an existing doctor's details
from ..services.doctor.update_doctor import update_doctor_service

# Import service function to delete a doctor
from ..services.doctor.delete_doctor import delete_doctor_service

# Import service function to retrieve all doctors
from ..services.doctor.get_all_doctors import get_all_doctors_service

# ---------------------------- Initialization ----------------------------

# Initialize the OAuth2 password bearer to extract token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a FastAPI APIRouter instance for the doctor endpoints
router = APIRouter(
    prefix="/doctor",         # Base path for all endpoints in this router
    tags=["Doctor"],          # Tag used in OpenAPI documentation
)

# ---------------------------- Route: Get Doctor by ID ----------------------------

# Define route to retrieve a specific doctor by ID
@router.get("/{doctor_id}", response_model=DoctorRead)
async def get_doctor(
    doctor_id: int,                             # Doctor's unique identifier from the path
    token: str = Depends(oauth2_scheme),        # Extract token using OAuth2
    db: Session = Depends(get_db)               # Inject database session
):
    """
    Retrieve a doctor by their ID.
    """
    # Delegate logic to service layer to get doctor by ID
    return await get_doctor_by_id_service(doctor_id, token, db)


# ---------------------------- Route: Create Doctor (Admin Only) ----------------------------

# Define route to create a new doctor (Admin access required)
@router.post("/", response_model=DoctorRead, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor: DoctorCreate,                       # Doctor creation payload validated via Pydantic
    token: str = Depends(oauth2_scheme),        # Extract token from Authorization header
    db: Session = Depends(get_db)               # Inject SQLAlchemy session
):
    """
    Create a new doctor (Admin only).
    """
    # Delegate logic to service layer to create a new doctor
    return await create_doctor_service(doctor, token, db)


# ---------------------------- Route: Update Doctor (Admin Only) ----------------------------

# Define route to update doctor details (Admin access required)
@router.put("/{doctor_id}", response_model=DoctorRead)
async def update_doctor(
    doctor_id: int,                             # Doctor's unique identifier from the path
    updated_doctor: DoctorUpdate,              # Updated data validated via Pydantic schema
    token: str = Depends(oauth2_scheme),        # Extract token from the request
    db: Session = Depends(get_db)               # Inject database session
):
    """
    Update a doctor (Admin only).
    """
    # Delegate logic to service layer to update doctor information
    return await update_doctor_service(doctor_id, updated_doctor, token, db)


# ---------------------------- Route: Delete Doctor (Admin Only) ----------------------------

# Define route to delete a doctor (Admin access required)
@router.delete("/{doctor_id}", response_model=DoctorDeleteResponse)
async def delete_doctor(
    doctor_id: int,                             # ID of the doctor to delete
    token: str = Depends(oauth2_scheme),        # Extract token for authorization
    db: Session = Depends(get_db)               # Inject database session
):
    """
    Delete a doctor (Admin only).
    """
    # Delegate logic to service layer to delete the doctor
    return await delete_doctor_service(doctor_id, token, db)


# ---------------------------- Route: Get All Doctors ----------------------------

# Define route to retrieve all doctors
@router.get("/", response_model=list[DoctorRead])
async def get_all_doctors(
    token: str = Depends(oauth2_scheme),        # Extract token to identify requester
    db: Session = Depends(get_db)               # Inject database session
):
    """
    Retrieve all doctors.
    - Admins & patients: see all.
    - Doctors: see only self.
    """
    # Delegate logic to service layer to retrieve doctors list
    return await get_all_doctors_service(token, db)
