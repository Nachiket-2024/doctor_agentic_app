# ---------------------------- External Imports ----------------------------
# For working with timestamps and timezones  
from datetime import datetime, timedelta, timezone

# For encoding and decoding JWTs and handling JWT-related exceptions  
from jose import JWTError, jwt

# For database session handling using SQLAlchemy ORM  
from sqlalchemy.orm import Session

# For making HTTP requests (used for communicating with Google OAuth2 endpoints)  
import requests

# For raising HTTP exceptions in FastAPI  
from fastapi import HTTPException

# For printing error tracebacks in case of unexpected exceptions  
import traceback

# ---------------------------- Internal Imports ----------------------------
# Application-wide settings from environment  
from ..core.settings import settings

# Import Admin model for DB queries  
from ..models.admin_model import Admin

# Import Doctor model  
from ..models.doctor_model import Doctor

# Import Patient model  
from ..models.patient_model import Patient

# ---------------------------- AuthUtils Class ----------------------------
class AuthUtils:
    """
    A utility class for JWT operations and Google OAuth2 authentication.
    """

    # ------------------------ Method: Create JWT Token ------------------------
    @staticmethod
    def create_jwt_token(user_info: dict) -> str:
        """
        Creates a JWT token with user's email, role, id, and expiry.

        Parameters:
        - user_info (dict): Dictionary containing email, role, and id.

        Returns:
        - str: Encoded JWT token.
        """
        # Calculate token expiration time  
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Create the payload with user details  
        to_encode = {
            "sub": user_info["email"],
            "role": user_info["role"],
            "exp": expire,
            "id": user_info["id"],
        }

        # Encode the payload using secret and algorithm  
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

        # Return the encoded token  
        return encoded_jwt

    # ------------------------ Method: Verify JWT Token ------------------------
    @staticmethod
    def verify_jwt_token(token: str) -> dict:
        """
        Decodes and verifies the JWT token.

        Parameters:
        - token (str): JWT token to verify.

        Returns:
        - dict: Decoded token payload.
        """
        try:
            # Attempt to decode the JWT token  
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

            # Ensure 'id' is present in the payload  
            if "id" not in payload:
                raise HTTPException(status_code=401, detail="Token does not contain user ID")

            # Return decoded payload  
            return payload

        except JWTError:
            # Raise if token signature or structure is invalid  
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception:
            # Log unexpected decoding issues  
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Token validation error")

    # ------------------------ Method: Determine Role and ID ------------------------
    @staticmethod
    def determine_user_role_and_id(email: str, db: Session) -> tuple[str, int]:
        """
        Determines the user's role and ID based on email. Creates a Patient if not found.

        Parameters:
        - email (str): The user's email address.
        - db (Session): SQLAlchemy database session.

        Returns:
        - tuple[str, int]: Role ('admin' | 'doctor' | 'patient'), and user ID.
        """
        # Try finding the user in Admin table  
        admin = db.query(Admin).filter(Admin.email == email).first()
        if admin:
            return "admin", admin.id

        # Try finding the user in Doctor table  
        doctor = db.query(Doctor).filter(Doctor.email == email).first()
        if doctor:
            return "doctor", doctor.id

        # Try finding the user in Patient table  
        patient = db.query(Patient).filter(Patient.email == email).first()

        # If not found, create a new patient  
        if not patient:
            patient = Patient(
                name=email.split('@')[0],
                email=email
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)

        # Return default role and ID  
        return "patient", patient.id

    # ------------------------ Method: Google OAuth Authentication ------------------------
    @staticmethod
    def authenticate_with_google(code: str, db: Session) -> dict:
        """
        Authenticates the user with Google and stores access/refresh tokens.

        Parameters:
        - code (str): Authorization code from Google.
        - db (Session): SQLAlchemy database session.

        Returns:
        - dict: User info with email, name, role, and ID.
        """
        try:
            # -------- Step 1: Exchange code for access/refresh tokens --------  
            token_data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }

            # Send request to Google's token endpoint  
            response = requests.post("https://oauth2.googleapis.com/token", data=token_data)
            response.raise_for_status()
            token_info = response.json()

            # Check token response for required fields  
            if not all(k in token_info for k in ["access_token", "refresh_token", "expires_in"]):
                raise Exception("Incomplete token response from Google")

            # Extract token details  
            access_token = token_info["access_token"]
            refresh_token = token_info["refresh_token"]
            expires_in = token_info["expires_in"]
            token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

            # -------- Step 2: Fetch user's Google profile info --------  
            user_info_response = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info_response.raise_for_status()
            user_info = user_info_response.json()

            # Extract user name and email  
            user_name = user_info.get("name", "")
            user_email = user_info.get("email", "")

            # -------- Step 3: Determine user role and ID --------  
            role, user_id = AuthUtils.determine_user_role_and_id(user_email, db)

            # -------- Step 4: Save tokens to the appropriate model --------  
            if role == "admin":
                admin = db.query(Admin).filter(Admin.id == user_id).first()
                admin.access_token = access_token
                admin.refresh_token = refresh_token
                admin.token_expiry = token_expiry

            elif role == "doctor":
                doctor = db.query(Doctor).filter(Doctor.id == user_id).first()
                doctor.access_token = access_token
                doctor.refresh_token = refresh_token
                doctor.token_expiry = token_expiry

            elif role == "patient":
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

            # Commit all DB changes  
            db.commit()

            # -------- Step 5: Return user profile --------  
            return {
                "email": user_email,
                "name": user_name,
                "role": role,
                "id": user_id
            }

        except Exception as e:
            # Print full traceback for internal logs  
            traceback.print_exc()
            raise Exception(f"Error during Google authentication: {str(e)}")
