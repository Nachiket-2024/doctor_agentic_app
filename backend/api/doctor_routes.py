# ---------------------------- External Imports ----------------------------

# Import FastAPI components for routing, dependency injection, HTTP exceptions, and status codes
from fastapi import APIRouter, Depends, HTTPException, status

# Import Session class from SQLAlchemy ORM for database interactions
from sqlalchemy.orm import Session

# Import OAuth2PasswordBearer to handle OAuth2 token extraction from Authorization header
from fastapi.security import OAuth2PasswordBearer

# ---------------------------- Internal Imports ----------------------------

# Import User model (SQLAlchemy ORM)
from ..models.user_model import User

# Import Pydantic schemas for request validation and response serialization
from ..schemas.user_schema import UserCreate, UserResponse

# Import function to obtain database session dependency
from ..db.session import get_db

# Import JWT token verification utility
from ..auth.auth_utils import verify_jwt_token

# Import admin-only access control dependency
from ..auth.auth_user_check import admin_only

# ---------------------------- Initialization ----------------------------

# Initialize OAuth2 scheme for extracting token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create API router for doctor-related endpoints with prefix and tags
router = APIRouter(
    prefix="/doctor",  # All endpoints start with /doctor
    tags=["Doctor"],   # Tag for automatic docs grouping
)

# ---------------------------- Route: Get Doctor Information ----------------------------

@router.get("/{doctor_id}", response_model=UserResponse)
async def get_doctor(
    doctor_id: int,                      # Doctor's ID from path parameter
    token: str = Depends(oauth2_scheme),# JWT token extracted from Authorization header
    db: Session = Depends(get_db)        # Database session dependency
):
    """
    Retrieve doctor details by doctor ID.
    Accessible by any authenticated user.
    """
    try:
        # Verify and decode JWT token to confirm authentication
        payload = verify_jwt_token(token)
        email = payload.get("sub")        # Still extract email if needed

        # Query for doctor with matching ID and role 'doctor'
        doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()

        # Raise 404 if doctor not found
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Return doctor ORM object, FastAPI converts to Pydantic model automatically
        return doctor

    except Exception as e:
        # Return 500 internal server error with exception message
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Create Doctor (Admin Only) ----------------------------

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor: UserCreate,                 # Request body validated with UserCreate schema
    token: str = Depends(oauth2_scheme), # JWT token for admin authorization
    db: Session = Depends(get_db)         # Database session dependency
):
    """
    Create a new doctor.
    Access restricted to admin users.
    """
    try:
        # Ensure requester has admin privileges
        admin = admin_only(token, db)

        # Instantiate new User ORM object with role 'doctor' and provided data
        new_doctor = User(
            name=doctor.name,
            email=doctor.email,
            role="doctor",
            specialization=doctor.specialization,
            available_days=doctor.available_days,
            slot_duration=doctor.slot_duration,
        )

        # Add and commit new doctor to the database
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)  # Refresh to get auto-generated fields like ID

        # Return created doctor record
        return new_doctor

    except Exception as e:
        # Return 500 error with exception details
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Update Doctor (Admin Only) ----------------------------

@router.put("/{doctor_id}", response_model=UserResponse)
async def update_doctor(
    doctor_id: int,                     # ID of doctor to update
    updated_doctor: UserCreate,         # Updated data validated by UserCreate schema
    token: str = Depends(oauth2_scheme), # JWT token for admin authorization
    db: Session = Depends(get_db)         # Database session dependency
):
    """
    Update existing doctor details.
    Access restricted to admin users.
    """
    try:
        # Confirm requester is admin
        admin = admin_only(token, db)

        # Retrieve existing doctor record from database
        doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()

        # Raise 404 if doctor does not exist
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Update fields only if new values are provided
        doctor.name = updated_doctor.name if updated_doctor.name else doctor.name
        doctor.email = updated_doctor.email if updated_doctor.email else doctor.email
        doctor.specialization = updated_doctor.specialization if updated_doctor.specialization else doctor.specialization
        doctor.available_days = updated_doctor.available_days if updated_doctor.available_days else doctor.available_days
        doctor.slot_duration = updated_doctor.slot_duration if updated_doctor.slot_duration else doctor.slot_duration

        # Commit changes to database and refresh updated object
        db.commit()
        db.refresh(doctor)

        # Return updated doctor record
        return doctor

    except Exception as e:
        # Return 500 error with exception details
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Delete Doctor (Admin Only) ----------------------------

@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(
    doctor_id: int,                    # ID of doctor to delete
    token: str = Depends(oauth2_scheme), # JWT token for admin authorization
    db: Session = Depends(get_db)         # Database session dependency
):
    """
    Delete a doctor by ID.
    Access restricted to admin users.
    """
    try:
        # Ensure requester is admin
        admin = admin_only(token, db)

        # Query doctor record to delete
        doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()

        # Raise 404 if doctor not found
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Delete doctor and commit transaction
        db.delete(doctor)
        db.commit()

        # Return no content for successful deletion
        return

    except Exception as e:
        # Return 500 error with exception details
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Get All Doctors ----------------------------

@router.get("/", response_model=list[UserResponse])
async def get_all_doctors(
    token: str = Depends(oauth2_scheme), # JWT token for authentication
    db: Session = Depends(get_db)          # Database session dependency
):
    """
    Retrieve all doctors.
    Access rules:
    - Admins and Patients see all doctors.
    - Doctors see only their own record.
    """
    try:
        # Verify and decode JWT token to get user details
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")   # Extract email as well for compatibility
        role = payload.get("role")        # User role from token

        # Admin can see all doctors
        if role == "admin":
            doctors = db.query(User).filter(User.role == "doctor").all()
            return doctors

        # Patients can see all doctors
        elif role == "patient":
            doctors = db.query(User).filter(User.role == "doctor").all()
            return doctors

        # Doctors can see only their own data
        elif role == "doctor":
            doctor = db.query(User).filter(User.email == user_email, User.role == "doctor").first()
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor record not found")
            return [doctor]  # Return list with one doctor

        # Any other role is unauthorized
        else:
            raise HTTPException(status_code=403, detail="Unauthorized role")

    except Exception as e:
        # Return 500 error with exception details
        raise HTTPException(status_code=500, detail=str(e))
