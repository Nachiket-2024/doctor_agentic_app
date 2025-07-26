# ------------------------------------- External Imports -------------------------------------

# For defining column schema and types  
from sqlalchemy import Column, Integer, String

# ------------------------------------- Internal Imports -------------------------------------

# For accessing the declarative base for SQLAlchemy models  
from ..db.base import Base

# ------------------------------------- Model Declaration -------------------------------------

# Define the Admin model for administrator users  
class Admin(Base):  
    """
    Admin model represents the administrators for the system.
    Admin users have global access to the entire system.
    Includes Google token fields for sending Calendar invites or Gmail via admin account.
    """

    # Specify the table name for this model in the database  
    __tablename__ = 'admins'

    # Unique identifier for each admin (Primary Key, auto-incremented)  
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Name of the admin (cannot be null)  
    name = Column(String, nullable=False)

    # Email of the admin (must be unique and non-null)  
    email = Column(String, unique=True, nullable=False)

    # ---------------- Google OAuth Token Fields ----------------

    # Access token to allow admin to interact with Google APIs (e.g., Gmail, Calendar)  
    access_token = Column(String, nullable=True)

    # Refresh token to obtain new access tokens when the previous one expires  
    refresh_token = Column(String, nullable=True)

    # Optional ISO timestamp or string indicating when the token will expire  
    token_expiry = Column(String, nullable=True)
