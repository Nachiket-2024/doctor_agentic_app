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

    # Pydantic configuration to allow ORM object parsing  
    class Config(ConfigDict):
        from_attributes = True  # Enables compatibility with ORM objects

# ------------------------------------- Schema for Creating Admin -------------------------------------

# Schema used when creating a new admin  
class AdminCreate(AdminBase):
    # Inherits fields from AdminBase; used for creating new Admin records  
    pass

# ------------------------------------- Schema for Reading Admin -------------------------------------

# Schema used when returning admin data from the API  
class AdminRead(AdminBase):
    # Admin's unique ID in the database (included in response)  
    id: int

    # Pydantic configuration to allow ORM object parsing  
    class Config(ConfigDict):
        from_attributes = True  # Enables compatibility with ORM objects
