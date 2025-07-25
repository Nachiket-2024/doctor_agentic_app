# ---------------------------- External Imports ----------------------------

# FastAPI exception and dependency tools
from fastapi import HTTPException, Depends  

# Tool to extract token from the Authorization header using OAuth2
from fastapi.security import OAuth2PasswordBearer  

# SQLAlchemy session dependency for interacting with the database
from sqlalchemy.orm import Session  

# Exception class for handling JWT errors
from jose import JWTError  

# ---------------------------- Internal Imports ----------------------------

# Function to obtain a database session
from ..db.session import get_db  

# Function to decode and verify JWT tokens
from .auth_utils import verify_jwt_token  

# Admin model used to check admin privileges
from ..models.admin_model import Admin  


# ---------------------------- OAuth2 Setup ----------------------------

# Initialize the OAuth2PasswordBearer scheme
# This tells FastAPI to look for a token in the "Authorization: Bearer <token>" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ---------------------------- Dependency: Admin-Only Access ----------------------------

def admin_only(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency that allows access only to admin users.
    Extracts user info from JWT token and checks against the Admin table.
    """
    try:
        # Step 1: Verify and decode the JWT token to get the payload
        payload = verify_jwt_token(token)

        # Step 2: Extract user email from the payload ('sub' usually holds the subject/user identifier)
        user_email = payload.get("sub")

        # Step 3: Query the Admin table to check if the user exists and is an admin
        admin = db.query(Admin).filter(Admin.email == user_email).first()

        # Step 4: If no admin record is found, raise 403 Forbidden
        if not admin:
            raise HTTPException(status_code=403, detail="Admin access required")

        # Step 5: If valid admin, return the admin object (can be used in the route handler if needed)
        return admin

    except JWTError:
        # Token was invalid or could not be decoded
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    except Exception as e:
        # Catch any other unexpected server error
        raise HTTPException(status_code=500, detail=str(e))
