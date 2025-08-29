# ---------------------------- External Imports ----------------------------
# Exception class for HTTP errors
from fastapi import HTTPException

# SQLAlchemy session type
from sqlalchemy.orm import Session

# ---------------------------- Internal Imports ----------------------------
# SQLAlchemy model for Appointment
from ...models.appointment_model import Appointment

# Auth utility to extract user info from token
from ...auth.auth_user_check import AuthUserCheck

# ---------------------------- Class: AppointmentService ----------------------------
class GetAllAppointmentsService:
    """
    Service class for managing appointments (CRUD, notifications, calendar sync).
    """

    # Constructor to inject the database session
    def __init__(self, db: Session):
        # Store DB session for use in methods
        self.db = db

    # ---------------------------- Method: Get All Appointments ----------------------------
    async def get_all_appointments(self, token: str):
        """
        Fetch all appointments based on the role of the authenticated user.

        Args:
            token (str): JWT token of the requesting user

        Returns:
            List[Appointment]: List of appointment objects
        """

        try:
            # Extract user role and ID from token
            _, user_role, user_id = AuthUserCheck.get_user_from_token(token, self.db)

            # If user is admin, return all appointments
            if user_role == "admin":
                return self.db.query(Appointment).all()

            # If user is a doctor, return only their appointments
            elif user_role == "doctor":
                return self.db.query(Appointment).filter(Appointment.doctor_id == user_id).all()

            # If user is a patient, return only their appointments
            elif user_role == "patient":
                return self.db.query(Appointment).filter(Appointment.patient_id == user_id).all()

            # Raise an error for unrecognized roles
            else:
                raise HTTPException(status_code=403, detail="Not authorized to view appointments.")

        # Re-raise FastAPI HTTP exceptions
        except HTTPException as http_exc:
            raise http_exc

        # Catch and raise unexpected internal errors
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
