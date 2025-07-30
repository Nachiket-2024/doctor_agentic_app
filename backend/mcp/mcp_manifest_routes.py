# ------------------------------------- External Imports -------------------------------------

# FastAPI request and JSON response utilities
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse


# ------------------------------------- Router Setup -------------------------------------

# Create a router for manifest-related endpoints
router = APIRouter()


# ------------------------------------- Route: Serve Dynamic MCP Manifest -------------------------------------

# GET endpoint to serve dynamic MCP manifest for discovery
@router.get("/.well-known/ai-plugin.json", include_in_schema=False)
def serve_ai_plugin_manifest(request: Request):
    """
    Returns a dynamically generated MCP plugin manifest with no hardcoded URLs.
    """
    # Extract base URL from the incoming request (e.g., http://localhost:8000)
    base_url = str(request.base_url).rstrip("/")

    # Define the manifest with dynamic URLs
    manifest = {
        "schema_version": "v1",
        "name_for_human": "Doctor Scheduler Tool",
        "name_for_model": "doctor_scheduler_tool",
        "description_for_human": "Check doctor availability and manage appointments.",
        "description_for_model": (
            "Use this tool to check available time slots for a doctor on a given date. "
            "Input must include doctor_id and a target date."
        ),
        "auth": {
            "type": "none"
        },
        "api": {
            "type": "openapi",
            "url": f"{base_url}/openapi.json",
            "is_user_authenticated": False
        },
        "logo_url": f"{base_url}/static/logo.png",  # Optional logo file
        "contact_email": "support@example.com",
        "legal_info_url": f"{base_url}/legal"
    }

    # Return the manifest as a JSON response
    return JSONResponse(content=manifest)
