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

# Admin model from the database  
from ..models.admin_model import Admin  

# Doctor model from the database  
from ..models.doctor_model import Doctor  

# Patient model from the database  
from ..models.patient_model import Patient  

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
        scopes = os.getenv("GOOGLE_SCOPES", "")  

        # Replace commas with '%20' to conform to URL formatting  
        formatted_scopes = scopes.replace(",", "%20")  

        # Construct the complete authorization URL  
        auth_url = (
            f"{google_oauth_url}?response_type=code"
            f"&client_id={os.getenv('GOOGLE_CLIENT_ID')}"
            f"&redirect_uri={os.getenv('GOOGLE_REDIRECT_URI')}"
            f"&scope={formatted_scopes}"
            f"&access_type=offline"
            f"&include_granted_scopes=true"
            f"&prompt=consent"
        )

        # Redirect user to Google login  
        return RedirectResponse(url=auth_url)

    except Exception as e:
        # Raise error if OAuth setup fails  
        raise HTTPException(status_code=400, detail=f"Google OAuth2 Authentication Failed: {str(e)}")


# ---------------------------- Route: OAuth2 Callback ----------------------------

@router.get("/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    try:
        # Step 1: Use helper to do full auth and DB setup
        user_info = authenticate_with_google(code, db)

        # Step 2: Generate JWT from returned user_info
        jwt_token = create_jwt_token(user_info)

        # Step 3: Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_REDIRECT_URI")
        redirect_url = f"{frontend_url}?access_token={jwt_token}"

        return RedirectResponse(url=redirect_url)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google OAuth2 Authentication Failed: {str(e)}")


# ---------------------------- Route: Get Current Authenticated User ----------------------------

@router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Returns the authenticated user's information based on the JWT token.
    Tries Admin → Doctor → Patient. Refreshes token for Doctor/Patient.
    """
    try:
        # Step 1: Verify JWT token  
        payload = verify_jwt_token(token)

        # Step 2: Extract user info from token  
        user_id = payload.get("id")
        email = payload.get("sub")
        name = payload.get("name")

        # Step 3: Try Admin  
        if email:
            admin = db.query(Admin).filter(Admin.email == email).first()
        if admin:
            try:
                await get_valid_google_access_token(admin.id, "admin", db)
            except Exception as e:
                print(f"Token refresh failed: {e}")
            return {
                "email": admin.email,
                "name": admin.name,
                "role": "admin"
            }

        # Step 4: Try Doctor  
        doctor = db.query(Doctor).filter(Doctor.id == user_id).first() if user_id else None
        if not doctor and email:
            doctor = db.query(Doctor).filter(Doctor.email == email).first()
        if doctor:
            try:
                await get_valid_google_access_token(doctor.id, "doctor", db)
            except Exception as e:
                print(f"Token refresh failed: {e}")
            return {
                "email": doctor.email,
                "name": doctor.name,
                "role": "doctor"
            }

        # Step 5: Try Patient  
        patient = db.query(Patient).filter(Patient.id == user_id).first() if user_id else None
        if not patient and email:
            patient = db.query(Patient).filter(Patient.email == email).first()
        if patient:
            try:
                await get_valid_google_access_token(patient.id, "patient", db)
            except Exception as e:
                print(f"Token refresh failed: {e}")
            return {
                "email": patient.email,
                "name": patient.name,
                "role": "patient"
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
        "message": "Successfully logged out. Please delete the token from your client (frontend)."
    })
