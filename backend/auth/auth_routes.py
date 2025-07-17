# FastAPI tools to define routes (`APIRouter`), access incoming requests (`Request`),
# raise structured HTTP errors (`HTTPException`), and use dependency injection (`Depends`)
from fastapi import APIRouter, Request, HTTPException, Depends

# Used to send 302 redirect responses — useful for Google login and frontend redirection
from fastapi.responses import RedirectResponse

# A tool to extract a Bearer token from the Authorization header.
# Not used here directly (we use cookies), but defined for future compatibility.
from fastapi.security import OAuth2PasswordBearer

# Provides ORM access to the database, allowing you to query and persist objects
from sqlalchemy.orm import Session

# `jwt.decode()` decodes JWTs with a given secret and algorithm.
# `JWTError` is raised when the token is invalid, malformed, or expired.
from jose import jwt, JWTError

# Used to send HTTP requests to Google's OAuth2 endpoints (for token exchange, userinfo, etc.)
import requests

# Helper to encode query parameters into a safe URL string (e.g., for Google's login URL)
from urllib.parse import urlencode

# `cast` tells the type checker what type we're expecting (helps with IDEs, type safety).
# `Annotated` allows attaching metadata (like `Depends` or `Cookie`) to type hints.
from typing import cast, Annotated

# Used to declare generator-type dependencies, such as for yielding DB sessions
from collections.abc import Generator

# JSONResponse is used to return structured JSON output (e.g., in `/refresh` or `/logout`)
from fastapi.responses import JSONResponse

# Generic Response object — can be used to return redirects, plain responses, etc.
from fastapi import Response

# Allows reading cookies from HTTP requests (e.g., `access_token` or `refresh_token`)
from fastapi import Cookie

# Secret keys and Google OAuth credentials pulled from secure config
from .auth_config import (
    JWT_SECRET,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    DOCTOR_EMAILS,
)

# Access token expiry time (minutes) and algorithm used to sign JWTs (e.g., HS256)
from .settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM

# Function to create a new SQLAlchemy session bound to the current DB
from ..db.session import SessionLocal

# ORM models representing a doctor and patient row in the database
from ..models.doctor_model import Doctor
from ..models.patient_model import Patient

# Schema to return both tokens in a structured format (used in OpenAPI docs)
from .token_schema import Token

# Pydantic models to validate responses from Google's token and userinfo APIs
from .auth_schema import GoogleTokenResponse, GoogleUserInfo

# Internal utility functions for generating and decoding JWTs
from .jwt_handler import create_access_token, create_refresh_token, decode_token

# How long refresh tokens remain valid (in days)
from .settings import REFRESH_TOKEN_EXPIRE_DAYS

# Import the logger from your logging configuration
from ..logging_utils.logging_config import get_logger

# Create a router to group all /auth endpoints together
router = APIRouter(tags=["Auth"])

# Initialize logger for this module
logger = get_logger("auth_routes")

# Optional: defines how to extract bearer tokens from headers (not used in this file)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session to routes that require DB access.
    Uses a generator pattern to ensure the session is closed after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def assign_role_based_on_email(email: str) -> str:
    """
    Assigns a role based on the user's email:
    - "doctor" for emails in DOCTOR_EMAILS
    - "patient" by default for all others
    """
    if email in DOCTOR_EMAILS:
        return "doctor"
    else:
        return "patient"


