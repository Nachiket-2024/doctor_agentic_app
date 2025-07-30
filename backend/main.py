# ---------------------------- External Imports ----------------------------

# Load environment variables from .env file  
from dotenv import load_dotenv

# Work with file paths in an OS-independent way  
from pathlib import Path

# Import FastAPI framework  
from fastapi import FastAPI

# Middleware to handle Cross-Origin Resource Sharing  
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------- Environment Setup ----------------------------

# Get the base directory (3 levels up from current file)  
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from the .env file in base directory  
_ = load_dotenv(dotenv_path=BASE_DIR / ".env")

# ---------------------------- Internal Imports ----------------------------

# Authentication route handlers  
from .auth.auth_routes import router as auth_router

# Doctor route handlers  
from .api.doctor_routes import router as doctor_router

# Patient route handlers  
from .api.patient_routes import router as patient_router

# Appointment route handlers  
from .api.appointment_routes import router as appointment_router

# Doctor slot availability handlers  
from .api.doctor_slot_routes import router as doctor_slot_router

# Availability Tool route handlers
from .mcp.availability_tool_routes import router as availability_tool_router

# MCP Manifest router handlers
from .mcp.mcp_manifest_routes import router as mcp_manifest_router

# LLM router handlers
from .llm_integration.llm_routes import router as llm_router


# ---------------------------- App Initialization ----------------------------

# Create a FastAPI application instance  
app = FastAPI()

# ---------------------------- Middleware Configuration ----------------------------

# Enable CORS to allow frontend (e.g., React app) to access backend  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------- Router Registration ----------------------------

# Register authentication-related routes under /auth  
app.include_router(auth_router)

# Register doctor-specific routes under /doctors  
app.include_router(doctor_router)

# Register doctor slot management routes under /doctor_slot  
app.include_router(doctor_slot_router)

# Register appointment-related routes under /appointments  
app.include_router(appointment_router)

# Register patient-specific routes under /patients  
app.include_router(patient_router)

# Register Availability Tool router under /tools/availability
app.include_router(availability_tool_router)

# Register MCP Manifest router under /.well-known/ai-plugin.json
app.include_router(mcp_manifest_router)

# Register LLM router under /llm
app.include_router(llm_router)

# ---------------------------- Root Route ----------------------------

# Define a simple root route to verify the API is running  
@app.get("/")
def read_root():
    return {"message": "Welcome to the Doctor Agentic app!"}
