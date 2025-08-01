# ---------------------------- External Imports ----------------------------

# For managing SQLAlchemy database sessions  
from sqlalchemy.orm import Session

# FastAPI exception for consistent error responses  
from fastapi import HTTPException

# ---------------------------- Internal Imports ----------------------------

# JWT token verification utility and determine user role ,id function  
from .auth_utils import AuthUtils

# ---------------------------- Class: IdentityExtractor ----------------------------

class AuthUserCheck:
    """
    Utility class for extracting user identity from a JWT token.
    """

    # ------------------------ Method: Get User from Token ------------------------

    @staticmethod
    def get_user_from_token(token: str, db: Session) -> tuple[str, str, int]:
        """
        Decodes JWT token, extracts email, determines user role and ID.

        Parameters:
        - token (str): OAuth2 Bearer token
        - db (Session): SQLAlchemy session

        Returns:
        - tuple[str, str, int]: user_email, user_role, user_id
        """
        try:
            # Decode the token to get payload  
            payload = AuthUtils.verify_jwt_token(token)
            user_email = payload.get("sub")

            # Raise error if email is not present  
            if not user_email:
                raise HTTPException(status_code=401, detail="Invalid token: no email found")

            # Reuse internal logic to determine role and ID  
            user_role, user_id = AuthUtils.determine_user_role_and_id(user_email, db)

            # Return extracted identity tuple  
            return user_email, user_role, user_id

        except Exception as e:
            # Raise standard HTTP error for any exception  
            raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
