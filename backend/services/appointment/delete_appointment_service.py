# ---------------------------- External Imports ----------------------------

# Exception class for HTTP error responses
from fastapi import HTTPException

# SQLAlchemy ORM Session for DB operations
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Appointment model
from ...models.appointment_model import Appointment

# Patient and Admin models
from ...models.patient_model import Patient
from ...models.admin_model import Admin

# Auth function to decode token
from ...auth.auth_user_check import AuthUserCheck

# Calendar deletion function
from ...google_integration.google_calender_service import GoogleCalendarService

# Gmail notification utility
from ...google_integration.gmail_service import GmailService

# ---------------------------- Class: AppointmentService ----------------------------

class DeleteAppointmentService:
    """
    Service class for managing appointments, including creation, deletion,
    calendar sync, and notifications.
    """

    # Constructor to inject the database session
    def __init__(self, db: Session):
        # Store DB session as an instance variable
        self.db = db

    # ---------------------------- Method: Delete Appointment ----------------------------

    async def delete_appointment(self, appointment_id: int, token: str):
        """
        Deletes an appointment with proper role check, calendar cleanup, and notification.

        Args:
            appointment_id (int): ID of the appointment to delete
            token (str): JWT token of the user making the request

        Returns:
            None
        """

        # Extract role from token to enforce permissions
        _, user_role, _ = AuthUserCheck.get_user_from_token(token, self.db)

        # Only allow admin to perform delete operations
        if user_role != "admin":
            raise HTTPException(status_code=403, detail="Only admin can delete appointments")

        # Fetch the appointment by its ID
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

        # Raise 404 if appointment doesn't exist
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Fetch the patient associated with this appointment
        patient = self.db.query(Patient).filter(Patient.id == appointment.patient_id).first()

        # Retrieve the default admin user (used as sender for notifications)
        admin = self.db.query(Admin).filter(Admin.id == 1).first()

        # If event ID is present, remove it from Google Calendar
        if appointment.event_id:
            await GoogleCalendarService(db=self.db, user_id=patient.id, user_role="patient").delete_event(
                appointment.event_id
            )

        # Notify patient via Gmail about appointment cancellation
        await GmailService(db=self.db, user_id=admin.id).send_email_via_gmail(
            patient.email,
            "Appointment Cancellation",
            appointment.id,
            email_type="cancelled"
        )

        # Delete appointment record from DB
        self.db.delete(appointment)
        self.db.commit()

        # Return nothing (FastAPI interprets as HTTP 204)
        return
