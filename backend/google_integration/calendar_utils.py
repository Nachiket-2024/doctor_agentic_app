import os
from dotenv import load_dotenv  # To load environment variables from .env
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Load environment variables from .env file
load_dotenv()

# SCOPES define the permissions requested from the user for Google services.
SCOPES = [
    'https://www.googleapis.com/auth/calendar',  # Permission to access the Google Calendar API
    'https://www.googleapis.com/auth/gmail.send'  # Permission to send emails via Gmail API
]

# Fetch Google OAuth credentials from environment variables
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Token file path from the environment variable (this can remain static)
TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")  # Path to store the user's token

def get_calendar_service():
    """
    Authenticates the user and returns a Google Calendar service object.
    """
    creds = None
    # Check if token file exists (stores access/refresh token pair)
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If credentials are invalid or expired, refresh or authenticate the user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh expired credentials using the refresh token
        else:
            # If no credentials exist, run the OAuth flow to get new credentials
            flow = InstalledAppFlow.from_client_config(
                {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uris": [REDIRECT_URI]
                },
                SCOPES
            )
            creds = flow.run_local_server(port=0)  # Starts a local web server for OAuth2 login
    
        # Save the credentials to a token file for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    # Build the Google Calendar service using the credentials
    service = build('calendar', 'v3', credentials=creds)
    return service

def create_event(summary, start_time, end_time, email):
    """
    Creates a Google Calendar event for a given time period and email.
    """
    service = get_calendar_service()  # Get the authenticated Google Calendar service
    
    # Define the event structure
    event = {
        'summary': summary,  # Title of the event (e.g., "Appointment with John")
        'start': {
            'dateTime': start_time,  # Start date and time of the event
            'timeZone': 'Asia/Kolkata'  # Timezone for the event
        },
        'end': {
            'dateTime': end_time,  # End date and time of the event
            'timeZone': 'Asia/Kolkata'  # Timezone for the event
        },
        'attendees': [{'email': email}],  # Attendee email (Doctor or Patient)
    }
    
    # Insert the event into the primary calendar of the user
    event_result = service.events().insert(calendarId='primary', body=event).execute()
    return event_result  # Returns the created event result
