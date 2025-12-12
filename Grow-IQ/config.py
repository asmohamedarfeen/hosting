import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional

class Settings(BaseSettings):
    # =================================================================
    # Application Basic Settings
    # =================================================================
    APP_NAME: str = "Grow-IQ"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production-environment-variable")
    
    # =================================================================
    # Server Settings
    # =================================================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000  # Default, will be overridden by env var or validator
    WORKERS: int = 4
    
    @field_validator('PORT', mode='before')
    @classmethod
    def validate_port(cls, v):
        """Safely parse PORT from environment, handling $PORT literal string"""
        # If already an integer, return as-is
        if isinstance(v, int):
            return v
        # If None or not provided, use default
        if v is None:
            return 8000
        # If string, handle various cases
        if isinstance(v, str):
            # Strip whitespace
            v = v.strip()
            # Handle case where PORT might be set to literal '$PORT' string
            if v == "$PORT" or not v or v == "":
                return 8000
            try:
                return int(v)
            except (ValueError, TypeError):
                return 8000
        # If not string or int, default to 8000
        return 8000
    
    # =================================================================
    # Database Settings
    # =================================================================
    # Defaulting to a local SQLite DB for dev, can be overridden by env for Postgres
    # Use absolute path relative to this file to ensure we use the correct DB
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(_BASE_DIR, 'dashboard.db')}")
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    
    # =================================================================
    # Security & CORS Settings
    # =================================================================
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "100"))
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")
    # CORS Origins - Comma separated list of origins
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8000").split(",")
    
    # =================================================================
    # File Upload Settings
    # =================================================================
    # Default 16MB max file size
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(16 * 1024 * 1024)))
    # Upload folder path
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "./static/uploads")
    
    # =================================================================
    # OAuth Settings (Google)
    # =================================================================
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI")
    
    # =================================================================
    # AI & External API Settings
    # =================================================================
    # Gemini API Key for Resume Analysis and Interview
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "AIzaSyA3f8izcUDNQTik3utegfZ5bKvxeG0vwq8")
    
    # =================================================================
    # Azure Settings (For Deployment)
    # =================================================================
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_CONTAINER_NAME: str = os.getenv("AZURE_CONTAINER_NAME", "media")
    
    # =================================================================
    # Logging
    # =================================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore" # Ignore extra fields in .env file

# Create global settings instance
settings = Settings()

# Ensure critical directories exist
try:
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
except Exception:
    pass
