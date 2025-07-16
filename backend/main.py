# --- Import FastAPI core and dependencies ---
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # To allow frontend-backend communication

# --- Import environment loader ---
from dotenv import load_dotenv  # To load .env variables

# --- Load environment variables from .env file ---
load_dotenv()

# --- Import route modules ---
from .api.doctor_routes import router as doctor_router
from .api.patient_routes import router as patient_router
from .api.appointment_routes import router as appointment_router

# --- Create the FastAPI app instance ---
app = FastAPI()

# --- Enable CORS (allow frontend to access the backend) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["http://localhost:5173"] or prod URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register modular routers with the app ---
app.include_router(doctor_router)       # Handles all /doctors routes
app.include_router(appointment_router)  # Handles all /appointments routes
app.include_router(patient_router)      # Handles all /patients routes

# --- Root route for basic server health check ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Doctor Appointment Agentic API"}
