# Import necessary FastAPI components
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

# Import models
from ..models.user_model import User
from ..schemas.user_schema import UserCreate, UserResponse  # Import the Pydantic models
from ..db.session import get_db
from ..auth.auth_utils import verify_jwt_token  # JWT token verification utility
from ..auth.auth_user_check import admin_only  # Admin-only access dependency

# Initialize OAuth2PasswordBearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create the router for patient-related routes
router = APIRouter(
    prefix="/patient",  # All routes will be under /patient
    tags=["Patient"],  # Tag to categorize in Swagger docs
)

# ---------------------------- Route: Get Patient Information ----------------------------
@router.get("/{patient_id}", response_model=UserResponse)  # Set response model
async def get_patient(patient_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get patient details by patient_id.
    Accessible by all authenticated users, but only the relevant patient's data is returned.
    """
    try:
        # Verify JWT token and get the logged-in user's info
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")  # Extract user email from token
        
        # Fetch the patient record by ID
        patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Check if the logged-in user is the same as the patient being queried or if the user is an admin
        if patient.email != user_email and payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="You can only view your own information")
        
        return patient  # Return the actual SQLAlchemy object, FastAPI will convert it to Pydantic

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Create Patient (Admin or Self) ----------------------------
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)  # Set response model
async def create_patient(
    patient: UserCreate,  # Use Pydantic schema here for request body
    token: str = Depends(oauth2_scheme),  # JWT token for authorization
    db: Session = Depends(get_db)  # Database session dependency
):
    """
    Create a new patient (admin or self).
    New logins are patients by default.
    """
    try:
        # If the user is not an admin, they are assumed to be a new patient creating their own account
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")  # Extract user email from token

        # Check if the user is trying to create their own account
        existing_patient = db.query(User).filter(User.email == user_email, User.role == "patient").first()

        if existing_patient:
            raise HTTPException(status_code=400, detail="Patient already exists")

        # If not an admin, create the user as a patient
        new_patient = User(
            name=patient.name,
            email=patient.email,
            role="patient",  # Ensure the role is 'patient'
            age=patient.age,
            phone_number=patient.phone_number,
        )

        # If an admin is creating a patient, they can specify details
        if payload.get("role") == "admin":
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)
            return {"message": "Patient created successfully", "patient_id": new_patient.id}

        # If the user is a patient, they can create their own account without needing admin
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)

        return {"message": "Account created successfully. You are logged in as a patient.", "patient_id": new_patient.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Update Patient (Admin or Self) ----------------------------
@router.put("/{patient_id}", response_model=UserResponse)  # Set response model
async def update_patient(
    patient_id: int,
    updated_patient: UserCreate,  # Use Pydantic schema here for request body
    token: str = Depends(oauth2_scheme),  # JWT token for authorization
    db: Session = Depends(get_db)  # Database session dependency
):
    """
    Update patient details (admin or the patient themselves).
    """
    try:
        # Verify JWT token and get the logged-in user's info
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")  # Extract user email from token
        
        # Fetch the existing patient record
        patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Ensure that the patient is either the one requesting the update or an admin
        if patient.email != user_email and payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="You can only update your own information")

        # Update patient fields with provided data
        patient.name = updated_patient.name if updated_patient.name else patient.name
        patient.email = updated_patient.email if updated_patient.email else patient.email
        patient.age = updated_patient.age if updated_patient.age else patient.age
        patient.phone_number = updated_patient.phone_number if updated_patient.phone_number else patient.phone_number

        db.commit()
        db.refresh(patient)

        return {"message": "Patient updated successfully", "patient_id": patient.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Delete Patient (Admin Only) ----------------------------
@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    token: str = Depends(oauth2_scheme),  # JWT token for authorization
    db: Session = Depends(get_db)  # Database session dependency
):
    """
    Delete patient details (admin only).
    """
    try:
        # Check if the user is an admin
        admin = admin_only(token, db)

        # Fetch the patient record to delete
        patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Delete the patient record
        db.delete(patient)
        db.commit()

        return {"message": "Patient deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
