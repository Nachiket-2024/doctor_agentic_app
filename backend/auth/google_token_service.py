# ------------------------------------- External Imports -------------------------------------

# To make asynchronous HTTP requests to Google APIs  
import httpx  

# For working with datetime objects and time comparisons (with timezone support)  
from datetime import datetime, timedelta, timezone  

# For handling HTTP exceptions in FastAPI  
from fastapi import HTTPException  

# For accessing environment variables like GOOGLE_CLIENT_ID and SECRET  
import os  

# To load .env file variables into the OS environment  
from dotenv import load_dotenv  


# ------------------------------------- Load Environment Variables -------------------------------------

# Load variables from .env into os.environ  
load_dotenv()


# ------------------------------------- Internal Imports -------------------------------------

# Import models to access token data directly from respective tables  
from ..models.admin_model import Admin  
from ..models.doctor_model import Doctor  
from ..models.patient_model import Patient  


# ------------------------------------- Token Refresh Logic -------------------------------------

async def get_valid_google_access_token(user_id: int, role: str, db):
    """
    Get a valid Google access token (and refresh token) for the given user by role.
    If expired or about to expire, refresh it using the refresh token.
    """

    # Log the user ID and role being checked  
    print(f"Checking Google tokens for user_id={user_id} with role={role}")

    # Determine the user object based on role  
    if role == "admin":
        user = db.query(Admin).filter(Admin.id == user_id).first()
    elif role == "doctor":
        user = db.query(Doctor).filter(Doctor.id == user_id).first()
    elif role == "patient":
        user = db.query(Patient).filter(Patient.id == user_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid user role.")

    # If user record not found  
    if not user:
        print("No user found for provided ID and role.")
        raise HTTPException(status_code=404, detail="User not found.")

    # Extract token expiry field  
    token_expiry = user.token_expiry

    # If token is missing or will expire in next 2 minutes, refresh it  
    if not token_expiry or token_expiry <= datetime.now(timezone.utc) + timedelta(minutes=2):
        # Use the refresh token to get a new access token  
        new_token_data = await refresh_google_access_token(user.refresh_token)

        # If response lacks access token, raise an error  
        if not new_token_data.get("access_token"):
            raise HTTPException(status_code=400, detail="Failed to refresh Google access token.")

        # Update access token and token expiry  
        user.access_token = new_token_data["access_token"]
        user.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=new_token_data["expires_in"])

        # If refresh token was rotated, update it too  
        if "refresh_token" in new_token_data:
            user.refresh_token = new_token_data["refresh_token"]

        # Save changes to DB  
        db.commit()

    # Return access and refresh tokens for further use  
    return user.access_token, user.refresh_token


# ------------------------------------- Refresh Token Logic -------------------------------------

async def refresh_google_access_token(refresh_token: str):
    """
    Exchange a refresh token for a new access token using Google's OAuth2 token endpoint.
    """

    # Define Google's token endpoint URL  
    token_url = "https://oauth2.googleapis.com/token"

    # Read client ID and client secret from environment  
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    # Prepare request payload for the refresh request  
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    # Make asynchronous POST request to Google's token endpoint  
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=payload)

    # If request fails, raise error with status and reason  
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to refresh token from Google.")

    # Return parsed JSON token response  
    return response.json()
