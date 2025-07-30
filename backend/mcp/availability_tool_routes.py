# ------------------------------------- External Imports -------------------------------------

# FastAPI routing, dependency injection, and exceptions
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy session for DB access
from sqlalchemy.orm import Session

# ------------------------------------- Internal Imports -------------------------------------

# Session dependency
from ..db.session import get_db

# Input/output schemas for the tool
from ..schemas.tool_schema import CheckAvailabilityInput, CheckAvailabilityOutput

# Shared logic reused from the main route
from ..tools.availability_logic import get_available_slots_logic


# ------------------------------------- Router Setup -------------------------------------

# Create a router for tool-related endpoints
router = APIRouter(
    prefix="/tools/availability",
    tags=["MCP Tools"],
)


# ------------------------------------- MCP Tool Endpoint -------------------------------------

# POST endpoint for checking availability via MCP tool
@router.post("/check", response_model=CheckAvailabilityOutput)
def mcp_check_doctor_availability(
    input_data: CheckAvailabilityInput,        # Input schema with doctor_id and date
    db: Session = Depends(get_db),             # Inject the DB session
):
    """
    Tool endpoint to return available slots for a doctor on a specific date.
    Designed for use by LLM agents via MCP.
    """
    try:
        # Use the shared logic to fetch available slots
        slots = get_available_slots_logic(
            doctor_id=input_data.doctor_id,
            target_date=input_data.date,
            db=db
        )
        # Return in schema-defined format
        return CheckAvailabilityOutput(available_slots=slots)

    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
