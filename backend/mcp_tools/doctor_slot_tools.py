# ---------------------------- External Imports ----------------------------

# Import the tool decorator from FastAPI MCP
from fastapi_mcp import tool

# Import SQLAlchemy Session for database access
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Import the service function to fetch available slots for a doctor
from ..services.doctor_slot.doctor_slot_availability_service import DoctorSlotAvailabilityService

# ---------------------------- Tool: Get Available Doctor Slots ----------------------------

# MCP tool to retrieve available slot start times for a given doctor and date
@tool(name="get_available_slots_by_doctor", description="Get available time slots for a doctor on a specific date.")
async def get_available_slots_tool(
    doctor_id: int,                   # Doctor's unique ID
    date_str: str,                    # Date string in 'YYYY-MM-DD' format
    db: Session                       # Injected SQLAlchemy database session
):
    # Call the corresponding service to fetch the available slots
    return await DoctorSlotAvailabilityService.get_available_slots_by_doctor_id(doctor_id, date_str, db)
