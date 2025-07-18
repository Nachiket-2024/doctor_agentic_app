# --- Import necessary components ---
from sqlalchemy import create_engine  # To create a connection to the database using SQLAlchemy
from dotenv import load_dotenv  # To load environment variables from the .env file
import os  # To interact with environment variables and file paths

# --- Load environment variables from .env ---
load_dotenv()  # Loads environment variables from the .env file into the environment

# --- Database URL from the .env file ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/doctor_db")
# Retrieves the DATABASE_URL from environment variables (or uses a default if not set)
# The URL follows the format: 'postgresql://username:password@host:port/database_name'

# --- Create SQLAlchemy engine ---
engine = create_engine(DATABASE_URL)  # Creates an SQLAlchemy engine to connect to the database using the DATABASE_URL
