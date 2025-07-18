from fastapi import APIRouter, Request, HTTPException, Depends  # Import FastAPI components for routing and HTTP exceptions
from fastapi.responses import RedirectResponse, JSONResponse  # Import for redirecting and JSON responses
from fastapi.security import OAuth2PasswordBearer  # OAuth2 security dependency
from sqlalchemy.orm import Session  # For database session management
from jose import jwt, JWTError  # For JWT token handling
import requests  # To make external HTTP requests (used for Google OAuth2)
from urllib.parse import urlencode  # For encoding URL parameters
from typing import cast, Annotated  # For type casting and annotations
from collections.abc import Generator  # For generator types
from fastapi import Cookie, Response  # For managing cookies in requests and responses

# Import configuration settings and environment variables
from .auth_config import (
    JWT_SECRET,  # JWT secret key for encoding/decoding tokens
    GOOGLE_CLIENT_ID,  # Google OAuth2 client ID
    GOOGLE_CLIENT_SECRET,  # Google OAuth2 client secret
    GOOGLE_REDIRECT_URI,  # Redirect URI after Google authentication
    ADMIN_EMAILS,  # Admin emails imported from the environment
)
from .settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM  # Token expiration settings and algorithm
from ..db.session import SessionLocal  # Database session provider
from ..models.doctor_model import Doctor  # Import Doctor model for DB interactions
from ..models.patient_model import Patient  # Import Patient model for DB interactions
from .token_schema import Token  # Import token schema for JWT token response
from .auth_schema import GoogleTokenResponse, GoogleUserInfo  # Import schema for Google response handling
from .jwt_handler import create_access_token, create_refresh_token, decode_token  # JWT token handlers
from .settings import REFRESH_TOKEN_EXPIRE_DAYS  # Refresh token expiration settings

# Create a FastAPI router for authentication routes
router = APIRouter(tags=["Auth"])

