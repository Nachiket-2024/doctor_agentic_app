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
from ...auth.auth_user_check import get_user_from_token

# Calendar deletion function
from ...google_integration.calendar_utils import delete_event

# Gmail notification utility
from ...google_integration.gmail_utils import send_email_via_gmail

# ---------------------------- Function: Delete Appointment ----------------------------

# Delete an appointment with access control and calendar/email cleanup
async def delete_appointment_entry(appointment_id: int, token: str, db: Session):
    # Extract user details from token
    _, user_role, _ = get_user_from_token(token, db)

    # Only admin users are allowed to delete appointments
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete appointments")

    # Retrieve appointment by ID
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Retrieve the patient associated with the appointment
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()

    # Retrieve the default admin account (assumed to be ID 1)
    admin = db.query(Admin).filter(Admin.id == 1).first()

    # If a calendar event exists, remove it from Google Calendar
    if appointment.event_id:
        await delete_event(patient.id, db, appointment.event_id)

    # Send a cancellation email to the patient
    await send_email_via_gmail(admin.id, patient.email, "Appointment Cancellation", appointment.id, db, email_type="cancelled")

    # Delete the appointment from the database
    db.delete(appointment)
    db.commit()

    # Return nothing (HTTP 204)
    return
