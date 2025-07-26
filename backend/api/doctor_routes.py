# ---------------------------- External Imports ----------------------------

# Import FastAPI core components
from fastapi import APIRouter, Depends, HTTPException, status

# Import Session class from SQLAlchemy
from sqlalchemy.orm import Session

# OAuth2 dependency to extract token
from fastapi.security import OAuth2PasswordBearer

# ---------------------------- Internal Imports ----------------------------

# Import Doctor ORM model
from ..models.doctor_model import Doctor

# Import Pydantic schemas for Doctor
from ..schemas.doctor_schema import DoctorCreate, DoctorRead, DoctorUpdate, DoctorDeleteResponse

# Import DB session getter
from ..db.session import get_db

# JWT verification function
from ..auth.auth_utils import verify_jwt_token

# Function to determine user's role and ID
from ..auth.auth_user_check import determine_user_role_and_id

# ---------------------------- Initialization ----------------------------

# OAuth2 token extractor
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FastAPI router instance
router = APIRouter(
    prefix="/doctor",
    tags=["Doctor"],
)

# ---------------------------- Route: Get Doctor by ID ----------------------------

@router.get("/{doctor_id}", response_model=DoctorRead)
async def get_doctor(
    doctor_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Retrieve a doctor by their ID.
    """
    try:
        # Validate token and extract email
        payload = verify_jwt_token(token)
        email = payload.get("sub")

        # Fetch doctor from DB
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

        # Raise 404 if not found
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Return doctor
        return doctor

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Create Doctor (Admin Only) ----------------------------

@router.post("/", response_model=DoctorRead, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor: DoctorCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Create a new doctor (Admin only).
    """
    try:
        # Validate token and get user role
        payload = verify_jwt_token(token)
        email = payload.get("sub")
        role, _ = determine_user_role_and_id(email, db)

        # Only admins allowed
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Create and persist new doctor
        new_doctor = Doctor(**doctor.model_dump())
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)

        return new_doctor

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Update Doctor (Admin Only) ----------------------------

@router.put("/{doctor_id}", response_model=DoctorRead)
async def update_doctor(
    doctor_id: int,
    updated_doctor: DoctorUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Update a doctor (Admin only).
    """
    try:
        # Validate and authorize
        payload = verify_jwt_token(token)
        email = payload.get("sub")
        role, _ = determine_user_role_and_id(email, db)

        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Fetch doctor
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Apply updates
        for key, value in updated_doctor.model_dump(exclude_unset=True).items():
            setattr(doctor, key, value)

        db.commit()
        db.refresh(doctor)
        return doctor

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Delete Doctor (Admin Only) ----------------------------

@router.delete("/{doctor_id}", response_model=DoctorDeleteResponse)
async def delete_doctor(
    doctor_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Delete a doctor (Admin only).
    """
    try:
        # Authorize user
        payload = verify_jwt_token(token)
        email = payload.get("sub")
        role, _ = determine_user_role_and_id(email, db)

        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Locate doctor
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        db.delete(doctor)
        db.commit()

        return DoctorDeleteResponse(
            message="Doctor deleted successfully",
            doctor_id=doctor_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------- Route: Get All Doctors ----------------------------

@router.get("/", response_model=list[DoctorRead])
async def get_all_doctors(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Retrieve all doctors.
    - Admins & patients: see all.
    - Doctors: see only self.
    """
    try:
        # Get token info
        payload = verify_jwt_token(token)
        email = payload.get("sub")
        role, user_id = determine_user_role_and_id(email, db)

        # Return all doctors for admin/patient
        if role in ("admin", "patient"):
            return db.query(Doctor).all()

        # Return only current doctor for doctors
        elif role == "doctor":
            doctor = db.query(Doctor).filter(Doctor.id == user_id).first()
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")
            return [doctor]

        # Deny others
        else:
            raise HTTPException(status_code=403, detail="Unauthorized role")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