# OAuth2 password bearer for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session to routes that require DB access.
    Uses a generator pattern to ensure the session is closed after the request finishes.
    """
    db = SessionLocal()  # Create a new database session
    try:
        yield db  # Yield the database session to the route function
    finally:
        db.close()  # Close the session after the request


def assign_role_based_on_email(email: str) -> str:
    """
    Assigns a role based on the user's email:
    - "admin" for emails in ADMIN_EMAILS
    - "doctor" for emails in DOCTOR_EMAILS
    - "patient" by default for all others
    """
    # Check if the email is in the admin list from .env
    if email in ADMIN_EMAILS:
        return "admin"
    elif email.endswith('@doctor.com'):  # Modify this condition as needed
        return "doctor"
    else:
        return "patient"  # Default to patient


@router.get("/auth/login")
def login() -> RedirectResponse:
    """
    Begins the OAuth2 flow by redirecting the user to Google's login page.
    Requests user's email, profile info, and access to Calendar and Gmail.
    """

    # Build the query parameters for Google's OAuth2 login
    query_params: dict[str, str] = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",  # Google will return an authorization code
        "scope": "openid email profile "
                  "https://www.googleapis.com/auth/calendar "
                  "https://www.googleapis.com/auth/gmail.readonly "
                  "https://www.googleapis.com/auth/gmail.send",  # Request Calendar and Gmail access
        "access_type": "offline",  # Needed to receive a refresh token
        "prompt": "consent",  # Always ask the user for permission
    }

    # Encode the query parameters into a URL for Google login
    auth_url: str = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(query_params)}"

    # Redirect the user to the Google login page
    return RedirectResponse(auth_url)


@router.get("/auth/callback", response_model=Token)
def auth_callback(request: Request, db: Annotated[Session, Depends(get_db)]) -> Response:
    """
    Handles Google's redirect after user authentication.
    - Exchanges the authorization `code` for access/refresh tokens from Google.
    - Fetches the user's email/profile info from Google.
    - Checks if doctor or patient exists in the database, creating a new one if not.
    - Sets the access and refresh tokens in secure HttpOnly cookies.
    """
    code: str | None = request.query_params.get("code")  # Extract the authorization code from the query params
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")  # Raise error if code is missing

    # Exchange the authorization code for tokens from Google
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",  # Grant type for code exchange
    }

    # Send a POST request to Google to get the tokens
    token_response = requests.post("https://oauth2.googleapis.com/token", data=token_data)
    if not token_response.ok:
        raise HTTPException(status_code=400, detail="Failed to fetch token")  # Raise error if token exchange fails

    token_json = cast(GoogleTokenResponse, token_response.json())  # Cast the response to expected schema

    # Use the access token to get user information from Google
    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {token_json['access_token']}"},
    )
    if not userinfo_response.ok:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")  # Raise error if fetching user info fails

    user_info = cast(GoogleUserInfo, userinfo_response.json())  # Cast the user info response
    email = user_info.get("email")  # Extract the email from the response
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Google response")

    google_id = user_info.get("id")  # Extract Google ID from the response
    if not google_id:
        raise HTTPException(status_code=400, detail="Google ID not found in Google response")

    name = user_info.get("name", "")  # Get the user's name, defaulting to an empty string

    if email in ADMIN_EMAILS:
        # Admin login - no need to check for doctor or patient, just assign admin role
        user_id = "admin"  # Admin will have 'admin' as the user ID
    else:
        # Check if doctor or patient exists in the database
        doctor = db.query(Doctor).filter(Doctor.email == email).first()  # Search for the doctor in the database
        patient = db.query(Patient).filter(Patient.email == email).first()  # Search for the patient in the database

        if not doctor and not patient:
            role = assign_role_based_on_email(email)  # Assign role based on email
            if role == "doctor":
                # Create a new doctor record if not found
                doctor = Doctor(google_id=google_id, email=email, name=name)
                db.add(doctor)
                db.commit()
                db.refresh(doctor)
                patient = None
            elif role == "patient":
                # Create a new patient record if not found
                patient = Patient(google_id=google_id, email=email, name=name)
                db.add(patient)
                db.commit()
                db.refresh(patient)
                doctor = None

        # Assign user_id based on doctor or patient model
        if doctor:
            user_id = doctor.id
        elif patient:
            user_id = patient.id
        else:
            user_id = None  # This should not happen anymore for admins, because user_id is "admin"

    # Creating JWT tokens for the authenticated user
    if user_id != "admin":
        access_token = create_access_token({"sub": str(user_id)})  # Create access token for the user
        refresh_token = create_refresh_token({"sub": str(user_id)})  # Create refresh token for the user
    else:
        # Handle admin login without creating any user model
        access_token = create_access_token({"sub": "admin"})  # Admin access token
        refresh_token = create_refresh_token({"sub": "admin"})  # Admin refresh token

    # Redirect to frontend after login with the generated tokens in cookies
    response = RedirectResponse(url="http://localhost:5173/dashboard", status_code=302)

    # Set secure HttpOnly access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Expiry in minutes
    )

    # Set secure HttpOnly refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # Expiry in days
    )

    return response  # Return the response to frontend


def get_current_user_from_cookie(
    db: Annotated[Session, Depends(get_db)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> Doctor | Patient | str:
    """
    Dependency that extracts the current logged-in doctor, patient, or admin from the `access_token` cookie.
    - Verifies and decodes the token.
    - Extracts user ID (`sub`) and looks up the doctor or patient in the database.
    - Allows admin access (where user_id is 'admin').
    - Raises 401 Unauthorized if anything is invalid.
    """
    if access_token is None:
        raise HTTPException(status_code=401, detail="Access token missing")  # Raise error if no token provided

    credentials_exc = HTTPException(
        status_code=401,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT using secret and algorithm
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=[ALGORITHM])

        # Extract user ID from the token payload
        sub = payload.get("sub")

        # Ensure the ID is valid
        if not isinstance(sub, str):
            raise credentials_exc

        user_id = sub  # Now it's a string (either 'admin' or user ID)

    except (JWTError, ValueError):
        raise credentials_exc

    # If it's admin, don't look for a doctor or patient
    if user_id == "admin":
        return "admin"

    # Otherwise, query the doctor or patient from DB
    doctor = db.query(Doctor).filter(Doctor.id == user_id).first()
    patient = db.query(Patient).filter(Patient.id == user_id).first()

    if not doctor and not patient:
        raise credentials_exc

    return doctor if doctor else patient  # Return the authenticated user (doctor or patient)


@router.get("/auth/me")
def get_me(current_user: Annotated[Doctor | Patient | str, Depends(get_current_user_from_cookie)]) -> dict[str, str | int | None]:
    """
    Returns the authenticated user's public profile (id, email, name).
    Uses the access token cookie to identify the user.
    """
    if current_user == "admin":
        # Admin does not have a user model, so return a predefined admin profile.
        return {
            "id": "admin",  # Admin doesn't have a specific ID in the DB
            "email": ADMIN_EMAILS[0],  # You can define the admin email here
            "name": "Admin",  # Or whatever name you want to display for the admin
        }

    # For doctor or patient, return their details as usual
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
    }


@router.post("/auth/refresh")
def refresh_token(
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> JSONResponse:
    """
    Refreshes the access token using a valid refresh token stored in the cookie.
    - Validates the refresh token.
    - Issues a new access token and sets it in the cookie.
    """
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        # Decode and validate the token
        payload = decode_token(refresh_token)

        # Ensure it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise HTTPException(status_code=401, detail="Invalid user ID in token")

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # Generate a new access token
    new_access_token = create_access_token({"sub": user_id})

    # Send it in a new cookie
    response = JSONResponse(content={"message": "Token refreshed"})
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return response


@router.post("/auth/logout")
def logout(_: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)]) -> JSONResponse:
    """
    Logs the user out by deleting both the access_token and refresh_token cookies.
    Requires the user to be currently logged in.
    """

    response = JSONResponse(content={"message": "Logged out successfully"})

    # Remove access token cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax",
    )

    # Remove refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return response
