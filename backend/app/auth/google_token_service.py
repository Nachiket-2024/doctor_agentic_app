# ------------------------------------- External Imports -------------------------------------
# To make asynchronous HTTP requests to Google APIs  
import httpx  

# For working with datetime objects and time comparisons (with timezone support)  
from datetime import datetime, timedelta, timezone  

# For handling HTTP exceptions in FastAPI  
from fastapi import HTTPException  

# ------------------------------------- Internal Imports -------------------------------------
# Application-wide settings from environment  
from ..core.settings import settings  

# Import models to access token data directly from respective tables  
from ..models.admin_model import Admin  
from ..models.doctor_model import Doctor  
from ..models.patient_model import Patient  

# ------------------------------------- Class: GoogleTokenManager -------------------------------------
class GoogleTokenService:
    """
    Handles Google OAuth2 token refresh and access token retrieval based on user role.
    """

    # ------------------------ Method: Get Valid Access Token ------------------------
    @staticmethod
    async def get_valid_google_access_token(user_id: int, role: str, db):
        """
        Get a valid Google access token for the given user by role.
        If token is expired or near expiry, refresh it using the refresh token.

        Parameters:
        - user_id (int): User ID from the database
        - role (str): User role (admin/doctor/patient)
        - db: SQLAlchemy database session

        Returns:
        - tuple[str, str]: (access_token, refresh_token)
        """
        # Determine the user object based on role  
        if role == "admin":
            user = db.query(Admin).filter(Admin.id == user_id).first()
        elif role == "doctor":
            user = db.query(Doctor).filter(Doctor.id == user_id).first()
        elif role == "patient":
            user = db.query(Patient).filter(Patient.id == user_id).first()
        else:
            raise HTTPException(status_code=400, detail="Invalid user role.")

        # If user record not found  
        if not user:
            print("No user found for provided ID and role.")
            raise HTTPException(status_code=404, detail="User not found.")

        # Extract token expiry field  
        token_expiry = user.token_expiry

        # Convert string to datetime if needed  
        if isinstance(token_expiry, str):
            token_expiry = datetime.fromisoformat(token_expiry)

        # If token is missing or about to expire, refresh it  
        if not token_expiry or token_expiry <= datetime.now(timezone.utc) + timedelta(minutes=2):
            # Use the refresh token to get a new access token  
            new_token_data = await GoogleTokenService.refresh_google_access_token(user.refresh_token)

            # If response lacks access token, raise an error  
            if not new_token_data.get("access_token"):
                raise HTTPException(status_code=400, detail="Failed to refresh Google access token.")

            # Update access token and token expiry  
            user.access_token = new_token_data["access_token"]
            user.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=new_token_data["expires_in"])

            # If refresh token was rotated, update it  
            if "refresh_token" in new_token_data:
                user.refresh_token = new_token_data["refresh_token"]

            # Commit changes to DB  
            db.commit()

        # Return valid access and refresh tokens  
        return user.access_token, user.refresh_token

    # ------------------------ Method: Refresh Google Token ------------------------
    @staticmethod
    async def refresh_google_access_token(refresh_token: str) -> dict:
        """
        Refresh the Google OAuth2 access token using a refresh token.

        Parameters:
        - refresh_token (str): User's stored refresh token

        Returns:
        - dict: Dictionary containing the new access token and possibly new refresh token
        """
        # Define Google's token endpoint URL  
        token_url = "https://oauth2.googleapis.com/token"

        # Prepare request payload  
        payload = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        # Make async POST request  
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=payload)

        # Raise error if request failed  
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to refresh token from Google.")

        # Return the parsed token response  
        return response.json()