@router.get("/auth/login")
def login() -> RedirectResponse:
    """
    Begins the OAuth2 flow by redirecting the user to Google's login page.
    Requests user's email, profile info, and access to Calendar and Gmail.
    """
    logger.info("Redirecting user to Google login page")

    query_params: dict[str, str] = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",        # Google will return an authorization code
        "scope": "openid email profile "  # We want identity, email, and profile
                  "https://www.googleapis.com/auth/calendar "
                  "https://www.googleapis.com/auth/gmail.readonly "
                  "https://www.googleapis.com/auth/gmail.send",  # Add Gmail and Calendar scopes
        "access_type": "offline",       # Needed to receive a refresh token
        "prompt": "consent",            # Always ask the user for permission
    }

    # Encode the params into a full Google login URL
    auth_url: str = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(query_params)}"

    # Redirect the user to Google
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
    code: str | None = request.query_params.get("code")
    if not code:
        logger.warning("Missing authorization code in callback")
        raise HTTPException(status_code=400, detail="Missing authorization code")

    # Exchange code for tokens from Google
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    token_response = requests.post("https://oauth2.googleapis.com/token", data=token_data)
    if not token_response.ok:
        logger.error("Failed to fetch token from Google")
        raise HTTPException(status_code=400, detail="Failed to fetch token")

    token_json = cast(GoogleTokenResponse, token_response.json())

    # Use access token to get user info
    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {token_json['access_token']}"},
    )
    if not userinfo_response.ok:
        logger.error("Failed to fetch user info from Google")
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    user_info = cast(GoogleUserInfo, userinfo_response.json())
    email = user_info.get("email")
    if not email:
        logger.error("Email not found in Google response")
        raise HTTPException(status_code=400, detail="Email not found in Google response")

    google_id = user_info.get("id")
    if not google_id:
        logger.error("Google ID not found in Google response")
        raise HTTPException(status_code=400, detail="Google ID not found in Google response")

    name = user_info.get("name", "")

    # Check if doctor or patient already exists
    doctor = db.query(Doctor).filter(Doctor.email == email).first()
    patient = db.query(Patient).filter(Patient.email == email).first()

    if not doctor and not patient:
        role = assign_role_based_on_email(email)
        if role == "doctor":
            doctor = Doctor(google_id=google_id, email=email, name=name)
            db.add(doctor)
            db.commit()
            db.refresh(doctor)
            logger.info(f"New doctor created: {name}, {email}")
        else:
            patient = Patient(google_id=google_id, email=email, name=name)
            db.add(patient)
            db.commit()
            db.refresh(patient)
            logger.info(f"New patient created: {name}, {email}")
    else:
        logger.info(f"User {name} already exists")

    # Create access and refresh tokens
    user_id = doctor.id if doctor else patient.id
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token({"sub": str(user_id)})

    # Redirect to frontend after login
    response = RedirectResponse(url="http://localhost:5173/dashboard", status_code=302)

    # Set secure HttpOnly access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    # Set secure HttpOnly refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    logger.info(f"User {name} logged in successfully")
    return response


def get_current_user_from_cookie(
    db: Annotated[Session, Depends(get_db)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> Doctor | Patient:
    """
    Dependency that extracts the current logged-in doctor or patient from the `access_token` cookie.
    - Verifies and decodes the token.
    - Extracts user ID (`sub`) and looks up the doctor or patient in the database.
    - Raises 401 Unauthorized if anything is invalid.
    """
    if access_token is None:
        logger.warning("Access token missing")
        raise HTTPException(status_code=401, detail="Access token missing")

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

        user_id = int(sub)  # Convert to integer for DB lookup

    except (JWTError, ValueError):
        logger.error("Invalid or expired token")
        raise credentials_exc

    # Query the doctor or patient from DB
    doctor = db.query(Doctor).filter(Doctor.id == user_id).first()
    patient = db.query(Patient).filter(Patient.id == user_id).first()

    if not doctor and not patient:
        logger.error(f"User not found: {user_id}")
        raise credentials_exc

    logger.info(f"User {user_id} authenticated successfully")
    return doctor if doctor else patient


@router.get("/auth/me")
def get_me(current_user: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)]) -> dict[str, str | int | None]:
    """
    Returns the authenticated user's public profile (id, email, name).
    Uses the access token cookie to identify the user.
    """
    logger.info(f"Returning profile for user {current_user.id} ({current_user.email})")
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
        logger.warning("Refresh token missing")
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        # Decode and validate the token
        payload = decode_token(refresh_token)

        # Ensure it's a refresh token
        if payload.get("type") != "refresh":
            logger.error("Invalid token type")
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            logger.error(f"Invalid user ID in token: {user_id}")
            raise HTTPException(status_code=401, detail="Invalid user ID in token")

    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
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

    logger.info(f"Access token refreshed for user {user_id}")
    return response


@router.post("/auth/logout")
def logout(_: Annotated[Doctor | Patient, Depends(get_current_user_from_cookie)]) -> JSONResponse:
    """
    Logs the user out by deleting both the access_token and refresh_token cookies.
    Requires the user to be currently logged in.
    """
    logger.info(f"Logging out user {_}")

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

    logger.info(f"User {_} logged out successfully")
    return response
