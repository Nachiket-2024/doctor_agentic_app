# Import required modules
import os  # Used for accessing environment variables and file paths
from dotenv import load_dotenv  # Loads variables from a .env file into environment
from google.oauth2.credentials import Credentials  # Manages user credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # Handles OAuth 2.0 flow for installed apps
from googleapiclient.discovery import build  # Builds the Google API service
from google.auth.transport.requests import Request  # Used to refresh expired credentials

# Load environment variables from .env file in the root directory
load_dotenv()

# Fetch Google OAuth credentials and settings from environment variables
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")  # Your app's Google Client ID
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")  # Your app's Client Secret
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")  # Redirect URI configured in Google Cloud Console
SCOPES = os.getenv("GOOGLE_SCOPES").split(", ")  # List of OAuth scopes required (comma-separated in .env)
TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")  # Path to the token file for storing credentials

def get_calendar_service():
    """
    Authenticates the user and returns a Google Calendar service object.
    """
    creds = None  # Initialize credentials to None
    
    # Check if token file exists (stores access and refresh tokens)
    if os.path.exists(TOKEN_FILE):
        # Load credentials from the token file
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials exist, refresh or obtain new credentials via OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired credentials using the refresh token
            creds.refresh(Request())
        else:
            # Initiate OAuth flow using client config from .env variables
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": CLIENT_ID,
                        "client_secret": CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "redirect_uris": [REDIRECT_URI]
                    }
                },
                SCOPES  # Scopes for permissions
            )
            # Open local browser to authorize the app and get credentials
            creds = flow.run_local_server(port=0)
        
        # Save the obtained credentials to token.json for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    # Build and return the Google Calendar service object
    service = build('calendar', 'v3', credentials=creds)
    return service

def create_event(summary, start_time, end_time, email):
    """
    Creates a Google Calendar event for a given time period and attendee email.
    """
    service = get_calendar_service()  # Get an authenticated calendar service instance
    
    # Define the event structure for Google Calendar API
    event = {
        'summary': summary,  # Event title (e.g., "Appointment with John")
        'start': {
            'dateTime': start_time,  # ISO 8601 format datetime string for event start
            'timeZone': 'Asia/Kolkata'  # Set the time zone to IST
        },
        'end': {
            'dateTime': end_time,  # ISO 8601 format datetime string for event end
            'timeZone': 'Asia/Kolkata'
        },
        'attendees': [{'email': email}],  # Email address of attendee (doctor or patient)
    }
    
    # Insert the event into the user's primary calendar and return the result
    event_result = service.events().insert(calendarId='primary', body=event).execute()
    return event_result

def update_event(appointment_id, summary, start_time, end_time, email):
    """
    Updates an existing Google Calendar event with new details.
    """
    service = get_calendar_service()  # Get an authenticated calendar service instance

    # Define the updated event fields
    event = {
        'summary': summary,  # Updated title of the event
        'start': {
            'dateTime': start_time,  # Updated start datetime
            'timeZone': 'Asia/Kolkata'
        },
        'end': {
            'dateTime': end_time,  # Updated end datetime
            'timeZone': 'Asia/Kolkata'
        },
        'attendees': [{'email': email}],  # Updated attendee email
    }

    # Use the appointment ID as a placeholder for the event ID (this assumes event ID = "appointment-{id}")
    event_id = f"appointment-{appointment_id}"  # Replace with actual Google event ID in production

    # Call Google Calendar API to update the existing event
    event_result = service.events().update(
        calendarId='primary',
        eventId=event_id,
        body=event
    ).execute()
    
    return event_result

def delete_event(appointment_id):
    """
    Deletes a Google Calendar event using its appointment ID.
    """
    service = get_calendar_service()  # Get an authenticated calendar service instance

    # Construct the event ID from the appointment ID (used in creation or DB mapping)
    event_id = f"appointment-{appointment_id}"  # Replace with real event ID if different

    # Call the API to delete the event from the primary calendar
    service.events().delete(
        calendarId='primary',
        eventId=event_id
    ).execute()
    
    # Return confirmation of successful deletion
    return {"message": "Event deleted successfully"}
