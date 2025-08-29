# ------------------------------------- External Imports -------------------------------------
# Import BaseModel and ConfigDict from Pydantic for schema creation and configuration  
from pydantic import BaseModel, ConfigDict

# ------------------------------------- Base Schema for Admin -------------------------------------
# Define base schema with common admin fields  
class AdminBase(BaseModel):
    # Admin's full name (required)  
    name: str

    # Admin's email address (required)  
    email: str

    # Google access token for calendar/email integration (optional)  
    access_token: str | None = None

    # Google refresh token to regenerate access token (optional)  
    refresh_token: str | None = None

    # Expiry time of token in ISO string or timestamp (optional)  
    token_expiry: str | None = None

    # Pydantic config to allow compatibility with ORM models (like SQLAlchemy)  
    class Config(ConfigDict):
        from_attributes = True

# ------------------------------------- Schema for Creating Admin -------------------------------------
# Schema used when creating a new admin  
class AdminCreate(AdminBase):
    # Inherits all fields from AdminBase  
    pass

# ------------------------------------- Schema for Reading Admin -------------------------------------
# Schema used when returning admin data from the API  
class AdminRead(AdminBase):
    # Admin's unique database ID (included in read schema)  
    id: int

    # Pydantic config to allow compatibility with ORM models (like SQLAlchemy)  
    class Config(ConfigDict):
        from_attributes = True
