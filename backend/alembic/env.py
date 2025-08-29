# ---------------------------- External Imports ----------------------------
# Import logging configuration utility to configure loggers from a file
from logging.config import fileConfig

# Import SQLAlchemy engine creation function and connection pool
from sqlalchemy import engine_from_config
from sqlalchemy import pool

# Import Alembic migration context
from alembic import context

# Import system and OS utilities for path manipulation
import sys
import os

# Import dotenv to load environment variables from a .env file
from dotenv import load_dotenv

# ---------------------------- Internal Imports ----------------------------
# Import the declarative base for SQLAlchemy models
from app.db.base import Base  

# Import all the models so Alembic can detect schema changes
from app.models import admin_model, doctor_model, patient_model, appointment_model  

# ---------------------------- Path Setup ----------------------------
# Add the parent directory to sys.path so that app modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ---------------------------- Environment Setup ----------------------------
# Load environment variables from .env file
load_dotenv()

# ---------------------------- Alembic Config Setup ----------------------------
# Get the Alembic Config object which provides access to .ini file values
config = context.config

# Override the SQLAlchemy URL from environment variable
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Configure logging from the Alembic config file if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------- Metadata Setup ----------------------------
# Set the target metadata for 'autogenerate' support in Alembic
target_metadata = Base.metadata

# ---------------------------- Offline Migrations ----------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (without a DB engine)."""
    # Retrieve the SQLAlchemy URL
    url = config.get_main_option("sqlalchemy.url")

    # Configure the Alembic context for offline migrations
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    # Run the migrations within a transaction context
    with context.begin_transaction():
        context.run_migrations()

# ---------------------------- Online Migrations ----------------------------
def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with a DB engine)."""
    # Create a SQLAlchemy engine from the Alembic config
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Connect to the database and configure Alembic context
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        # Run the migrations within a transaction context
        with context.begin_transaction():
            context.run_migrations()

# ---------------------------- Migration Execution ----------------------------
# Decide whether to run offline or online migrations based on context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
