from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal
import logging


class Settings(BaseSettings):
    
    # Application settings
    APP_NAME: str = Field(default="pixelfort")
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development"
    )
    
    # API settings
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000, ge=1, le=65535)  # ge=greater or equal, le=less or equal
    API_RELOAD: bool = Field(default=False)
    MAX_UPLOAD_SIZE: int = Field(
        default=10485760,  # 10MB in bytes
        description="Maximum file upload size in bytes"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    
    # Database (future)
    DATABASE_URL: str = Field(default="sqlite:///./storage/db/pixelfort.db")
    
    # Storage
    STORAGE_PATH: str = Field(default="/app/storage/photos")

    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production-min-32-chars")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7)  # 7 days
    
    # Computed properties
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"
    
    # Pydantic configuration
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance (singleton)
settings = Settings()

# Configure logging based on settings
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log startup info
logger.info(f"🔧 Environment: {settings.ENVIRONMENT}")
logger.info(f"🔧 API: {settings.API_HOST}:{settings.API_PORT}")
logger.info(f"🔧 Log Level: {settings.LOG_LEVEL}")