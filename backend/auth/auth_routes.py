# ---------------------------- External Imports ----------------------------

# To read environment variables from the system
import os  

# FastAPI tools for routing, dependencies, and HTTP errors
from fastapi import APIRouter, Depends, HTTPException, Request

# Response classes for JSON output and redirection
from fastapi.responses import JSONResponse, RedirectResponse 

# SQLAlchemy session for interacting with the database
from sqlalchemy.orm import Session  

# For loading environment variables from a .env file
from dotenv import load_dotenv  

# To handle JWT decoding and verification errors
from jose import JWTError  

# To extract Bearer token from Authorization header
from fastapi.security import OAuth2PasswordBearer  

# ---------------------------- Internal Imports ----------------------------

# Internal utility functions for Google auth and JWT
from .auth_utils import authenticate_with_google, create_jwt_token, verify_jwt_token

# User model from the database
from ..models.user_model import User  

# Admin model from the database
from ..models.admin_model import Admin 

# Dependency for getting DB session
from ..db.session import get_db  

# For checking and generating access token
from .google_token_service import get_valid_google_access_token

# ---------------------------- Setup ----------------------------

# Load variables from .env file like client ID, secret, and redirect URIs
load_dotenv()

# Set up FastAPI's OAuth2PasswordBearer to extract token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a FastAPI router to group authentication routes
router = APIRouter(
    prefix="/auth",            # All endpoints will be prefixed with /auth
    tags=["Authentication"],   # Tags shown in Swagger docs
)

# ---------------------------- Route: Google Login Initiation ----------------------------

@router.get("/login")
async def login_with_google(request: Request, db: Session = Depends(get_db)):
    """
    Initiates the Google OAuth2 login flow and redirects the user to the Google login page.
    """
    try:
        # Google's OAuth2 base URL
        google_oauth_url = "https://accounts.google.com/o/oauth2/v2/auth"

        # Fetch the required scopes from the environment variable
        scopes = os.getenv("GOOGLE_SCOPES", "")  # e.g., openid,email,profile

        # Replace commas with '%20' (space) to create a valid URL
        formatted_scopes = scopes.replace(",", "%20")

        # Build the complete Google OAuth2 authorization URL
        auth_url = (
            f"{google_oauth_url}?response_type=code"
            f"&client_id={os.getenv('GOOGLE_CLIENT_ID')}"
            f"&redirect_uri={os.getenv('GOOGLE_REDIRECT_URI')}"
            f"&scope={formatted_scopes}"
            f"&access_type=offline"
            f"&include_granted_scopes=true"
            f"&prompt=consent"
        )

        # Redirect the user to Google's OAuth2 login page
        return RedirectResponse(url=auth_url)

    except Exception as e:
        # Raise HTTP 400 if any error occurs during the redirect setup
        raise HTTPException(status_code=400, detail=f"Google OAuth2 Authentication Failed: {str(e)}")


# ---------------------------- Route: OAuth2 Callback ----------------------------

@router.get("/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Handles the callback after user logs in with Google.
    Exchanges code for user info, checks user/admin role, and redirects to frontend with token.
    """
    try:
        # Step 1: Authenticate the user via Google using the provided code
        user_info = authenticate_with_google(code, db)

        # Step 2: Check if the user is an admin
        admin = db.query(Admin).filter(Admin.email == user_info['email']).first()

        # Step 3: Assign role based on user type
        if admin:
            role = "admin"
        else:
            # Step 4: Check if the user is already registered
            user = db.query(User).filter(User.email == user_info['email']).first()
            role = user.role if user else "patient"

        # Step 5: Generate a JWT token for the authenticated user
        jwt_token = create_jwt_token(user_info)

        # Step 6: Get frontend URL to redirect the user after successful login
        frontend_url = os.getenv("FRONTEND_REDIRECT_URI")

        # Step 7: Append token and role to the frontend URL
        redirect_url = f"{frontend_url}?access_token={jwt_token}&role={role}"

        # Step 8: Redirect the user to the frontend with the token
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        # If any step fails, raise a 400 error
        raise HTTPException(status_code=400, detail=f"Google OAuth2 Authentication Failed: {str(e)}")


# ---------------------------- Route: Get Current Authenticated User ----------------------------

@router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Returns the authenticated user's information based on the JWT token.
    Also attempts to refresh the user's Google access token if expired.
    """
    try:
        # Step 1: Decode the JWT token
        payload = verify_jwt_token(token)

        # Step 2: Try using the user_id directly from the token (new logic)
        user_id = payload.get("id")  # Newly included in JWT
        email = payload.get("sub")   # fallback for older tokens

        user = None
        if user_id:
            # Step 2.1: Look up the user using ID if available
            user = db.query(User).filter(User.id == user_id).first()

        if not user and email:
            # Step 2.2: Fallback to email lookup (older tokens)
            user = db.query(User).filter(User.email == email).first()

        if user:
            # Step 3: Try to refresh token if possible
            try:
                await get_valid_google_access_token(user.id, db)
            except Exception as e:
                print(f"Google token refresh failed: {e}")

            # Step 4: Return user info
            return {
                "email": user.email,
                "name": user.name,
                "role": user.role
            }

        # Step 5: If not a User, try Admin by email
        if email:
            admin = db.query(Admin).filter(Admin.email == email).first()
            if admin:
                return {
                    "email": admin.email,
                    "name": admin.name,
                    "role": "admin"
                }

        # Step 6: User not found
        raise HTTPException(status_code=404, detail="User not found")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Logout ----------------------------

@router.post("/logout")
async def logout():
    """
    Logs out the user. Since JWT is stateless, this only tells frontend to delete token.
    """
    return JSONResponse(content={
        "message": "Successfully logged out. Please delete the token from your client(frontend)."
    })
