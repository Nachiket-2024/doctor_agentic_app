# ---------------------------- External Imports ----------------------------

# For loading environment variables from a .env file
import os

# For working with timestamps and timezones
from datetime import datetime, timedelta, timezone

# For encoding and decoding JWTs and handling JWT-related exceptions
from jose import JWTError, jwt

# For loading environment variables at runtime
from dotenv import load_dotenv

# For database session handling using SQLAlchemy ORM
from sqlalchemy.orm import Session

# For making HTTP requests (used for communicating with Google OAuth2 endpoints)
import requests

# For raising HTTP exceptions in FastAPI
from fastapi import HTTPException

# For printing error tracebacks in case of unexpected exceptions
import traceback

# ---------------------------- Internal Imports ----------------------------

# Import Admin model for DB queries
from ..models.admin_model import Admin

# Import Doctor model
from ..models.doctor_model import Doctor

# Import Patient model
from ..models.patient_model import Patient

# ---------------------------- Load Environment Variables ----------------------------

# Load variables from .env
load_dotenv()

# Load secret and algorithm for JWT
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

# Google OAuth credentials
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Raise error if any env vars are missing
if not JWT_SECRET or not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not GOOGLE_REDIRECT_URI:
    raise ValueError("Missing required environment variables")

# Optional: token expiry duration
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


# ---------------------------- Create JWT Token ----------------------------

def create_jwt_token(user_info):
    """
    Create a JWT token with user's email, role, id, and expiry.
    """
    # Calculate expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Define the JWT payload
    to_encode = {
        "sub": user_info["email"],
        "role": user_info["role"],
        "exp": expire,
        "id": user_info["id"],
    }

    # Encode the JWT
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# ---------------------------- Verify JWT Token ----------------------------

def verify_jwt_token(token: str):
    """
    Decodes and verifies the JWT token.
    """
    try:
        # Decode the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Ensure the ID exists in payload
        if "id" not in payload:
            raise HTTPException(status_code=401, detail="Token does not contain user ID")

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Token validation error")
    

# ---------------------------- Role Determination Logic ----------------------------

def determine_user_role_and_id(email: str, db: Session) -> tuple[str, int]:
    """
    Determines the role of the user (admin, doctor, patient) based on their email.
    If no match is found, a new patient is created.

    Parameters:
    - email (str): The email address to check.
    - db (Session): The SQLAlchemy database session.

    Returns:
    - tuple[str, int]: A tuple containing the role ('admin' | 'doctor' | 'patient') and user ID.
    """
    # -------- Step 1: Check if the user is an admin --------
    admin = db.query(Admin).filter(Admin.email == email).first()
    if admin:
        return "admin", admin.id

    # -------- Step 2: Check if the user is a doctor --------
    doctor = db.query(Doctor).filter(Doctor.email == email).first()
    if doctor:
        return "doctor", doctor.id

    # -------- Step 3: Check if the user is a patient --------
    patient = db.query(Patient).filter(Patient.email == email).first()
    if not patient:
        patient = Patient(
            name=email.split('@')[0],
            email=email
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

    return "patient", patient.id


# ---------------------------- Google OAuth2 Authentication ----------------------------

def authenticate_with_google(code: str, db: Session):
    """
    Authenticates user with Google and stores tokens in appropriate model table.
    """
    try:
        # -------- Step 1: Exchange code for Google tokens --------
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        # Send token request
        response = requests.post("https://oauth2.googleapis.com/token", data=token_data)
        response.raise_for_status()
        token_info = response.json()

        # Ensure required fields exist
        if not all(k in token_info for k in ["access_token", "refresh_token", "expires_in"]):
            raise Exception("Incomplete token response from Google")

        # Extract tokens and calculate expiry
        access_token = token_info["access_token"]
        refresh_token = token_info["refresh_token"]
        expires_in = token_info["expires_in"]
        token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # -------- Step 2: Fetch user info from Google --------
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info_response.raise_for_status()
        user_info = user_info_response.json()

        # Get name and email from Google
        user_name = user_info.get("name", "")
        user_email = user_info.get("email", "")

        # -------- Step 3: Determine user role and ID --------
        role, user_id = determine_user_role_and_id(user_email, db)

        # -------- Step 4: Save tokens in respective table --------
        if role == "admin":
            # Update Admin tokens
            admin = db.query(Admin).filter(Admin.id == user_id).first()
            admin.access_token = access_token
            admin.refresh_token = refresh_token
            admin.token_expiry = token_expiry

        elif role == "doctor":
            # Update Doctor tokens
            doctor = db.query(Doctor).filter(Doctor.id == user_id).first()
            doctor.access_token = access_token
            doctor.refresh_token = refresh_token
            doctor.token_expiry = token_expiry

        elif role == "patient":
            # Update if patient exists or create a new one
            patient = db.query(Patient).filter(Patient.id == user_id).first()
            if not patient:
                patient = Patient(
                    name=user_name,
                    email=user_email,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_expiry=token_expiry
                )
                db.add(patient)
            else:
                patient.access_token = access_token
                patient.refresh_token = refresh_token
                patient.token_expiry = token_expiry

        # Save changes
        db.commit()

        # -------- Step 5: Return user info --------
        return {
            "email": user_email,
            "name": user_name,
            "role": role,
            "id": user_id
        }

    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error during Google authentication: {str(e)}")
