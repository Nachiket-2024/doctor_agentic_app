# ---------------------------- External Imports ----------------------------

# Import the tool decorator from FastAPI MCP to expose functions to the LLM agent
from fastapi_mcp import tool

# Import the SQLAlchemy Session class for typed DB access
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import the service to create a new appointment
from ..services.appointment.create_appointment_service import CreateAppointmentService

# Import the service to retrieve an appointment by its ID
from ..services.appointment.get_appointment_by_id_service import GetAppointmentByIDService

# Import the service to update an existing appointment
from ..services.appointment.update_appointment_service import UpdateAppointmentService

# Import the service to delete an appointment
from ..services.appointment.delete_appointment_service import DeleteAppointmentService

# Import the service to retrieve all appointments based on role
from ..services.appointment.get_all_appointments_service import GetAllAppointmentsService

# ---------------------------- Tool: Create Appointment ----------------------------

# Define an MCP tool that creates a new appointment using patient & doctor info
@tool(name="create_appointment", description="Create a new appointment with patient and doctor info.")
async def create_appointment_tool(
    appointment: dict,       # Dictionary containing appointment creation data
    token: str,              # Auth token from frontend or LLM agent context
    db: Session,             # SQLAlchemy DB session passed manually by LangChain
):
    # Delegate creation logic to service layer
    return await CreateAppointmentService.create_appointment(appointment, token, db)


# ---------------------------- Tool: Get Appointment by ID ----------------------------

# Define an MCP tool that retrieves a single appointment by its unique ID
@tool(name="get_appointment_by_id", description="Retrieve an appointment by its ID.")
async def get_appointment_by_id_tool(
    appointment_id: int,     # ID of the appointment to retrieve
    token: str,              # Auth token from frontend or agent context
    db: Session,             # SQLAlchemy DB session
):
    # Call service function to fetch appointment by ID
    return await GetAppointmentByIDService.get_appointment_by_id(appointment_id, token, db)


# ---------------------------- Tool: Update Appointment ----------------------------

# Define an MCP tool that updates an existing appointment
@tool(name="update_appointment", description="Update details of an existing appointment.")
async def update_appointment_tool(
    appointment_id: int,         # ID of the appointment to update
    appointment_update: dict,    # Dictionary containing updated fields
    token: str,                  # Auth token for user authorization
    db: Session,                 # SQLAlchemy DB session
):
    # Forward to service layer to handle update
    return await UpdateAppointmentService.update_appointment(appointment_id, appointment_update, token, db)


# ---------------------------- Tool: Delete Appointment ----------------------------

# Define an MCP tool that deletes an appointment based on ID
@tool(name="delete_appointment", description="Delete an appointment by ID.")
async def delete_appointment_tool(
    appointment_id: int,     # ID of the appointment to delete
    token: str,              # Auth token to verify permissions
    db: Session,             # SQLAlchemy DB session
):
    # Use service layer to perform deletion
    return await DeleteAppointmentService.delete_appointment(appointment_id, token, db)


# ---------------------------- Tool: Get All Appointments ----------------------------

# Define an MCP tool that retrieves all appointments accessible to the user
@tool(name="get_all_appointments", description="Fetch all appointments accessible to the user.")
async def get_all_appointments_tool(
    token: str,              # User's access token for authorization and filtering
    db: Session,             # SQLAlchemy DB session
):
    # Call service to return appointments filtered by role (admin, doctor, patient)
    return await GetAllAppointmentsService.get_all_appointments(token, db)
