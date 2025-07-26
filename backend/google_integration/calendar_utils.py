# ---------------------------- External Imports ----------------------------

# For accessing environment variables
import os

# For loading variables from a .env file
from dotenv import load_dotenv

# To create credentials with refresh support
from google.oauth2.credentials import Credentials

# For building Google API service clients
from googleapiclient.discovery import build

# For database session type hinting
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Function to get a valid (possibly refreshed) Google access token for a user
from ..auth.google_token_service import get_valid_google_access_token

# ---------------------------- Load environment variables ----------------------------

# Load all environment variables from the .env file
load_dotenv()

# ---------------------------- Google OAuth Environment Configuration ----------------------------

# Google OAuth Client ID from .env
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# Google OAuth Client Secret from .env
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Redirect URI registered in Google Cloud
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Scopes required by your app (calendar, gmail, etc.)
GOOGLE_SCOPES = os.getenv("GOOGLE_SCOPES", "").split(", ")

# ---------------------------- Google Credentials Generator ----------------------------

def get_google_credentials(access_token: str, refresh_token: str):
    """
    Builds a Google credentials object using access and refresh tokens.
    This allows for automatic token refresh when using Google API clients.
    """
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=GOOGLE_SCOPES
    )
    return creds

# ---------------------------- Google Calendar Service Generator ----------------------------

def get_calendar_service(access_token: str, refresh_token: str):
    """
    Creates and returns an authenticated Google Calendar API service object.
    """
    # Generate credentials object
    creds = get_google_credentials(access_token, refresh_token)

    # Build the service client for Calendar API
    service = build("calendar", "v3", credentials=creds)

    return service

# ---------------------------- Create Calendar Event ----------------------------

async def create_event(user_id: int, db: Session, summary: str, start_time: str, end_time: str, email: str):
    """
    Creates a calendar event in the user's Google Calendar.
    Uses the user's stored access/refresh tokens, refreshed if needed.
    """
    # Get valid access and refresh tokens for the user
    access_token, refresh_token = await get_valid_google_access_token(user_id, "patient", db)

    # Initialize Google Calendar service
    service = get_calendar_service(access_token, refresh_token)

    # Define the event structure to be created
    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time,
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Asia/Kolkata"
        },
        "attendees": [{"email": email}]
    }

    # Insert the event into the user's primary calendar
    created_event = service.events().insert(calendarId="primary", body=event).execute()

    # Return event details
    return created_event

# ---------------------------- Update Calendar Event ----------------------------

async def update_event(user_id: int, db: Session, event_id: str, summary: str, start_time: str, end_time: str, email: str):
    """
    Updates an existing calendar event using the event ID.
    Retrieves and refreshes tokens as needed for authentication.
    """
    # Get valid access and refresh tokens for the user
    access_token, refresh_token = await get_valid_google_access_token(user_id, "patient", db)

    # Initialize Calendar API client
    service = get_calendar_service(access_token, refresh_token)

    # Define the updated event data
    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time,
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Asia/Kolkata"
        },
        "attendees": [{"email": email}]
    }

    # Update the specified event using its ID
    updated_event = service.events().update(
        calendarId="primary",
        eventId=event_id,
        body=event
    ).execute()

    # Return updated event metadata
    return updated_event

# ---------------------------- Delete Calendar Event ----------------------------

async def delete_event(user_id: int, db: Session, event_id: str):
    """
    Deletes a calendar event from the user's Google Calendar using the event ID.
    Automatically handles token refresh as needed.
    """
    # Get valid access and refresh tokens for the user
    access_token, refresh_token = await get_valid_google_access_token(user_id, "patient", db)

    # Create Calendar API client
    service = get_calendar_service(access_token, refresh_token)

    # Delete the specified event
    service.events().delete(calendarId="primary", eventId=event_id).execute()

    # Return confirmation message
    return {"message": "Event deleted successfully"}
