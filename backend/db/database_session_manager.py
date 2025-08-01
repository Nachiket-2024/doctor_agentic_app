# ---------------------------- External Imports ----------------------------

# Import typing's Generator to define function return types that yield values
from typing import Generator

# Import SQLAlchemy engine creation and session-related classes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Application-wide settings from environment
from ..core.settings import settings

# ---------------------------- Class: DatabaseSessionManager ----------------------------

class DatabaseSessionManager:
    """
    Handles environment-based DB config, initializes SQLAlchemy engine/sessionmaker,
    and provides a dependency for yielding DB sessions.
    """

    # ------------------------ Constructor: Initialize DB Engine and Session ------------------------

    def __init__(self):
        # Fetch the database URL from the environment settings
        db_url = settings.DATABASE_URL

        # Store the DB name for logging/debugging purposes
        self.db_name = db_url.split("/")[-1]

        # Create the SQLAlchemy engine instance for managing DB connections
        self.engine = create_engine(db_url)

        # Create a sessionmaker factory bound to the DB engine
        self.SessionLocal = sessionmaker(
            autocommit=False,  # Prevent auto-committing transactions
            autoflush=False,   # Disable auto-flushing of changes to DB
            bind=self.engine   # Bind sessionmaker to the created engine
        )

    # ------------------------ Dependency: Yield DB Session ------------------------

    def get_db(self) -> Generator[Session, None, None]:
        """
        Yields a database session. Use this as a FastAPI dependency.
        Ensures the session is closed after request completion.
        """

        # Create a new database session instance
        db = self.SessionLocal()

        try:
            # Yield the session to the calling route or service
            yield db

        finally:
            # Close the session after the request completes
            db.close()
