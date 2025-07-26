# ------------------------------------- External Imports -------------------------------------

# For encoding the MIME message
import base64

# For creating plain text email content
from email.mime.text import MIMEText

# For Gmail API service
from googleapiclient.discovery import build

# For database access
from sqlalchemy.orm import Session

# For raising HTTP errors
from fastapi import HTTPException


# ------------------------------------- Internal Imports -------------------------------------

# Appointment model to fetch appointment details
from ..models.appointment_model import Appointment

# Doctor model for fetching doctor details
from ..models.doctor_model import Doctor

# Patient model for fetching patient details
from ..models.patient_model import Patient

# Utility function to build Google credentials from tokens
from .calendar_utils import get_google_credentials

# Utility function to securely fetch valid tokens for a user
from ..auth.google_token_service import get_valid_google_access_token


# ---------------------------------- Send Gmail Message ----------------------------------

async def send_email_via_gmail(
    user_id: int,              # ID of the user whose Gmail will be used to send the mail
    from_email: str,           # The Gmail address from which the email is sent
    to_email: str,             # Recipient's email address
    subject: str,              # Subject of the email
    appointment_id: int,       # ID of the appointment to include in the message
    db: Session                # Database session for querying data
):
    """
    Sends an appointment confirmation email using the user's Gmail account.
    Automatically refreshes access token if expired before sending.
    """

    # -------- Step 1: Fetch appointment details --------
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        # Raise error if appointment not found
        raise HTTPException(status_code=404, detail="Appointment not found")

    # -------- Step 2: Fetch doctor and patient details --------
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    if not doctor or not patient:
        # Raise error if either doctor or patient not found
        raise HTTPException(status_code=404, detail="Doctor or Patient not found")

    # -------- Step 3: Get valid access and refresh tokens --------
    access_token, refresh_token = await get_valid_google_access_token(user_id, from_email, db)

    # -------- Step 4: Build Gmail API service with credentials --------
    credentials = get_google_credentials(access_token, refresh_token)
    gmail_service = build("gmail", "v1", credentials=credentials)

    # -------- Step 5: Construct appointment email content --------
    appointment_details = {
        'patient_name': patient.name,
        'doctor_name': doctor.name,
        'appointment_date': appointment.date,
        'appointment_time': f"{appointment.start_time} - {appointment.end_time}",
    }

    # Compose email body with personalized appointment details
    body = f"""
    Dear {appointment_details['patient_name']},

    Your appointment with {appointment_details['doctor_name']} has been successfully scheduled for:

    Date: {appointment_details['appointment_date']}
    Time: {appointment_details['appointment_time']}

    Please make sure to arrive 10 minutes early.

    Best regards,
    Your Doctor Agentic App Team
    """

    # -------- Step 6: Encode email using base64 as required by Gmail API --------
    message = MIMEText(body)
    message['to'] = to_email
    message['from'] = from_email
    message['subject'] = subject

    # Encode the message in base64 URL-safe format
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # -------- Step 7: Send email using Gmail API --------
    gmail_service.users().messages().send(
        userId="me",
        body={'raw': raw_message}
    ).execute()

    # -------- Step 8: Return success response --------
    return {"message": "Email sent successfully"}
