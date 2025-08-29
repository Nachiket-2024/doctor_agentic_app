# ---------------------------- External Imports ----------------------------
# FastAPI tools for routing, dependencies, and HTTP errors
from fastapi import APIRouter, Depends, HTTPException, Request

# Response classes for JSON output and redirection
from fastapi.responses import JSONResponse, RedirectResponse

# SQLAlchemy session for interacting with the database
from sqlalchemy.orm import Session

# To handle JWT decoding and verification errors
from jose import JWTError

# To extract Bearer token from Authorization header
from fastapi.security import OAuth2PasswordBearer

# ---------------------------- Internal Imports ----------------------------
# Internal utility functions for Google auth and JWT
from .auth_utils import AuthUtils

# Application-wide settings from environment
from ..core.settings import settings

# Admin model from the database
from ..models.admin_model import Admin

# Doctor model from the database
from ..models.doctor_model import Doctor

# Patient model from the database
from ..models.patient_model import Patient

# Dependency for getting DB session
from ..db.database_session_manager import DatabaseSessionManager

# For checking and generating access token
from .google_token_service import GoogleTokenService

# ---------------------------- Router & OAuth Setup ----------------------------
# Set up FastAPI's OAuth2PasswordBearer to extract token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a FastAPI router instance with prefix and tags
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# ------------------------ Route: Google Login Initiation ------------------------
@router.get("/login")
async def login_with_google(request: Request, db: Session = Depends(DatabaseSessionManager().get_db)):
    """
    Initiates the Google OAuth2 login flow and redirects the user to the Google login page.
    """
    try:
        google_oauth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        scopes = settings.GOOGLE_SCOPES
        formatted_scopes = scopes.replace(",", "%20")
        auth_url = (
            f"{google_oauth_url}?response_type=code"
            f"&client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
            f"&scope={formatted_scopes}"
            f"&access_type=offline"
            f"&include_granted_scopes=true"
            f"&prompt=consent"
        )
        return RedirectResponse(url=auth_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google OAuth2 Authentication Failed: {str(e)}")

# ------------------------ Route: OAuth2 Callback ------------------------
@router.get("/callback")
async def google_callback(code: str, db: Session = Depends(DatabaseSessionManager().get_db)):
    """
    Handles the OAuth2 callback, authenticates the user, and redirects with JWT.
    """
    try:
        user_info = AuthUtils.authenticate_with_google(code, db)
        jwt_token = AuthUtils.create_jwt_token(user_info)
        redirect_url = f"{settings.FRONTEND_REDIRECT_URI}?access_token={jwt_token}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google OAuth2 Authentication Failed: {str(e)}")

# ------------------------ Route: Get Current Authenticated User ------------------------
@router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(DatabaseSessionManager().get_db)):
    """
    Returns the authenticated user's information based on the JWT token.
    Tries Admin → Doctor → Patient. Refreshes token for Doctor/Patient.
    """
    try:
        payload = AuthUtils.verify_jwt_token(token)
        user_id = payload.get("id")
        email = payload.get("sub")
        name = payload.get("name")

        admin = db.query(Admin).filter(Admin.email == email).first() if email else None
        if admin:
            try:
                await GoogleTokenService.get_valid_google_access_token(admin.id, "admin", db)
            except Exception as e:
                print(f"Token refresh failed: {e}")
            return {"email": admin.email, "name": admin.name, "role": "admin"}

        doctor = db.query(Doctor).filter(Doctor.id == user_id).first() if user_id else None
        if not doctor and email:
            doctor = db.query(Doctor).filter(Doctor.email == email).first()
        if doctor:
            try:
                await GoogleTokenService.get_valid_google_access_token(doctor.id, "doctor", db)
            except Exception as e:
                print(f"Token refresh failed: {e}")
            return {"email": doctor.email, "name": doctor.name, "role": "doctor"}

        patient = db.query(Patient).filter(Patient.id == user_id).first() if user_id else None
        if not patient and email:
            patient = db.query(Patient).filter(Patient.email == email).first()
        if patient:
            try:
                await GoogleTokenService.get_valid_google_access_token(patient.id, "patient", db)
            except Exception as e:
                print(f"Token refresh failed: {e}")
            return {"email": patient.email, "name": patient.name, "role": "patient"}

        raise HTTPException(status_code=404, detail="User not found")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------ Route: Logout ------------------------
@router.post("/logout")
async def logout():
    """
    Logs out the user. Since JWT is stateless, this only tells frontend to delete token.
    """
    return JSONResponse(content={
        "message": "Successfully logged out. Please delete the token from your client (frontend)."
    })
