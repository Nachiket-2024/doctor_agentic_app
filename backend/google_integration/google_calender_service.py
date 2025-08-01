# ---------------------------- External Imports ----------------------------

# To create Google credentials that support refresh tokens
from google.oauth2.credentials import Credentials

# To build and interact with Google API service clients (e.g., Calendar, Gmail)
from googleapiclient.discovery import build

# To use the SQLAlchemy session for database access
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# To fetch valid (and refresh if needed) Google tokens from the database
from ..auth.google_token_service import GoogleTokenService

# Application-level configuration, including Google credentials and scopes
from ..core.settings import settings

# ---------------------------- Class: GoogleCalendarService ----------------------------

class GoogleCalendarService:
    """
    Handles creation, update, and deletion of Google Calendar events using
    user-specific access and refresh tokens.
    """

    def __init__(self, db: Session, user_id: int, user_role: str = "patient"):
        # Initialize the database session
        self.db = db

        # Store the ID of the user (doctor, patient, or admin)
        self.user_id = user_id

        # Store the user's role, defaulting to 'patient'
        self.user_role = user_role

    # ---------------------------- Function: get_google_credentials ----------------------------

    def get_google_credentials(self, access_token: str, refresh_token: str) -> Credentials:
        """
        Builds a Google credentials object using access and refresh tokens.
        Automatically enables token refresh for long-term use.
        """
        # Construct and return a credentials object with all necessary fields
        return Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=settings.GOOGLE_SCOPES,
        )

    # ---------------------------- Function: build_calendar_service ----------------------------

    def build_calendar_service(self, access_token: str, refresh_token: str):
        """
        Returns an authenticated Google Calendar API client using credentials.
        """
        # Get credentials using tokens
        creds = self.get_google_credentials(access_token, refresh_token)

        # Build and return the calendar service client
        return build("calendar", "v3", credentials=creds)

    # ---------------------------- Function: create_event ----------------------------

    async def create_event(self, summary: str, start_time: str, end_time: str, email: str):
        """
        Creates a new Google Calendar event for the authenticated user.
        """

        # Fetch valid access and refresh tokens for the user
        access_token, refresh_token = await GoogleTokenService.get_valid_google_access_token(
            self.user_id, self.user_role, self.db
        )

        # Build the calendar API client
        service = self.build_calendar_service(access_token, refresh_token)

        # Define the event object to be created
        event = {
            "summary": summary,
            "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
            "attendees": [{"email": email}],
        }

        # Insert the event into the user's primary calendar
        return service.events().insert(calendarId="primary", body=event).execute()

    # ---------------------------- Function: update_event ----------------------------

    async def update_event(self, event_id: str, summary: str, start_time: str, end_time: str, email: str):
        """
        Updates an existing event using its event ID and new event data.
        """

        # Fetch valid access and refresh tokens
        access_token, refresh_token = await GoogleTokenService.get_valid_google_access_token(
            self.user_id, self.user_role, self.db
        )

        # Build the calendar API client
        service = self.build_calendar_service(access_token, refresh_token)

        # Construct updated event details
        updated_event = {
            "summary": summary,
            "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
            "attendees": [{"email": email}],
        }

        # Update the existing event with new details
        return service.events().update(
            calendarId="primary",
            eventId=event_id,
            body=updated_event,
        ).execute()

    # ---------------------------- Function: delete_event ----------------------------

    async def delete_event(self, event_id: str):
        """
        Deletes an existing calendar event from the user's Google Calendar.
        """

        # Fetch valid access and refresh tokens
        access_token, refresh_token = await GoogleTokenService.get_valid_google_access_token(
            self.user_id, self.user_role, self.db
        )

        # Build the calendar API client
        service = self.build_calendar_service(access_token, refresh_token)

        # Call the API to delete the specified event
        service.events().delete(calendarId="primary", eventId=event_id).execute()

        # Return confirmation response
        return {"message": "Event deleted successfully"}
