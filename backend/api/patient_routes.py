# Import necessary FastAPI components for routing, dependencies, and HTTP handling
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session  # ORM session for database interaction
from fastapi.security import OAuth2PasswordBearer  # OAuth2 scheme for JWT token extraction

# Import database models
from ..models.user_model import User  # SQLAlchemy User model
# Import request/response schemas
from ..schemas.user_schema import UserCreate, UserResponse
# Import function to get database session
from ..db.session import get_db
# Import utility to verify JWT tokens
from ..auth.auth_utils import verify_jwt_token
# Import role-based dependency for admin-only access
from ..auth.auth_user_check import admin_only

# OAuth2 token extractor (reads token from Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize FastAPI router with a prefix and tags for docs
router = APIRouter(
    prefix="/patient",  # All routes start with /patient
    tags=["Patient"],   # Tagged as "Patient" in Swagger UI
)

# ---------------------------- Route: Get Patient by ID ----------------------------
@router.get("/{patient_id}", response_model=UserResponse)
async def get_patient(patient_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get a single patient's details by ID.
    Accessible by the patient themselves or an admin.
    """
    try:
        # Decode JWT token and extract user identity
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")

        # Fetch patient from DB by ID and ensure role is 'patient'
        patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Only the patient or admin can view this record
        if patient.email != user_email and payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="You can only view your own information")

        return patient  # FastAPI will auto-convert to UserResponse
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Create Patient ----------------------------
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: UserCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Create a new patient.
    If the user is a patient, they create their own account.
    Admins can create patient accounts for others.
    """
    try:
        # Decode JWT token
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")

        # Check if a patient already exists with this email
        existing_patient = db.query(User).filter(User.email == user_email, User.role == "patient").first()

        if existing_patient:
            raise HTTPException(status_code=400, detail="Patient already exists")

        # Create patient instance from input data
        new_patient = User(
            name=patient.name,
            email=patient.email,
            role="patient",
            age=patient.age,
            phone_number=patient.phone_number,
        )

        # Admins can create on behalf of others
        if payload.get("role") == "admin":
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)
            return new_patient

        # Regular patients can register themselves
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Update Patient ----------------------------
@router.put("/{patient_id}", response_model=UserResponse)
async def update_patient(
    patient_id: int,
    updated_patient: UserCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Update a patient's info.
    Allowed for the patient themselves or an admin.
    """
    try:
        # Decode token
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")

        # Fetch patient to update
        patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Only the owner or an admin can update
        if patient.email != user_email and payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="You can only update your own information")

        # Update fields conditionally
        patient.name = updated_patient.name or patient.name
        patient.email = updated_patient.email or patient.email
        patient.age = updated_patient.age or patient.age
        patient.phone_number = updated_patient.phone_number or patient.phone_number

        db.commit()
        db.refresh(patient)
        return patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Delete Patient (Admin Only) ----------------------------
@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(patient_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Delete a patient record.
    Only admins are allowed to delete.
    """
    try:
        # Ensure the user is an admin
        admin = admin_only(token, db)

        # Fetch patient by ID
        patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Delete and commit
        db.delete(patient)
        db.commit()
        return {"message": "Patient deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Get All Patients ----------------------------
@router.get("/", response_model=list[UserResponse])
async def get_all_patients(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Return patient list depending on the role:
    - Admin: sees all patients
    - Doctor: logic TBD
    - Patient: sees only self
    """
    try:
        # Decode JWT token to get payload data like email and role
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")  # 'sub' is usually the email or unique ID
        role = payload.get("role")       # Get user's role from the token

        # ---------- Case: Admin ----------
        if role == "admin":
            admin_only(token, db)  # Will raise 403 if not a valid admin

            # Query all patients from User table
            patients = db.query(User).filter(User.role == "patient").all()
            return patients

        # ---------- Case: Patient ----------
        elif role == "patient":
            # Return only the patient record of the logged-in user
            patient = db.query(User).filter(User.email == user_email, User.role == "patient").first()
            if not patient:
                raise HTTPException(status_code=404, detail="Patient record not found")
            return [patient]  # Must return a list to match response_model

        # ---------- Case: Doctor ----------
        elif role == "doctor":
            # Doctor logic to be implemented later (placeholder for now)
            doctor = db.query(User).filter(User.email == user_email, User.role == "doctor").first()
            if not doctor:
                raise HTTPException(status_code=403, detail="Doctor not found")
            raise HTTPException(status_code=501, detail="Doctor-patient filtering not yet implemented")

        # ---------- Invalid Role ----------
        else:
            raise HTTPException(status_code=403, detail="Unauthorized role")

    except Exception as e:
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        raise HTTPException(status_code=500, detail="Internal Server Error")
