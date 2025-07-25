# ---------------------------- External Imports ----------------------------

# Import FastAPI components for routing, dependency injection, HTTP errors, and status codes
from fastapi import APIRouter, Depends, HTTPException, status
  
# SQLAlchemy ORM session for database interactions
from sqlalchemy.orm import Session   

# OAuth2 scheme to extract JWT token from Authorization header
from fastapi.security import OAuth2PasswordBearer              

# ---------------------------- Internal Imports ----------------------------

# User SQLAlchemy model representing users and patients
from ..models.user_model import User       

# Pydantic schemas for validating request/response data
from ..schemas.user_schema import UserCreate, UserResponse  

# Dependency function to get a DB session instance
from ..db.session import get_db   

# Utility to verify the validity of JWT tokens
from ..auth.auth_utils import verify_jwt_token   

# Dependency enforcing that only admins can access a route
from ..auth.auth_user_check import admin_only                    

# ---------------------------- OAuth2 Setup ----------------------------

# OAuth2PasswordBearer instance to extract token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")          

# ---------------------------- Router Setup ----------------------------

# Create FastAPI router instance with prefix and tags for grouping endpoints
router = APIRouter(
    prefix="/patient",   # All endpoints under /patient
    tags=["Patient"],    # Grouped under "Patient" tag in docs
)

# ---------------------------- Route: Get Patient by ID ----------------------------

@router.get("/{patient_id}", response_model=UserResponse)
async def get_patient(
    patient_id: int,                         # Patient ID path parameter
    token: str = Depends(oauth2_scheme),    # JWT token extracted from header
    db: Session = Depends(get_db)            # Database session injected
):
    """
    Retrieve a single patient's details by ID.
    Accessible by the patient themselves or an admin.
    """
    try:
        # Verify JWT token and extract payload
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")  # Email of requester

        # Query DB for patient with given ID and role 'patient'
        patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()

        # If patient not found, raise 404
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Only the patient themselves or an admin can view this record
        if patient.email != user_email and payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="You can only view your own information")

        # Return patient details, FastAPI serializes via UserResponse schema
        return patient
    except Exception as e:
        # Catch-all for unexpected errors, return HTTP 500 with error details
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Create Patient ----------------------------

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: UserCreate,                     # Request body validated against UserCreate schema
    token: str = Depends(oauth2_scheme),    # JWT token dependency
    db: Session = Depends(get_db)            # DB session dependency
):
    """
    Create a new patient.
    Patients can create their own accounts.
    Admins can create accounts on behalf of others.
    """
    try:
        # Verify JWT token and extract user info
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")

        # Check if patient already exists with this email
        existing_patient = db.query(User).filter(User.email == user_email, User.role == "patient").first()
        if existing_patient:
            raise HTTPException(status_code=400, detail="Patient already exists")

        # Create new User instance with role 'patient'
        new_patient = User(
            name=patient.name,
            email=patient.email,
            role="patient",
            age=patient.age,
            phone_number=patient.phone_number,
        )

        # Admin can create patient on behalf of others
        if payload.get("role") == "admin":
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)
            return new_patient

        # Normal patients can create their own account
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_patient
    except Exception as e:
        # Return 500 on error with exception details
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Update Patient ----------------------------

@router.put("/{patient_id}", response_model=UserResponse)
async def update_patient(
    patient_id: int,                        # Patient ID to update
    updated_patient: UserCreate,            # Updated patient data
    token: str = Depends(oauth2_scheme),   # JWT token dependency
    db: Session = Depends(get_db)           # DB session dependency
):
    """
    Update a patient's information.
    Allowed only for the patient themselves or admins.
    """
    try:
        # Decode token and get requester info
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")

        # Retrieve patient from DB
        patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Authorization: only self or admin allowed to update
        if patient.email != user_email and payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="You can only update your own information")

        # Update fields if provided, else retain old values
        patient.name = updated_patient.name or patient.name
        patient.email = updated_patient.email or patient.email
        patient.age = updated_patient.age or patient.age
        patient.phone_number = updated_patient.phone_number or patient.phone_number

        # Commit changes to DB
        db.commit()
        db.refresh(patient)
        return patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Delete Patient (Admin Only) ----------------------------

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,                        # Patient ID to delete
    token: str = Depends(oauth2_scheme),   # JWT token dependency
    db: Session = Depends(get_db)           # DB session dependency
):
    """
    Delete a patient record.
    Only accessible by admin users.
    """
    try:
        # Ensure user is admin, raises if not
        admin_only(token, db)

        # Find patient by ID
        patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Delete patient and commit transaction
        db.delete(patient)
        db.commit()
        return {"message": "Patient deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Get All Patients ----------------------------

@router.get("/", response_model=list[UserResponse])
async def get_all_patients(
    token: str = Depends(oauth2_scheme),   # JWT token dependency
    db: Session = Depends(get_db)           # DB session dependency
):
    """
    Return a list of patients filtered by the requester's role:
    - Admin: returns all patients.
    - Patient: returns only their own record.
    - Doctor: not implemented yet, raises 501.
    """
    try:
        # Decode token payload to get user email and role
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")
        role = payload.get("role")

        # Admin can see all patients
        if role == "admin":
            admin_only(token, db)  # Enforce admin check

            patients = db.query(User).filter(User.role == "patient").all()
            return patients

        # Patient sees only their own record
        elif role == "patient":
            patient = db.query(User).filter(User.email == user_email, User.role == "patient").first()
            if not patient:
                raise HTTPException(status_code=404, detail="Patient record not found")
            return [patient]  # Return list for schema compatibility

        # Doctor functionality to be implemented
        elif role == "doctor":
            doctor = db.query(User).filter(User.email == user_email, User.role == "doctor").first()
            if not doctor:
                raise HTTPException(status_code=403, detail="Doctor not found")
            raise HTTPException(status_code=501, detail="Doctor-patient filtering not yet implemented")

        # Invalid roles get forbidden
        else:
            raise HTTPException(status_code=403, detail="Unauthorized role")

    except Exception as e:
        import traceback
        traceback.print_exc()  # Log traceback to console
        raise HTTPException(status_code=500, detail="Internal Server Error")
