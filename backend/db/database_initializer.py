# ---------------------------- Internal Imports ----------------------------
# Import the session manager that handles DB engine and sessions
from .database_session_manager import DatabaseSessionManager

# Import the base class that maintains metadata for all models
from .base import Base

# Import model classes so their table definitions are registered with SQLAlchemy
from ..models.doctor_model import Doctor
from ..models.patient_model import Patient
from ..models.admin_model import Admin
from ..models.appointment_model import Appointment

# ---------------------------- Class: DatabaseInitializer ----------------------------
class DatabaseInitializer:
    """
    Responsible for initializing the database schema by creating all tables
    registered with the SQLAlchemy Base metadata.
    """

    def __init__(self, db_manager: DatabaseSessionManager):
        # Store reference to the session manager instance
        self.engine = db_manager.engine

    def initialize_schema(self) -> None:
        """
        Initializes the database schema.

        - Uses `Base.metadata.create_all(...)` to scan all imported model classes.
        - Typically run during development or test bootstrapping.
        - For production migrations, prefer Alembic.
        """
        Base.metadata.create_all(bind=self.engine)

# ---------------------------- Entry Point for Direct Execution ----------------------------
# Allow direct execution to initialize the DB schema via CLI
if __name__ == "__main__":
    # Instantiate the session manager
    db_manager = DatabaseSessionManager()

    # Instantiate and run the initializer
    initializer = DatabaseInitializer(db_manager)
    initializer.initialize_schema()
