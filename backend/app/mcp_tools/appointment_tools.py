# ---------------------------- External Imports ----------------------------
# Import SQLAlchemy ORM Session for database operations
from sqlalchemy.orm import Session  # SQLAlchemy Session for typed DB access

# ---------------------------- Internal Imports ----------------------------
# Import the shared MCP instance for defining tools
from ..mcp_main import mcp  

# Import service to create a new appointment
from ..services.appointment.create_appointment_service import CreateAppointmentService

# Import service to retrieve an appointment by its ID
from ..services.appointment.get_appointment_by_id_service import GetAppointmentByIDService

# Import service to update an existing appointment
from ..services.appointment.update_appointment_service import UpdateAppointmentService

# Import service to delete an appointment
from ..services.appointment.delete_appointment_service import DeleteAppointmentService

# Import service to retrieve all appointments filtered by user role
from ..services.appointment.get_all_appointments_service import GetAllAppointmentsService

# ---------------------------- Tool: Create Appointment ----------------------------
# Define MCP tool to create a new appointment
@mcp.tool(
    name="create_appointment",  # Tool name
    description="Create a new appointment with patient and doctor info.",  # Tool description
    exclude_args=["db"]  # Exclude DB session from external arguments
)
# Async function to create an appointment
async def create_appointment_tool(
    appointment: dict,  # Appointment data payload
    token: str,         # Authorization token
    db: Session | None = None,  # Optional database session
):
    # Call service to create appointment
    return await CreateAppointmentService.create_appointment(appointment, token, db)

# ---------------------------- Tool: Get Appointment by ID ----------------------------
# Define MCP tool to retrieve a single appointment by its ID
@mcp.tool(
    name="get_appointment_by_id",  # Tool name
    description="Retrieve an appointment by its ID.",  # Tool description
    exclude_args=["db"]  # Exclude DB session from external arguments
)
# Async function to get appointment by ID
async def get_appointment_by_id_tool(
    appointment_id: int,  # Appointment's unique ID
    token: str,           # Authorization token
    db: Session | None = None,  # Optional database session
):
    # Call service to fetch appointment by ID
    return await GetAppointmentByIDService.get_appointment_by_id(appointment_id, token, db)

# ---------------------------- Tool: Update Appointment ----------------------------
# Define MCP tool to update an existing appointment
@mcp.tool(
    name="update_appointment",  # Tool name
    description="Update details of an existing appointment.",  # Tool description
    exclude_args=["db"]  # Exclude DB session from external arguments
)
# Async function to update appointment
async def update_appointment_tool(
    appointment_id: int,   # Appointment ID to update
    appointment_update: dict,  # Updated appointment data
    token: str,            # Authorization token
    db: Session | None = None,  # Optional database session
):
    # Call service to update appointment details
    return await UpdateAppointmentService.update_appointment(appointment_id, appointment_update, token, db)

# ---------------------------- Tool: Delete Appointment ----------------------------
# Define MCP tool to delete an appointment by ID
@mcp.tool(
    name="delete_appointment",  # Tool name
    description="Delete an appointment by ID.",  # Tool description
    exclude_args=["db"]  # Exclude DB session from external arguments
)
# Async function to delete appointment
async def delete_appointment_tool(
    appointment_id: int,  # Appointment ID to delete
    token: str,           # Authorization token
    db: Session | None = None,  # Optional database session
):
    # Call service to remove appointment
    return await DeleteAppointmentService.delete_appointment(appointment_id, token, db)

# ---------------------------- Tool: Get All Appointments ----------------------------
# Define MCP tool to retrieve all appointments accessible to the user
@mcp.tool(
    name="get_all_appointments",  # Tool name
    description="Fetch all appointments accessible to the user.",  # Tool description
    exclude_args=["db"]  # Exclude DB session from external arguments
)
# Async function to get all appointments
async def get_all_appointments_tool(
    token: str,           # Authorization token
    db: Session | None = None,  # Optional database session
):
    # Call service to fetch all appointments
    return await GetAllAppointmentsService.get_all_appointments(token, db)
