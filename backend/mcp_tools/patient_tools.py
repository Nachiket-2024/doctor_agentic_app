# ---------------------------- External Imports ----------------------------

# Import the tool decorator from FastAPI MCP
from fastapi_mcp import tool

# SQLAlchemy ORM session class for database interactions
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import schema definitions for patient data handling
from ..schemas.patient_schema import (
    PatientCreate,           # Schema for creating a patient
    PatientUpdate,           # Schema for updating patient info
)

# Import service function to retrieve a patient by ID
from ..services.patient.get_patient_by_id_service import GetPatientByIDService

# Import service function to create a new patient
from ..services.patient.create_patient_service import CreatePatientService

# Import service function to update patient details
from ..services.patient.update_patient_service import UpdatePatientService

# Import service function to delete a patient
from ..services.patient.delete_patient_service import DeletePatientService

# Import service function to retrieve all patients
from ..services.patient.get_all_patients_service import GetAllPatientsService

# ---------------------------- Tool: Get Patient by ID ----------------------------

# MCP tool to fetch a patient by their ID (only admin or self)
@tool(name="get_patient_by_id", description="Get patient profile by their ID. Admin or patient only.")
async def get_patient_tool(
    patient_id: int,     # Unique ID of the patient to retrieve
    token: str,          # JWT token for authorization
    db: Session          # SQLAlchemy session
):
    # Delegate to service function to fetch patient data
    return await GetPatientByIDService.get_patient_by_id(patient_id, token, db)


# ---------------------------- Tool: Create Patient ----------------------------

# MCP tool to create a new patient record
@tool(name="create_patient", description="Create a new patient record.")
async def create_patient_tool(
    patient: PatientCreate,  # Patient creation data
    token: str,              # Authorization token
    db: Session              # SQLAlchemy session
):
    # Delegate to service function for patient creation
    return await CreatePatientService.create_patient(patient, token, db)


# ---------------------------- Tool: Update Patient ----------------------------

# MCP tool to update an existing patient's data
@tool(name="update_patient", description="Update an existing patient's information.")
async def update_patient_tool(
    patient_id: int,             # ID of the patient to update
    update_data: PatientUpdate,  # Updated patient fields
    token: str,                  # JWT token for access control
    db: Session                  # SQLAlchemy session
):
    # Delegate to service function to update patient details
    return await UpdatePatientService.update_patient(patient_id, update_data, token, db)


# ---------------------------- Tool: Delete Patient ----------------------------

# MCP tool to delete a patient record (admin-only)
@tool(name="delete_patient", description="Delete a patient by ID. Admin only.")
async def delete_patient_tool(
    patient_id: int,   # ID of the patient to delete
    token: str,        # Authorization token
    db: Session        # SQLAlchemy session
):
    # Delegate to service function to handle deletion
    return await DeletePatientService.delete_patient(patient_id, token, db)


# ---------------------------- Tool: Get All Patients ----------------------------

# MCP tool to retrieve patients (admin sees all, patients see only self)
@tool(name="get_all_patients", description="Retrieve all patient records. Admin or patient.")
async def get_all_patients_tool(
    token: str,    # JWT token to determine access level
    db: Session    # SQLAlchemy session
):
    # Delegate to service function to retrieve list of patients
    return await GetAllPatientsService.get_all_patients(token, db)
