# ---------------------------- External Imports ----------------------------

# Import DeclarativeBase from SQLAlchemy's ORM package for model definitions
from sqlalchemy.orm import DeclarativeBase


# ---------------------------- Base ORM Class Definition ----------------------------

# Define a base class for all ORM models in the application.
# All model classes (e.g., User, Admin, Appointment) will inherit from this `Base` class.
# This provides SQLAlchemy the metadata it needs to map models to DB tables.
class Base(DeclarativeBase):
    pass  # No additional customization is required at this point
