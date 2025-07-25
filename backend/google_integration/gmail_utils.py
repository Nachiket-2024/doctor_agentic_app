# ------------------------------------- Imports -------------------------------------
import base64  # For encoding the MIME message
from email.mime.text import MIMEText  # For creating email content
from googleapiclient.discovery import build  # For Gmail API service
from sqlalchemy.orm import Session  # For querying the database
from fastapi import HTTPException  # For raising error responses

# Import database models
from ..models.user_model import User  # Represents the User table
from ..models.appointment_model import Appointment  # Represents the Appointment table

# Import credentials builder from calendar_utils (shared logic)
from .calendar_utils import get_google_credentials  # Returns a properly scoped credentials object

# ---------------------------- Send Gmail Message ----------------------------
def send_email_via_gmail(
    access_token: str,
    refresh_token: str,
    to_email: str,
    subject: str,
    appointment_id: int,
    db: Session
):
    """
    Sends an appointment confirmation email using Gmail API on behalf of the user.
    Requires both access_token and refresh_token for token refresh support.
    """

    # ------------------ Step 1: Fetch appointment ------------------
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # ------------------ Step 2: Fetch doctor and patient ------------------
    doctor = db.query(User).filter(User.id == appointment.doctor_id).first()
    patient = db.query(User).filter(User.id == appointment.patient_id).first()
    if not doctor or not patient:
        raise HTTPException(status_code=404, detail="Doctor or Patient not found")

    # ------------------ Step 3: Build Gmail service ------------------
    credentials = get_google_credentials(access_token, refresh_token)  # Create Credentials object
    gmail_service = build("gmail", "v1", credentials=credentials)  # Build Gmail API client

    # ------------------ Step 4: Create email body ------------------
    appointment_details = {
        'patient_name': patient.name,
        'doctor_name': doctor.name,
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

    # ------------------ Step 5: Build and encode email ------------------
    message = MIMEText(body)  # Plain text email content
    message['to'] = to_email
    message['subject'] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()  # Gmail API requires base64url

    # ------------------ Step 6: Send email ------------------
    gmail_service.users().messages().send(
        userId="me",  # "me" refers to the authenticated user
        body={'raw': raw_message}
    ).execute()

    return {"message": "Email sent successfully"}
