# ---------------------------- External Imports ----------------------------
# Import the SQLAlchemy ORM Session for database interaction
from sqlalchemy.orm import Session  # SQLAlchemy ORM Session for database access

# ---------------------------- Internal Imports ----------------------------
# Import the shared MCP instance used for defining tools
from ..mcp_main import mcp  # Shared MCP instance

# Import Pydantic schemas for doctor creation and update validation
from ..schemas.doctor_schema import DoctorCreate, DoctorUpdate  # Pydantic schemas for validation

# Import service to get a doctor by ID
from ..services.doctor.get_doctor_by_id_service import GetDoctorByIdService

# Import service to create a new doctor
from ..services.doctor.create_doctor_service import CreateDoctorService

# Import service to update an existing doctor
from ..services.doctor.update_doctor_service import UpdateDoctorService

# Import service to delete a doctor
from ..services.doctor.delete_doctor_service import DeleteDoctorService

# Import service to get all doctors
from ..services.doctor.get_all_doctors_service import GetAllDoctorsService

# ---------------------------- Tool: Get Doctor by ID ----------------------------
# Define MCP tool to retrieve a doctor by their ID
@mcp.tool(
    name="get_doctor_by_id",  # Tool name
    description="Retrieve a doctor by their ID.",  # Tool description
    exclude_args=["db"]  # Exclude DB session from external tool args
)
# Async function to get doctor using service
async def get_doctor_tool(
    doctor_id: int,  # Doctor's unique ID
    token: str,      # Authorization token
    db: Session | None = None  # Optional database session
):
    # Call service to fetch doctor by ID
    return await GetDoctorByIdService.get_doctor_by_id(doctor_id, token, db)

# ---------------------------- Tool: Create Doctor (Admin Only) ----------------------------
# Define MCP tool to create a new doctor (restricted to admins)
@mcp.tool(
    name="create_doctor",  # Tool name
    description="Create a new doctor. Only admins can perform this.",  # Description
    exclude_args=["db"]  # Exclude DB session from external tool args
)
# Async function to create a doctor
async def create_doctor_tool(
    doctor: DoctorCreate,  # Doctor creation data (validated via schema)
    token: str,            # Authorization token
    db: Session | None = None  # Optional database session
):
    # Call service to create a new doctor
    return await CreateDoctorService.create_doctor(doctor, token, db)

# ---------------------------- Tool: Update Doctor (Admin Only) ----------------------------
# Define MCP tool to update an existing doctor (admin only)
@mcp.tool(
    name="update_doctor",  # Tool name
    description="Update a doctor. Only admins can perform this.",  # Description
    exclude_args=["db"]  # Exclude DB session from external tool args
)
# Async function to update doctor info
async def update_doctor_tool(
    doctor_id: int,  # Doctor ID to update
    updated_doctor: DoctorUpdate,  # Updated doctor data (validated via schema)
    token: str,  # Authorization token
    db: Session | None = None  # Optional database session
):
    # Call service to update doctor details
    return await UpdateDoctorService.update_doctor(doctor_id, updated_doctor, token, db)

# ---------------------------- Tool: Delete Doctor (Admin Only) ----------------------------
# Define MCP tool to delete a doctor by ID (admin only)
@mcp.tool(
    name="delete_doctor",  # Tool name
    description="Delete a doctor by ID. Only admins can perform this.",  # Description
    exclude_args=["db"]  # Exclude DB session from external tool args
)
# Async function to delete doctor
async def delete_doctor_tool(
    doctor_id: int,  # Doctor ID to delete
    token: str,      # Authorization token
    db: Session | None = None  # Optional database session
):
    # Call service to remove doctor
    return await DeleteDoctorService.delete_doctor(doctor_id, token, db)

# ---------------------------- Tool: Get All Doctors ----------------------------
# Define MCP tool to fetch all doctors (filtered by role)
@mcp.tool(
    name="get_all_doctors",  # Tool name
    description="Retrieve all doctors (filtered by role).",  # Description
    exclude_args=["db"]  # Exclude DB session from external tool args
)
# Async function to get all doctors
async def get_all_doctors_tool(
    token: str,  # Authorization token
    db: Session | None = None  # Optional database session
):
    # Call service to fetch all doctors
    return await GetAllDoctorsService.get_all_doctors(token, db)
