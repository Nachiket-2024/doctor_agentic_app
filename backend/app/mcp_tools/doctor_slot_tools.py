# ---------------------------- External Imports ----------------------------
# Import SQLAlchemy Session for database operations
from sqlalchemy.orm import Session  # Typed DB session for service calls

# ---------------------------- Internal Imports ----------------------------
# Import the shared MCP instance to define tools
from ..mcp_main import mcp  

# Import service to fetch available slots for a doctor
from ..services.doctor_slot.doctor_slot_availability_service import DoctorSlotAvailabilityService

# ---------------------------- Tool: Get Available Doctor Slots ----------------------------
# Define MCP tool to retrieve available slots for a specific doctor and date
@mcp.tool(
    name="get_available_slots_by_doctor",  # Tool name
    description="Get available time slots for a doctor on a specific date.",  # Tool description
    exclude_args=["db"]  # Exclude the database session from external arguments
)
# Async function to fetch available doctor slots
async def get_available_slots_tool(
    doctor_id: int,                   # Doctor's unique ID
    date_str: str,                    # Date in 'YYYY-MM-DD' format
    db: Session | None = None          # Optional database session injected by MCP
):
    # Call the service function to get the available slots for the doctor
    return await DoctorSlotAvailabilityService.get_available_slots_by_doctor_id(doctor_id, date_str, db)
