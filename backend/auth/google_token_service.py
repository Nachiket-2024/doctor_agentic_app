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

# Import the GoogleIntegration model to access stored token information
from ..models.google_integration_model import GoogleIntegration  


# ------------------------------------- Token Refresh Logic -------------------------------------

async def get_valid_google_access_token(user_id: int, db):
    """
    Get a valid Google access token (and refresh token) for the given user.
    If expired or about to expire, refresh it using the refresh token.
    """

    # Log the user ID being checked
    print("Checking GoogleIntegration for user_id:", user_id)

    # Query the integration record for the user
    integration = db.query(GoogleIntegration).filter(GoogleIntegration.user_id == user_id).first()

    # If no integration record is found, raise an error
    if not integration:
        print("No integration found for user.")
        raise HTTPException(status_code=404, detail="Google tokens not found for user.")

    # Debug print: integration object found
    print("Found integration:", integration)

    # Convert token expiry string to datetime, if it exists
    token_expiry = datetime.fromisoformat(integration.token_expiry) if integration.token_expiry else None

    # If token is missing or will expire in next 2 minutes, refresh it
    if not token_expiry or token_expiry <= datetime.now(timezone.utc) + timedelta(minutes=2):
        # Use the refresh token to get new access token
        new_token_data = await refresh_google_access_token(integration.refresh_token)

        # If response lacks access token, raise an error
        if not new_token_data.get("access_token"):
            raise HTTPException(status_code=400, detail="Failed to refresh Google access token.")

        # Update the access token and new expiry time
        integration.access_token = new_token_data["access_token"]
        integration.token_expiry = (
            datetime.now(timezone.utc) + timedelta(seconds=new_token_data["expires_in"])
        ).isoformat()

        # If refresh token was rotated, update it too
        if "refresh_token" in new_token_data:
            integration.refresh_token = new_token_data["refresh_token"]

        # Commit the updated tokens to the database
        db.commit()

    # Return both tokens for use with Google API client (refresh token needed for auto-renewal)
    return integration.access_token, integration.refresh_token


# ------------------------------------- Refresh Token Logic -------------------------------------

async def refresh_google_access_token(refresh_token: str):
    """
    Exchange a refresh token for a new access token using Google's OAuth2 token endpoint.
    """

    # Google's token endpoint
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

    # Send request to Google's token endpoint using HTTPX
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=payload)

    # If request fails, raise an error
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to refresh token from Google.")

    # Return the JSON response with new tokens
    return response.json()
