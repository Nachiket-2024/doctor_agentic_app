from sqlalchemy import create_engine  # To create the database engine connection
from sqlalchemy.orm import sessionmaker  # To create sessions for interacting with the database
from ..auth import settings  # Import settings, including the DATABASE_URL, from the auth module

# Create the SQLAlchemy engine using the DATABASE_URL from settings
engine = create_engine(settings.DATABASE_URL)

# Create a session factory that will allow us to generate DB sessions
# autocommit=False: Disables autocommit, meaning transactions need to be explicitly committed
# autoflush=False: Disables autoflush, meaning queries won't be automatically flushed to the database
# bind=engine: Bind the session to the previously created engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency function to provide a database session
def get_db():
    """
    This function provides a database session to be used in API route handlers.
    The session will be closed automatically after the request finishes.
    """
    db = SessionLocal()  # Create a new session using the sessionmaker
    try:
        yield db  # Yield the session to be used by the request handler
    finally:
        db.close()  # Ensure the session is closed after the request is processed
