# ---------------------------- External Imports ----------------------------

# Import the tool decorator from FastAPI MCP
from fastapi_mcp import tool

# SQLAlchemy ORM Session for database access
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import Pydantic schemas for Doctor for input validation and output
from ..schemas.doctor_schema import DoctorCreate, DoctorUpdate

# Import service function to retrieve a doctor by ID
from ..services.doctor.get_doctor_by_id_service import GetDoctorByIdService

# Import service function to create a new doctor
from ..services.doctor.create_doctor_service import CreateDoctorService

# Import service function to update an existing doctor's details
from ..services.doctor.update_doctor_service import UpdateDoctorService

# Import service function to delete a doctor
from ..services.doctor.delete_doctor_service import DeleteDoctorService

# Import service function to retrieve all doctors
from ..services.doctor.get_all_doctors_service import GetAllDoctorsService

# ---------------------------- Tool: Get Doctor by ID ----------------------------

# MCP tool to retrieve a specific doctor by ID
@tool(name="get_doctor_by_id", description="Retrieve a doctor by their ID.")
async def get_doctor_tool(
    doctor_id: int,                  # Doctor's unique ID to retrieve
    token: str,                      # Authorization token
    db: Session                      # Injected database session
):
    # Delegate call to the service function
    return await GetDoctorByIdService.get_doctor_by_id(doctor_id, token, db)


# ---------------------------- Tool: Create Doctor (Admin Only) ----------------------------

# MCP tool to create a new doctor (Admin access required)
@tool(name="create_doctor", description="Create a new doctor. Only admins can perform this.")
async def create_doctor_tool(
    doctor: DoctorCreate,            # Doctor data for creation
    token: str,                      # Authorization token
    db: Session                      # Injected database session
):
    # Delegate call to the service function
    return await CreateDoctorService.create_doctor(doctor, token, db)


# ---------------------------- Tool: Update Doctor (Admin Only) ----------------------------

# MCP tool to update an existing doctor's information
@tool(name="update_doctor", description="Update a doctor. Only admins can perform this.")
async def update_doctor_tool(
    doctor_id: int,                  # ID of the doctor to update
    updated_doctor: DoctorUpdate,   # New data to update the doctor with
    token: str,                      # Authorization token
    db: Session                      # Injected database session
):
    # Delegate call to the service function
    return await UpdateDoctorService.update_doctor(doctor_id, updated_doctor, token, db)


# ---------------------------- Tool: Delete Doctor (Admin Only) ----------------------------

# MCP tool to delete a doctor
@tool(name="delete_doctor", description="Delete a doctor by ID. Only admins can perform this.")
async def delete_doctor_tool(
    doctor_id: int,                  # ID of the doctor to delete
    token: str,                      # Authorization token
    db: Session                      # Injected database session
):
    # Delegate call to the service function
    return await DeleteDoctorService.delete_doctor(doctor_id, token, db)


# ---------------------------- Tool: Get All Doctors ----------------------------

# MCP tool to retrieve all doctors (admins/patients see all; doctors see self)
@tool(name="get_all_doctors", description="Retrieve all doctors (filtered by role).")
async def get_all_doctors_tool(
    token: str,                      # Authorization token
    db: Session                      # Injected database session
):
    # Delegate call to the service function
    return await GetAllDoctorsService.get_all_doctors(token, db)
