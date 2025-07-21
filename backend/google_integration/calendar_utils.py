import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Load environment variables from .env file
load_dotenv()

# Fetch Google OAuth credentials and SCOPES from environment variables
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SCOPES = os.getenv("GOOGLE_SCOPES").split(", ")
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

def update_event(appointment_id, summary, start_time, end_time, email):
    """
    Updates an existing Google Calendar event.
    """
    service = get_calendar_service()  # Get the authenticated Google Calendar service
    
    # Define the event structure for the update
    event = {
        'summary': summary,  # Updated title of the event (e.g., "Updated Appointment with John")
        'start': {
            'dateTime': start_time,  # Updated start date and time
            'timeZone': 'Asia/Kolkata'  # Timezone for the event
        },
        'end': {
            'dateTime': end_time,  # Updated end date and time
            'timeZone': 'Asia/Kolkata'  # Timezone for the event
        },
        'attendees': [{'email': email}],  # Attendee email (Doctor or Patient)
    }

    # Fetch the event using its appointment ID (if you store the event ID in the database)
    event_id = f"appointment-{appointment_id}"  # This could be the actual ID of the event in your DB or system

    # Update the existing event using the Google Calendar API
    event_result = service.events().update(
        calendarId='primary',
        eventId=event_id,
        body=event
    ).execute()
    
    return event_result  # Returns the updated event result

def delete_event(appointment_id):
    """
    Deletes a Google Calendar event.
    """
    service = get_calendar_service()  # Get the authenticated Google Calendar service
    
    # Fetch the event using its appointment ID (if you store the event ID in the database)
    event_id = f"appointment-{appointment_id}"  # This could be the actual ID of the event in your DB or system

    # Delete the event from the Google Calendar
    service.events().delete(
        calendarId='primary',
        eventId=event_id
    ).execute()
    
    return {"message": "Event deleted successfully"}  # Return a success message when the event is deleted
