# ------------------------------------- External Imports -------------------------------------

# For defining column schema and types  
from sqlalchemy import Column ,Integer ,String 

# ------------------------------------- Internal Imports -------------------------------------

# For accessing the declarative base for SQLAlchemy models  
from ..db.base import Base  

# ------------------------------------- Model Declaration -------------------------------------

# Define the Admin model for administrator users  
class Admin(Base):  
    """
    Admin model represents the administrators for the system.
    Admin users have global access to the entire system.
    """

    # Specify the table name for this model in the database  
    __tablename__ = 'admins'  

    # Unique identifier for each admin (Primary Key, auto-incremented)  
    id = Column(Integer, primary_key=True, autoincrement=True)  

    # Name of the admin (cannot be null)  
    name = Column(String, nullable=False)  

    # Email of the admin (must be unique and non-null)  
    email = Column(String, unique=True, nullable=False)  
