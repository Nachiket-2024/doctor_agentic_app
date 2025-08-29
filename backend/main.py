# ---------------------------- External Imports ----------------------------
# Import FastAPI framework to create API application
from fastapi import FastAPI

# Import CORS middleware to handle Cross-Origin Resource Sharing
from fastapi.middleware.cors import CORSMiddleware

# Import asyncio for asynchronous background task execution
import asyncio

# Import asynccontextmanager to manage startup/shutdown context for the app
from contextlib import asynccontextmanager

# ---------------------------- Internal Imports ----------------------------
# Import shared MCP instance for background task execution
from .mcp_main import mcp

# Import centralized settings for environment variables
from .core.settings import settings

# Import authentication route handlers
from .auth.auth_routes import router as auth_router

# Import doctor route handlers
from .api.doctor_routes import router as doctor_router

# Import patient route handlers
from .api.patient_routes import router as patient_router

# Import appointment route handlers
from .api.appointment_routes import router as appointment_router

# Import doctor slot availability route handlers
from .api.doctor_slot_routes import router as doctor_slot_router

# ---------------------------- Lifespan Context ----------------------------
# Define FastAPI lifespan context to manage startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context to run MCP asynchronously on startup."""

    # Parse host and port from MCP_URL setting (format: http://host:port)
    host_port = settings.MCP_URL.split("//")[1].split(":")
    host = host_port[0]           # Hostname part
    port = int(host_port[1])      # Port as integer

    # Start MCP asynchronously in a background task
    loop = asyncio.get_event_loop()
    loop.create_task(mcp.run_async(host=host, port=port))

    # Yield control to FastAPI; app continues running while inside this block
    yield

# ---------------------------- App Initialization ----------------------------
# Create FastAPI app instance with lifespan context
app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_REDIRECT_URI],  # Allow requests from frontend origin only
    allow_credentials=True,                           # Allow cookies and credentials
    allow_methods=["*"],                              # Allow all HTTP methods
    allow_headers=["*"],                              # Allow all headers
)

# ---------------------------- Router Registration ----------------------------
# Register authentication routes
app.include_router(auth_router)

# Register doctor routes
app.include_router(doctor_router)

# Register doctor slot availability routes
app.include_router(doctor_slot_router)

# Register appointment routes
app.include_router(appointment_router)

# Register patient routes
app.include_router(patient_router)

# ---------------------------- Root Route ----------------------------
# Define a simple root endpoint to verify the API is running
@app.get("/")
def read_root():
    """Simple root endpoint to verify the API is running."""
    return {"message": "Welcome to the Doctor Agentic app!"}
