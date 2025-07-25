# ---------------------------- External Imports ----------------------------

# Import the standard `os` module for accessing environment variables
import os

# Import typing's Generator to define function return types that yield values
from typing import Generator

# Import SQLAlchemy engine creation and session-related classes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import dotenv to load environment variables from a `.env` file
from dotenv import load_dotenv

# Import `Path` for resolving and constructing filesystem paths
from pathlib import Path


# ---------------------------- Load Environment Variables ----------------------------

# Resolve the project root directory (three levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Construct the path to the `.env` file located at the root
env_path = BASE_DIR / ".env"

# Load environment variables from the `.env` file into the current environment
_ = load_dotenv(dotenv_path=env_path)


# ---------------------------- Database Configuration ----------------------------

# Fetch the database URL from the environment
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Raise an error if the environment variable is missing
if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the .env file.")

# Extract the database name from the connection URL (for logging/debugging if needed)
db_name = SQLALCHEMY_DATABASE_URL.split('/')[-1]


# ---------------------------- SQLAlchemy Engine and Session Setup ----------------------------

# Create the SQLAlchemy engine instance to manage DB connections
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a sessionmaker instance to create new database sessions
SessionLocal = sessionmaker(
    autocommit=False,  # Disable automatic commit — manual commit required
    autoflush=False,   # Disable automatic flush of changes to the DB
    bind=engine        # Bind this sessionmaker to our DB engine
)


# ---------------------------- Dependency for DB Session ----------------------------

# Define a generator function to provide a database session
# This is typically used in FastAPI routes as a dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()  # Create a new session
    try:
        yield db          # Yield the session to the request handler
    finally:
        db.close()        # Ensure session is closed after the request finishes
