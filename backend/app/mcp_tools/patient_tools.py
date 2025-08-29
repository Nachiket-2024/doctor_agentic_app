# ---------------------------- External Imports ----------------------------
# Import SQLAlchemy ORM Session for database operations
from sqlalchemy.orm import Session  # SQLAlchemy ORM session class for database interactions

# ---------------------------- Internal Imports ----------------------------
# Import shared MCP instance to define tools
from ..mcp_main import mcp  

# Import Pydantic schemas for patient creation and update validation
from ..schemas.patient_schema import PatientCreate, PatientUpdate  # Patient Pydantic schemas

# Import service to get a patient by ID
from ..services.patient.get_patient_by_id_service import GetPatientByIDService

# Import service to create a new patient
from ..services.patient.create_patient_service import CreatePatientService

# Import service to update an existing patient
from ..services.patient.update_patient_service import UpdatePatientService

# Import service to delete a patient
from ..services.patient.delete_patient_service import DeletePatientService

# Import service to retrieve all patients
from ..services.patient.get_all_patients_service import GetAllPatientsService

# ---------------------------- Tool: Get Patient by ID ----------------------------
# Define MCP tool to retrieve patient profile by ID (accessible to admin or patient)
@mcp.tool(
    name="get_patient_by_id",  # Tool name
    description="Get patient profile by their ID. Admin or patient only.",  # Tool description
    exclude_args=["db"]  # Exclude DB session from external arguments
)
# Async function to get patient by ID
async def get_patient_tool(
    patient_id: int,  # Patient's unique ID
    token: str,       # Authorization token
    db: Session | None = None  # Optional database session
):
    # Call service to fetch patient by ID
    return await GetPatientByIDService.get_patient_by_id(patient_id, token, db)

# ---------------------------- Tool: Create Patient ----------------------------
# Define MCP tool to create a new patient record
@mcp.tool(
    name="create_patient",  # Tool name
    description="Create a new patient record.",  # Tool description
    exclude_args=["db"]  # Exclude DB session from external arguments
)
# Async function to create patient
async def create_patient_tool(
    patient: PatientCreate,  # Patient creation data
    token: str,              # Authorization token
    db: Session | None = None  # Optional database session
):
    # Call service to create a new patient
    return await CreatePatientService.create_patient(patient, token, db)

# ---------------------------- Tool: Update Patient ----------------------------
# Define MCP tool to update existing patient information
@mcp.tool(
    name="update_patient",  # Tool name
    description="Update an existing patient's information.",  # Tool description
    exclude_args=["db"]  # Exclude DB session from external arguments
)
# Async function to update patient
async def update_patient_tool(
    patient_id: int,       # Patient ID to update
    update_data: PatientUpdate,  # Updated patient data
    token: str,            # Authorization token
    db: Session | None = None  # Optional database session
):
    # Call service to update patient details
    return await UpdatePatientService.update_patient(patient_id, update_data, token, db)

# ---------------------------- Tool: Delete Patient ----------------------------
# Define MCP tool to delete a patient by ID (admin only)
@mcp.tool(
    name="delete_patient",  # Tool name
    description="Delete a patient by ID. Admin only.",  # Tool description
    exclude_args=["db"]  # Exclude DB session from external arguments
)
# Async function to delete patient
async def delete_patient_tool(
    patient_id: int,       # Patient ID to delete
    token: str,            # Authorization token
    db: Session | None = None  # Optional database session
):
    # Call service to delete patient
    return await DeletePatientService.delete_patient(patient_id, token, db)

# ---------------------------- Tool: Get All Patients ----------------------------
# Define MCP tool to retrieve all patients (accessible to admin or patient)
@mcp.tool(
    name="get_all_patients",  # Tool name
    description="Retrieve all patient records. Admin or patient.",  # Tool description
    exclude_args=["db"]  # Exclude DB session from external arguments
)
# Async function to get all patients
async def get_all_patients_tool(
    token: str,            # Authorization token
    db: Session | None = None  # Optional database session
):
    # Call service to fetch all patients
    return await GetAllPatientsService.get_all_patients(token, db)
