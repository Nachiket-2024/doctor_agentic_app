import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from .calendar_utils import get_calendar_service  # Reuse OAuth2 creds & token.json

# --- Send email using Gmail API ---
def send_email_via_gmail(to_email: str, subject: str, body: str):
    # Get authorized credentials from calendar_utils (shared OAuth2 token)
    calendar_service = get_calendar_service()
    creds = calendar_service._http.credentials  # Extract OAuth credentials object

    # Build the Gmail API service
    gmail_service = build('gmail', 'v1', credentials=creds)

    # Create a MIME text email message
    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = subject

    # Encode the message as base64url required by Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Use Gmail API to send the email message
    gmail_service.users().messages().send(
        userId="me",
        body={'raw': raw_message}
    ).execute()
