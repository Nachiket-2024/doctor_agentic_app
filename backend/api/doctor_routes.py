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

# Create the router for doctor-related routes
router = APIRouter(
    prefix="/doctor",  # All routes will be under /doctor
    tags=["Doctor"],  # Tag to categorize in Swagger docs
)

# ---------------------------- Route: Get Doctor Information ----------------------------
@router.get("/{doctor_id}", response_model=UserResponse)  # Set response model
async def get_doctor(doctor_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get doctor details by doctor_id.
    Accessible by all authenticated users (admin, patient, doctor).
    """
    try:
        # Verify JWT token
        payload = verify_jwt_token(token)
        # Fetch the doctor by ID
        doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()

        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        return doctor  # Return the actual SQLAlchemy object, FastAPI will convert it to Pydantic

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Create Doctor (Admin Only) ----------------------------
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)  # Set response model
async def create_doctor(
    doctor: UserCreate,  # Use Pydantic schema here for request body
    token: str = Depends(oauth2_scheme),  # JWT token for authorization
    db: Session = Depends(get_db)  # Database session dependency
):
    """
    Create a new doctor (admin only).
    """
    try:
        # Check if the user is an admin
        admin = admin_only(token, db)
        
        # Create and add new doctor to the database
        new_doctor = User(
            name=doctor.name,
            email=doctor.email,
            role="doctor",  # Ensure the role is 'doctor'
            specialization=doctor.specialization,
            available_days=doctor.available_days,
            slot_duration=doctor.slot_duration,
        )
        
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)

        return new_doctor  # Return the SQLAlchemy object, FastAPI will convert it to Pydantic

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Update Doctor (Admin Only) ----------------------------
@router.put("/{doctor_id}", response_model=UserResponse)  # Set response model
async def update_doctor(
    doctor_id: int,
    updated_doctor: UserCreate,  # Use Pydantic schema here for request body
    token: str = Depends(oauth2_scheme),  # JWT token for authorization
    db: Session = Depends(get_db)  # Database session dependency
):
    """
    Update doctor details (admin only).
    """
    try:
        # Check if the user is an admin
        admin = admin_only(token, db)

        # Fetch the existing doctor record
        doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
        
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        # Update doctor fields with provided data
        doctor.name = updated_doctor.name if updated_doctor.name else doctor.name
        doctor.email = updated_doctor.email if updated_doctor.email else doctor.email
        doctor.specialization = updated_doctor.specialization if updated_doctor.specialization else doctor.specialization
        doctor.available_days = updated_doctor.available_days if updated_doctor.available_days else doctor.available_days
        doctor.slot_duration = updated_doctor.slot_duration if updated_doctor.slot_duration else doctor.slot_duration

        db.commit()
        db.refresh(doctor)

        return doctor  # Return the SQLAlchemy object, FastAPI will convert it to Pydantic

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Delete Doctor (Admin Only) ----------------------------
@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(
    doctor_id: int,
    token: str = Depends(oauth2_scheme),  # JWT token for authorization
    db: Session = Depends(get_db)  # Database session dependency
):
    """
    Delete doctor details (admin only).
    """
    try:
        # Check if the user is an admin
        admin = admin_only(token, db)

        # Fetch the doctor record to delete
        doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
        
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        # Delete the doctor record
        db.delete(doctor)
        db.commit()

        return {"message": "Doctor deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------- Route: Get All Doctors ----------------------------
@router.get("/", response_model=list[UserResponse])  # Set response model to a list of doctors
async def get_all_doctors(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get all doctors.
    - Admins can see all doctors.
    - Doctors can see their own information.
    - Patients can see all doctors.
    """
    try:
        # Verify JWT token to get user data (email and role)
        payload = verify_jwt_token(token)
        user_email = payload.get("sub")  # 'sub' is usually the email or unique ID
        role = payload.get("role")       # Get user's role from the token

        # ---------- Case: Admin ---------- 
        if role == "admin":
            # Admin sees all doctors
            doctors = db.query(User).filter(User.role == "doctor").all()
            return doctors

        # ---------- Case: Patient ---------- 
        elif role == "patient":
            # Patients can see all doctors
            doctors = db.query(User).filter(User.role == "doctor").all()
            return doctors

        # ---------- Case: Doctor ---------- 
        elif role == "doctor":
            # A doctor can only see their own information
            doctor = db.query(User).filter(User.email == user_email, User.role == "doctor").first()
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor record not found")
            return [doctor]  # Return a list of one doctor (since only the current doctor can see their info)

        # ---------- Invalid Role ---------- 
        else:
            raise HTTPException(status_code=403, detail="Unauthorized role")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
