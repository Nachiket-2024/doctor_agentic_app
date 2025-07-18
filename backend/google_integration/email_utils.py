import base64  # To encode the email message in base64, required by Gmail API
from email.mime.text import MIMEText  # To create the email message in MIME format (plain text)
from googleapiclient.discovery import build  # To interact with Google APIs like Gmail

# --- Reuse OAuth2 creds & token.json ---
from .calendar_utils import get_calendar_service  # Reuse OAuth2 credentials from the calendar_utils module

# --- Send email using Gmail API ---
def send_email_via_gmail(to_email: str, subject: str, appointment_details: dict):
    """
    Sends an appointment confirmation email using the Gmail API.
    """
    # Get authorized credentials from calendar_utils (the same OAuth2 token used for calendar integration)
    calendar_service = get_calendar_service()
    creds = calendar_service._http.credentials  # Extract OAuth credentials object from the calendar service

    # Build the Gmail API service using the extracted credentials
    gmail_service = build('gmail', 'v1', credentials=creds)

    # Prepare the email body with dynamic appointment details
    body = f"""
    Dear {appointment_details['patient_name']},  # Personalized greeting for the patient

    Your appointment with Dr. {appointment_details['doctor_name']} has been successfully scheduled for:
    
    Date: {appointment_details['appointment_date']}  # Appointment date
    Time: {appointment_details['appointment_time']}  # Appointment time

    Please make sure to arrive 10 minutes early.

    Best regards,
    Your Doctor Appointment System Team
    """

    # Create a MIME text email message using the body content
    message = MIMEText(body)
    message['to'] = to_email  # Set the recipient email
    message['subject'] = subject  # Set the email subject

    # Encode the message as base64url, which is required by Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Use Gmail API to send the email message (sent from the logged-in user's Gmail account)
    gmail_service.users().messages().send(
        userId="me",  # "me" refers to the authenticated user (who owns the token)
        body={'raw': raw_message}  # The raw base64url-encoded email message
    ).execute()  # Execute the API request to send the email
