# ------------------------------------- Imports -------------------------------------

# Import OS module to read environment variables from the system
import os

# FastAPI imports for routing and HTTP handling
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

# SQLAlchemy ORM for interacting with the database
from sqlalchemy.orm import Session

# Load environment variables from a .env file
from dotenv import load_dotenv

# JWTError to handle exceptions during JWT validation
from jose import JWTError

# OAuth2 scheme for reading tokens from Authorization headers
from fastapi.security import OAuth2PasswordBearer

# Internal utility functions related to authentication logic
from .auth_utils import authenticate_with_google, create_jwt_token, verify_jwt_token

# Import User and Admin models from internal modules
from ..models.user_model import User
from ..models.admin_model import Admin

# Function to retrieve a database session
from ..db.session import get_db

# Load environment variables (client ID, secret, scopes, etc.) from .env file
load_dotenv()

# Configure token extraction from Authorization: Bearer <token> header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a FastAPI APIRouter for grouping authentication-related endpoints
router = APIRouter(
    prefix="/auth",            # All endpoints under this router will be prefixed with /auth
    tags=["Authentication"],   # Tag used for organizing docs in Swagger UI
)


# ---------------------------- Route: Google Login Initiation ----------------------------

@router.get("/login")
async def login_with_google(request: Request, db: Session = Depends(get_db)):
    """
    Initiates the Google OAuth2 flow.
    Redirects the user to the Google authentication page.
    """
    try:
        # Base URL for Google's OAuth2 authentication endpoint
        google_oauth_url = "https://accounts.google.com/o/oauth2/v2/auth"

        # Fetch the requested scopes from environment and URL-encode them
        scopes = os.getenv("GOOGLE_SCOPES", "")             # e.g., openid,email,profile,...
        formatted_scopes = scopes.replace(",", "%20")       # Convert commas to %20 (space in URL encoding)

        # Construct the full OAuth2 authorization URL
        auth_url = (
            f"{google_oauth_url}?response_type=code"
            f"&client_id={os.getenv('GOOGLE_CLIENT_ID')}"               # App's client ID
            f"&redirect_uri={os.getenv('GOOGLE_REDIRECT_URI')}"         # Must match what is set in Google Console
            f"&scope={formatted_scopes}"                                # Requested scopes
            f"&access_type=offline"                                     # To get refresh token
            f"&include_granted_scopes=true"                             # To allow incremental scopes
            f"&prompt=consent"                                          # Force the consent screen every time
        )

        # Redirect the user to Google's OAuth2 login page
        return RedirectResponse(url=auth_url)

    except Exception as e:
        # Catch and return any exception as a client error
        raise HTTPException(status_code=400, detail=f"Google OAuth2 Authentication Failed: {str(e)}")


# ---------------------------- Route: OAuth2 Callback ----------------------------

@router.get("/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Handle the Google OAuth2 callback and exchange the authorization code for a JWT token.
    """
    try:
        # Step 1: Exchange the authorization code for user info (includes Google email)
        user_info = authenticate_with_google(code, db)

        # Step 2: Check if the authenticated user is an admin
        admin = db.query(Admin).filter(Admin.email == user_info['email']).first()

        # Step 3: Determine the user's role
        if admin:
            role = "admin"  # If admin exists, assign admin role
        else:
            # If not admin, check if the user exists in the users table
            user = db.query(User).filter(User.email == user_info['email']).first()
            if user:
                role = user.role  # Use role from DB
            else:
                role = "patient"  # Default to "patient" if user is not found

        # Step 4: Generate a JWT token containing user info
        jwt_token = create_jwt_token(user_info)

        # Debug log (optional): Print the generated JWT token to console
        print(f"Generated JWT Token: {jwt_token}")

        # Step 5: Define the frontend redirect URL after login
        frontend_url = os.getenv("FRONTEND_REDIRECT_URI", "http://localhost:5173/dashboard")

        # Step 6: Append token and role as query params to frontend URL
        redirect_url = f"{frontend_url}?access_token={jwt_token}&role={role}"

        # Debug log (optional): Print the redirect URL
        print(f"Redirect URL: {redirect_url}")

        # Step 7: Redirect user to frontend with token and role
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        # Catch and return any exception as a client error
        raise HTTPException(status_code=400, detail=f"Google OAuth2 Authentication Failed: {str(e)}")


# ---------------------------- Route: Get Current Authenticated User ----------------------------

@router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get current authenticated user's information based on the JWT token.
    Checks both User and Admin tables.
    """
    try:
        # Step 1: Decode the JWT token and extract the email
        payload = verify_jwt_token(token)
        email = payload["sub"]

        # Step 2: Try finding the user in the User table
        user = db.query(User).filter(User.email == email).first()
        if user:
            return {
                "email": user.email,
                "name": user.name,
                "role": user.role
            }

        # Step 3: If not found, try in the Admin table
        admin = db.query(Admin).filter(Admin.email == email).first()
        if admin:
            return {
                "email": admin.email,
                "name": admin.name,
                "role": "admin"  # Role is hardcoded for admins
            }

        # If neither user nor admin exists, raise not found
        raise HTTPException(status_code=404, detail="User not found")

    except JWTError:
        # JWT is invalid or expired
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        # General server error
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Logout ----------------------------

@router.post("/logout")
async def logout():
    """
    Logout the user. Since JWT is stateless, this will simply remove the token from the client side.
    The frontend should delete the token from localStorage/sessionStorage.
    """
    return JSONResponse(content={
        "message": "Successfully logged out. Please delete the token from your client(frontend)."
    })
