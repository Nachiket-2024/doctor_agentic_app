# --- Import FastAPI to create the app ---
from fastapi import FastAPI

# --- Import routers using relative imports ---
from .api.doctor_routes import doctor_router
from .api.appointment_routes import appointment_router

# --- Create FastAPI app instance ---
app = FastAPI()

# --- Register routers ---
app.include_router(doctor_router)
app.include_router(appointment_router)
