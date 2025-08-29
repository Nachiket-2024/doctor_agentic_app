# ------------------------------------- External Imports -------------------------------------
# For encoding the MIME message to base64
import base64

# For constructing plain-text MIME email content
from email.mime.text import MIMEText

# For building the Gmail API client
from googleapiclient.discovery import build

# For accessing the database session
from sqlalchemy.orm import Session

# For handling HTTP exceptions in FastAPI
from fastapi import HTTPException

# ------------------------------------- Internal Imports -------------------------------------
# Appointment model to fetch appointment details
from ..models.appointment_model import Appointment

# Doctor model to fetch doctor details
from ..models.doctor_model import Doctor

# Patient model to fetch patient details
from ..models.patient_model import Patient

# Service to create credentials for Google APIs
from .google_calender_service import GoogleCalendarService

# Service to retrieve and refresh Google access tokens securely
from ..auth.google_token_service import GoogleTokenService

# ------------------------------------- Class: GmailService -------------------------------------
class GmailService:
    """
    GmailService provides functionality to send appointment-related emails (created, updated, cancelled)
    using the Google Gmail API for the authenticated admin user.
    """

    def __init__(self, db: Session, user_id: int):
        # Store the database session for querying models
        self.db = db

        # Store the user ID (typically the admin's ID)
        self.user_id = user_id

        # Assume role is fixed to "admin" for now
        self.user_role = "admin"

    # ----------------- Function: send_email -----------------
    async def send_email_via_gmail(
        self,
        to_email: str,                 # Email address of the recipient (patient)
        subject: str,                  # Subject line of the email
        appointment_id: int,          # ID of the appointment being notified about
        email_type: str = "created"   # Email type: created, updated, or cancelled
    ):
        """
        Sends a Gmail message to notify a patient about an appointment status.
        """

        # ----------------- Step 1: Fetch appointment -----------------
        # Query the appointment by ID from the database
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

        # Raise error if appointment is not found
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # ----------------- Step 2: Fetch doctor and patient -----------------
        # Fetch doctor associated with the appointment
        doctor = self.db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()

        # Fetch patient associated with the appointment
        patient = self.db.query(Patient).filter(Patient.id == appointment.patient_id).first()

        # Raise error if either doctor or patient is missing
        if not doctor or not patient:
            raise HTTPException(status_code=404, detail="Doctor or Patient not found")

        # ----------------- Step 3: Generate Google credentials -----------------
        # Get a valid access and refresh token for this user
        access_token, refresh_token = await GoogleTokenService.get_valid_google_access_token(
            self.user_id,
            self.user_role,
            self.db
        )

        # Build Google credentials using the tokens
        credentials = GoogleCalendarService(self.db, self.user_id, self.user_role).get_google_credentials(access_token, refresh_token)

        # ----------------- Step 4: Initialize Gmail API client -----------------
        # Use the credentials to build the Gmail API service
        gmail_service = build("gmail", "v1", credentials=credentials)

        # ----------------- Step 5: Construct email body -----------------
        # Dynamically create the email message content
        body = self._build_email_body(email_type, patient.name, doctor.name, appointment)

        # ----------------- Step 6: Construct MIME message -----------------
        # Build a MIMEText object from the email body
        message = MIMEText(body)

        # Set recipient email address
        message["to"] = to_email

        # Set email subject
        message["subject"] = subject

        # Encode the MIME message in base64 for Gmail API
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # ----------------- Step 7: Send the email -----------------
        # Send the email through Gmail API
        gmail_service.users().messages().send(
            userId="me",               # "me" refers to the authenticated user
            body={"raw": raw_message}  # Include the base64-encoded MIME message
        ).execute()

        # ----------------- Step 8: Return success response -----------------
        # Return a simple success confirmation
        return {"message": "Email sent successfully"}

    # ----------------- Function: _build_email_body -----------------
    def _build_email_body(
        self,
        email_type: str,                  # Type of notification email (created, updated, cancelled)
        patient_name: str,               # Name of the patient
        doctor_name: str,                # Name of the doctor
        appointment: Appointment         # Appointment instance
    ) -> str:
        """
        Constructs the appropriate email body based on the email type.
        """

        # Extract appointment date and time details
        date = appointment.date
        time_range = f"{appointment.start_time} - {appointment.end_time}"

        # If appointment was just created
        if email_type == "created":
            return f"""
            Dear {patient_name},

            Your appointment with {doctor_name} has been successfully scheduled.

            Date: {date}
            Time: {time_range}

            Please arrive 10 minutes early.

            Best regards  
            Doctor Agentic App Team
            """

        # If appointment was updated
        elif email_type == "updated":
            return f"""
            Dear {patient_name},

            Your appointment with {doctor_name} has been updated.

            New Date: {date}
            New Time: {time_range}

            Please check your calendar and arrive on time.

            Best regards  
            Doctor Agentic App Team
            """

        # If appointment was cancelled
        elif email_type == "cancelled":
            return f"""
            Dear {patient_name},

            Your appointment with {doctor_name} on {date} at {time_range} has been **cancelled**.

            If this was unexpected, please contact us to reschedule.

            Best regards  
            Doctor Agentic App Team
            """

        # If an invalid email type was passed
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid email type. Must be 'created', 'updated', or 'cancelled'."
            )
