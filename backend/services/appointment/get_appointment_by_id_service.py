# ---------------------------- External Imports ----------------------------

# Exception class for HTTP error responses
from fastapi import HTTPException

# SQLAlchemy ORM Session for DB interactions
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------

# Appointment model from SQLAlchemy
from ...models.appointment_model import Appointment

# Utility to extract user info from token
from ...auth.auth_user_check import AuthUserCheck

# ---------------------------- Class: GetAppointmentByIDService ----------------------------

class GetAppointmentByIDService:
    """
    Service class to retrieve a specific appointment by ID with authorization checks.
    """

    # Constructor to inject the database session
    def __init__(self, db: Session):
        # Store DB session for use in methods
        self.db = db

    # ---------------------------- Method: Get Appointment by ID ----------------------------

    async def get_appointment_by_id(self, appointment_id: int, token: str):
        """
        Fetch a specific appointment by ID with access control based on user role.

        Args:
            appointment_id (int): The appointment's unique identifier
            token (str): JWT token from the request

        Returns:
            Appointment: The requested appointment object if authorized

        Raises:
            HTTPException: 403 if unauthorized, 404 if not found
        """

        # Extract user identity and role from token
        _, user_role, user_id = AuthUserCheck.get_user_from_token(token, self.db)

        # Query the appointment by its ID
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

        # Raise 404 if the appointment does not exist
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Allow access for admin, or if the user is the doctor or patient on the appointment
        if user_role == "admin" or \
           (user_role == "doctor" and appointment.doctor_id == user_id) or \
           (user_role == "patient" and appointment.patient_id == user_id):
            return appointment

        # Deny access for unauthorized users
        raise HTTPException(status_code=403, detail="You are not authorized to view this appointment")
