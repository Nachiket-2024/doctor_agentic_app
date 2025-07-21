# --- Environment setup ---
from dotenv import load_dotenv                      # Load environment variables from .env
from pathlib import Path                            # Work with paths in an OS-agnostic way

# Calculate base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
_ = load_dotenv(dotenv_path=BASE_DIR / ".env")     # Load .env variables

# --- FastAPI imports ---
from fastapi import FastAPI             # Core FastAPI imports
from fastapi.middleware.cors import CORSMiddleware # CORS middleware for frontend-backend communication

# Auth and Cookie routes
from .auth.auth_routes import router as auth_router

# --- Import route modules ---
from .api.doctor_routes import router as doctor_router
from .api.patient_routes import router as patient_router
from .api.appointment_routes import router as appointment_router

# --- Create the FastAPI app instance ---
app = FastAPI()

# --- Enable CORS (allow frontend to access the backend) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register modular routers with the app ---
app.include_router(auth_router)         # Handles all /auth routes
app.include_router(doctor_router)       # Handles all /doctors routes
app.include_router(appointment_router)  # Handles all /appointments routes
app.include_router(patient_router)      # Handles all /patients routes


@app.get("/")
def read_root():
    return {"message": "Welcome to the Doctor Agentic app!"}
