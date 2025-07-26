# ------------------------------------- External Imports -------------------------------------

# Import BaseModel for schema definitions
from pydantic import BaseModel, ConfigDict

# ------------------------------------- Shared Base Schema -------------------------------------

# Common fields shared across create/update/response
class GoogleIntegrationBase(BaseModel):
    # Access token used for Google API calls
    access_token: str

    # Refresh token used to obtain new access tokens
    refresh_token: str

    # Expiry time of access token (ISO format string), optional
    token_expiry: str | None = None


# ------------------------------------- Create Schema -------------------------------------

# Used when inserting new Google integration tokens
class GoogleIntegrationCreate(GoogleIntegrationBase):
    # ID of the user to associate tokens with
    user_id: int


# ------------------------------------- Update Schema -------------------------------------

# Used when updating tokens after refresh
class GoogleIntegrationUpdate(BaseModel):
    # Updated access token (if applicable)
    access_token: str | None = None

    # Updated refresh token (if applicable)
    refresh_token: str | None = None

    # Updated expiry time (if applicable)
    token_expiry: str | None = None


# ------------------------------------- Response Schema -------------------------------------

# Used when returning Google integration data (e.g., internal API)
class GoogleIntegrationOut(GoogleIntegrationBase):
    # Unique ID for the integration entry
    id: int

    # ID of the associated user
    user_id: int

    class Config(ConfigDict):
        from_attributes = True  # Allows use with SQLAlchemy ORM objects
