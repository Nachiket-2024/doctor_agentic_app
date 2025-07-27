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
    to_email: str,             # Recipient's email address
    subject: str,              # Subject of the email
    appointment_id: int,       # ID of the appointment to include in the message
    db: Session,               # Database session for querying data
    email_type: str = "created"  # Type of email: created, updated, or cancelled
):
    """
    Sends an appointment email (confirmation, update, or cancellation) using the user's Gmail.
    Only accepts 'created', 'updated', or 'cancelled' as valid email types.
    """

    # Step 1: Fetch appointment details
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Step 2: Fetch doctor and patient details
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    if not doctor or not patient:
        raise HTTPException(status_code=404, detail="Doctor or Patient not found")

    # Step 3: Get valid access and refresh tokens for the admin user
    access_token, refresh_token = await get_valid_google_access_token(user_id, "admin", db)

    # Step 4: Build Gmail API client using credentials
    credentials = get_google_credentials(access_token, refresh_token)
    gmail_service = build("gmail", "v1", credentials=credentials)

    # Step 5: Prepare appointment info to format into email
    appointment_details = {
        'patient_name': patient.name,
        'doctor_name': doctor.name,
        'appointment_date': appointment.date,
        'appointment_time': f"{appointment.start_time} - {appointment.end_time}",
    }

    # Step 6: Choose email body based on email_type argument
    if email_type == "created":
        body = f"""
        Dear {appointment_details['patient_name']},

        Your appointment with {appointment_details['doctor_name']} has been successfully scheduled.

        Date: {appointment_details['appointment_date']}
        Time: {appointment_details['appointment_time']}

        Please arrive 10 minutes early.

        Best regards  
        Doctor Agentic App Team
        """

    elif email_type == "updated":
        body = f"""
        Dear {appointment_details['patient_name']},

        Your appointment with {appointment_details['doctor_name']} has been updated.

        New Date: {appointment_details['appointment_date']}
        New Time: {appointment_details['appointment_time']}

        Please check your calendar and arrive on time.

        Best regards  
        Doctor Agentic App Team
        """

    elif email_type == "cancelled":
        body = f"""
        Dear {appointment_details['patient_name']},

        Your appointment with {appointment_details['doctor_name']} on {appointment_details['appointment_date']} at 
        {appointment_details['appointment_time']} has been **cancelled**.

        If this was unexpected, please contact us to reschedule.

        Best regards  
        Doctor Agentic App Team
        """

    else:
        # Raise error for invalid type
        raise HTTPException(status_code=400, detail="Invalid email type. Must be 'created', 'updated', or 'cancelled'.")

    # Step 7: Build MIME message with the constructed body
    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = subject

    # Step 8: Encode message in base64 for Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Step 9: Send email using Gmail API
    gmail_service.users().messages().send(
        userId="me",
        body={'raw': raw_message}
    ).execute()

    # Step 10: Return confirmation response
    return {"message": "Email sent successfully"}
