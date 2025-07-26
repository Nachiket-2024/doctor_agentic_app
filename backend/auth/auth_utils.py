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

from fastapi import HTTPException
import traceback

# ---------------------------- Internal Imports ----------------------------

# Importing the User model for DB operations related to non-admin users
from ..models.user_model import User

# Importing the Admin model for DB operations related to admin users
from ..models.admin_model import Admin

# Importing the GoogleIntegration model to store tokens
from ..models.google_integration_model import GoogleIntegration


# ---------------------------- Load Environment Variables ----------------------------

# Load the .env file into environment variables
load_dotenv()

# Fetch JWT secret used for signing tokens
JWT_SECRET = os.getenv("JWT_SECRET")

# Fetch the algorithm used to sign JWTs (e.g., HS256)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

# Fetch the Google OAuth2 client ID
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# Fetch the Google OAuth2 client secret
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Fetch the redirect URI registered with Google
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Raise error if any required environment variable is missing
if not JWT_SECRET or not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not GOOGLE_REDIRECT_URI:
    raise ValueError("Missing required environment variables")

# Fetch token expiration time in minutes (defaults to 60 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


# ---------------------------- Create JWT Token ----------------------------

def create_jwt_token(user_info):
    """
    Create JWT token for the authenticated user.
    """
    # Set token expiration time from now
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Define payload with subject (email), role, and expiry
    to_encode = {
        "sub": user_info["email"],
        "role": user_info["role"],
        "exp": expire,
        "id": user_info["id"],
    }

    # Encode payload using secret and algorithm
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# ---------------------------- Verify JWT Token ----------------------------

def verify_jwt_token(token: str):
    try:
        # Decode JWT token using the secret key and algorithm
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")])

        # Check if 'id' is missing
        if "id" not in payload:
            raise HTTPException(status_code=401, detail="Token does not contain user ID")

        # Return the payload for further use
        return payload

    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        # Print full traceback in terminal
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Token validation error")


# ---------------------------- Google OAuth2 Authentication ----------------------------

def authenticate_with_google(code: str, db: Session):
    """
    Authenticate the user using Google OAuth2.
    Steps:
    - Exchange auth code for access + refresh token
    - Fetch user info from Google
    - Register or find user in DB
    - Save tokens in GoogleIntegration table
    - Return enriched user info
    """
    try:
        # -------- Step 1: Exchange code for tokens --------
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        # Send POST request to Google's token endpoint
        response = requests.post("https://oauth2.googleapis.com/token", data=token_data)
        response.raise_for_status()
        token_info = response.json()

        # Validate required fields in token response
        if not all(k in token_info for k in ["access_token", "refresh_token", "token_type", "expires_in"]):
            raise Exception("Incomplete token response from Google")

        # Extract tokens and expiration
        access_token = token_info["access_token"]
        refresh_token = token_info["refresh_token"]
        expires_in = token_info["expires_in"]

        # Compute expiration timestamp in UTC
        token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # -------- Step 2: Use token to get user info --------
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info_response.raise_for_status()
        user_info = user_info_response.json()

        # Extract user name and email
        user_name = user_info.get("name", "")
        user_email = user_info.get("email", "")
        role = "patient"  # Default role

        # -------- Step 3: Check user/admin in DB --------
        admin = db.query(Admin).filter(Admin.email == user_email).first()
        if admin:
            role = "admin"
            user_id = admin.id
        else:
            user = db.query(User).filter(User.email == user_email).first()
            if not user:
                user = User(name=user_name, email=user_email, role=role)
                db.add(user)
                db.commit()
                db.refresh(user)
            user_id = user.id
            role = user.role

        # -------- Step 4: Store tokens in GoogleIntegration --------
        existing = db.query(GoogleIntegration).filter(GoogleIntegration.user_id == user_id).first()

        if existing:
            # Update existing integration record
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.token_expiry = token_expiry
        else:
            # Create new integration record
            integration = GoogleIntegration(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expiry=token_expiry
            )
            db.add(integration)

        # Persist changes to DB
        db.commit()

        # -------- Step 5: Return user info --------
        return {
            "email": user_email,
            "name": user_name,
            "role": role,
            "id": user_id
        }

    except Exception as e:
        raise Exception(f"Error during Google authentication: {str(e)}")
