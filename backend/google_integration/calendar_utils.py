# ---------------------------- External Imports ----------------------------

# For accessing environment variables
import os

# For loading variables from a .env file
from dotenv import load_dotenv

# To create credentials with refresh support
from google.oauth2.credentials import Credentials

# For building Google API service clients
from googleapiclient.discovery import build


# ---------------------------- Load environment variables ----------------------------

# Load all environment variables from the .env file
load_dotenv()


# ---------------------------- Google OAuth environment config ----------------------------

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")  # Google OAuth Client ID
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")  # Google OAuth Client Secret
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")  # Redirect URI registered in Google Cloud
GOOGLE_SCOPES = os.getenv("GOOGLE_SCOPES", "").split(", ")  # Scopes needed for API access


# ---------------------------- Google Credentials Generator ----------------------------

def get_google_credentials(access_token: str, refresh_token: str):
    """
    Builds a full credentials object using access and refresh tokens along with client secrets.
    This allows both Gmail and Calendar APIs to refresh tokens as needed.
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


# ---------------------------- Google Calendar service generator ----------------------------

def get_calendar_service(access_token: str, refresh_token: str):
    """
    Returns an authenticated Google Calendar service object using proper credentials.
    """
    creds = get_google_credentials(access_token, refresh_token)  # Get valid credentials
    service = build("calendar", "v3", credentials=creds)  # Build Calendar API service
    return service


# ---------------------------- Create calendar event ----------------------------

def create_event(access_token: str, refresh_token: str, summary: str, start_time: str, end_time: str, email: str):
    """
    Creates a Google Calendar event with the given info using user's credentials.
    """
    service = get_calendar_service(access_token, refresh_token)  # Get Calendar API client

    # Define event structure
    event = {
        "summary": summary,  # Event title
        "start": {
            "dateTime": start_time,  # ISO 8601 format
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Asia/Kolkata"
        },
        "attendees": [{"email": email}]  # Notify this email
    }

    # Create the event in primary calendar
    created_event = service.events().insert(calendarId="primary", body=event).execute()
    return created_event  # Return event metadata


# ---------------------------- Update calendar event ----------------------------

def update_event(access_token: str, refresh_token: str, event_id: str, summary: str, start_time: str, end_time: str, email: str):
    """
    Updates an existing event in Google Calendar using event ID and new details.
    """
    service = get_calendar_service(access_token, refresh_token)  # Get Calendar API client

    # Event structure with updated info
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

    # Update the specified event
    updated_event = service.events().update(
        calendarId="primary",
        eventId=event_id,
        body=event
    ).execute()

    return updated_event  # Return updated event metadata


# ---------------------------- Delete calendar event ----------------------------

def delete_event(access_token: str, refresh_token: str, event_id: str):
    """
    Deletes a Google Calendar event using the event ID.
    """
    service = get_calendar_service(access_token, refresh_token)  # Get Calendar API client

    # Delete the event
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return {"message": "Event deleted successfully"}  # Confirm deletion
