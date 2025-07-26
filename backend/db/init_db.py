# ---------------------------- Internal Imports ----------------------------

# Import the SQLAlchemy engine instance used to connect to the database
from .session import engine

# Import the base class that maintains metadata for all models
from .base import Base

# Import model classes so their table definitions are registered with SQLAlchemy
from ..models.doctor_model import Doctor
from ..models.patient_model import Patient
from ..models.admin_model import Admin
from ..models.appointment_model import Appointment


# ---------------------------- Database Initialization ----------------------------

def init_db() -> None:
    """
    Initializes the database schema by creating all registered tables.

    - `Base.metadata.create_all(...)` reads all model classes attached to the `Base`
      and creates the corresponding tables in the database.
    - `bind=engine` tells SQLAlchemy which DB connection to use.
    - This is typically used only for initial development or testing — in production,
      you'd usually use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)


# ---------------------------- Entry Point for Direct Execution ----------------------------

# This allows running the script directly (e.g., `python db/init_db.py`) to initialize the DB.
# When the file is executed as a standalone script, it calls `init_db()` to create tables.
if __name__ == "__main__":
    init_db()
