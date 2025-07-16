# --- Import necessary components ---
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# --- Load environment variables from .env ---
load_dotenv()

# --- Database URL from the .env file ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/doctor_db")

# --- Create SQLAlchemy engine ---
engine = create_engine(DATABASE_URL)

# --- Export the engine so it can be used in session and models ---
