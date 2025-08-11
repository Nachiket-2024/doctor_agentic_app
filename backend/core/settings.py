# ---------------------------- External Imports ----------------------------

# Import BaseSettings for creating settings models using environment variables
from pydantic_settings import BaseSettings

# Import Field to declare and configure model attributes with validation and metadata
from pydantic import Field

# ---------------------------- Settings Class ----------------------------

# Define a Settings class to centralize configuration loaded from environment variables
class Settings(BaseSettings):
    # PostgreSQL Database URL, typically includes user, password, host, port, and DB name
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # JWT secret key used for signing access and refresh tokens
    JWT_SECRET: str = Field(..., env="JWT_SECRET")

    # Algorithm used for JWT token signing (e.g., HS256)
    JWT_ALGORITHM: str = Field(..., env="JWT_ALGORITHM")

    # Expiry time for access tokens in minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Expiry time for refresh tokens in days
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(..., env="REFRESH_TOKEN_EXPIRE_DAYS")

    # Google OAuth2 client ID used for authentication
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")

    # Google OAuth2 client secret used for authentication
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")

    # Google OAuth2 redirect URI used to handle the callback after user consents
    GOOGLE_REDIRECT_URI: str = Field(..., env="GOOGLE_REDIRECT_URI")

    # Scopes requested during Google OAuth2 flow, typically space-separated
    GOOGLE_SCOPES: str = Field(..., env="GOOGLE_SCOPES")

    # Path to the local token file where Google access tokens are stored
    GOOGLE_TOKEN_FILE: str = Field(..., env="GOOGLE_TOKEN_FILE")

    # Frontend application's redirect URI after authentication completes
    FRONTEND_REDIRECT_URI: str = Field(..., env="FRONTEND_REDIRECT_URI")

    # Backend base URL where FastAPI is running
    BACKEND_URL: str = Field(..., env="BACKEND_URL")

    # Name of the LLM model served by Ollama (e.g., "llama3", "mistral")
    OLLAMA_MODEL: str = Field(..., env="OLLAMA_MODEL")

    # Sampling temperature for the LLM, affects randomness of outputs
    OLLAMA_TEMPERATURE: float = Field(..., env="OLLAMA_TEMPERATURE")

    # Ollama Base Url is where Ollama server / llm is running
    OLLAMA_BASE_URL: str = Field(..., env="OLLAMA_BASE_URL")

    # ---------------------------- Config Class ----------------------------

    # Internal class to configure environment file loading
    class Config:
        # Specify the .env file to load environment variables from
        env_file = ".env"

# ---------------------------- Instantiate Settings ----------------------------

# Create a global settings object to be reused throughout the application
settings = Settings()
