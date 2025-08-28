# ---------------------------- External Imports ----------------------------

# Import FastAPI framework to create the API app
from fastapi import FastAPI

# Import middleware to handle Cross-Origin Resource Sharing
from fastapi.middleware.cors import CORSMiddleware

# Import asyncio for background task execution
import asyncio

# Import asynccontextmanager to manage startup/shutdown context
from contextlib import asynccontextmanager

# ---------------------------- Internal Imports ----------------------------

# Import shared MCP instance for background processing
from .mcp_main import mcp

# Import centralized settings (loads environment variables)
from .core.settings import settings

# Import authentication route handlers
from .auth.auth_routes import router as auth_router

# Import doctor route handlers
from .api.doctor_routes import router as doctor_router

# Import patient route handlers
from .api.patient_routes import router as patient_router

# Import appointment route handlers
from .api.appointment_routes import router as appointment_router

# Import doctor slot availability handlers
from .api.doctor_slot_routes import router as doctor_slot_router

# ---------------------------- Lifespan Context ----------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context to run MCP asynchronously on startup."""

    # Parse host and port from MCP_URL (format: http://host:port)
    host_port = settings.MCP_URL.split("//")[1].split(":")
    host = host_port[0]
    port = int(host_port[1])

    # Start MCP as a background asynchronous task
    loop = asyncio.get_event_loop()
    loop.create_task(mcp.run_async(host=host, port=port))

    # Yield control to FastAPI; app runs while inside this block
    yield

    # Optional cleanup on shutdown (currently no tasks needed)

# ---------------------------- App Initialization ----------------------------

# Create FastAPI app instance with lifespan context
app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow frontend access dynamically
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_REDIRECT_URI],  # allow only frontend origin
    allow_credentials=True,                           # allow cookies/credentials
    allow_methods=["*"],                              # allow all HTTP methods
    allow_headers=["*"],                              # allow all headers
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

@app.get("/")
def read_root():
    """Simple root endpoint to verify the API is running."""
    return {"message": "Welcome to the Doctor Agentic app!"}
