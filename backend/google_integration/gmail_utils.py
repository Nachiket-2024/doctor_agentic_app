import base64
from email.mime.text import MIMEText  # For creating email message
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from .calendar_utils import get_calendar_service  # Reuse OAuth2 credentials from the calendar_utils module
from ..models.user_model import User  # User model stores both doctor and patient details
from ..models.appointment_model import Appointment  # Appointment model stores appointment details
from fastapi import HTTPException

def send_email_via_gmail(to_email: str, subject: str, appointment_id: int, db: Session):
    """
    Sends an appointment confirmation email using the Gmail API.
    This function fetches the appointment details from the database and sends a confirmation email.
    """
    # Get the appointment details from the database
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Fetch the patient and doctor details
    doctor = db.query(User).filter(User.id == appointment.doctor_id).first()
    patient = db.query(User).filter(User.id == appointment.patient_id).first()

    if not doctor or not patient:
        raise HTTPException(status_code=404, detail="Doctor or Patient not found")

    # Get authorized credentials from calendar_utils (the same OAuth2 token used for calendar integration)
    calendar_service = get_calendar_service()
    creds = calendar_service._http.credentials  # Extract OAuth credentials object from the calendar service

    # Build the Gmail API service using the extracted credentials
    gmail_service = build('gmail', 'v1', credentials=creds)

    # Prepare the email body with dynamic appointment details
    appointment_details = {
        'patient_name': patient.name,  # Assuming User model has 'name' field
        'doctor_name': doctor.name,    # Assuming User model has 'name' field
        'appointment_date': appointment.date,
        'appointment_time': f"{appointment.start_time} - {appointment.end_time}",
    }

    body = f"""
    Dear {appointment_details['patient_name']},

    Your appointment with Dr. {appointment_details['doctor_name']} has been successfully scheduled for:
    
    Date: {appointment_details['appointment_date']} 
    Time: {appointment_details['appointment_time']} 

    Please make sure to arrive 10 minutes early.

    Best regards,
    Your Doctor Agentic App Team
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

    return {"message": "Email sent successfully"}  # Return a success message
