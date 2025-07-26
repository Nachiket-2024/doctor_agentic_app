# ------------------------------------- External Imports -------------------------------------

# Import necessary SQLAlchemy column types for defining model attributes  
from sqlalchemy import Column, Integer, ForeignKey, String  

# Import relationship function for ORM relationship mapping between tables  
from sqlalchemy.orm import relationship  

# ------------------------------------- Internal Imports -------------------------------------

# Import the base class that all SQLAlchemy models inherit from  
from ..db.base import Base  

# Import the User model to associate tokens with users  
from .user_model import User  


# ------------------------------------- Google Integration Model -------------------------------------

# Define the GoogleIntegration model class that stores tokens for Gmail/Calendar usage  
class GoogleIntegration(Base):

    # Define the table name in the database  
    __tablename__ = 'google_integrations'

    # Primary key column uniquely identifying each record  
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key referencing the associated user in the users table  
    user_id = Column(Integer, ForeignKey(User.id), unique=True, nullable=False)

    # String column storing the latest access token for Google APIs  
    access_token = Column(String, nullable=False)

    # String column storing the refresh token to renew access token  
    refresh_token = Column(String, nullable=False)

    # Optional string column to store token expiry (ISO string or timestamp)  
    token_expiry = Column(String, nullable=True)

    # Relationship to access user details from the token record  
    user = relationship("User", foreign_keys=[user_id])
