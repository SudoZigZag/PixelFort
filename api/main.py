# PixelFort - Minimal FastAPI Application
# Let's start with the simplest possible API server.

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import logging

# Import our settings
from api.config import settings
from api.database import get_db 
from api.models import User

# Get logger (will use LOG_LEVEL from settings)
logger = logging.getLogger(__name__)

# Create FastAPI app - this is the core object
app = FastAPI(
    title="PixelFort",
    description="Photo NAS System with Configuration Management"
)

# Log startup info
logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode")

# Root endpoint - returns JSON when you visit http://localhost:8000
@app.get("/")
def read_root():
        return {
        "message": f"Hello from {settings.APP_NAME}!",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "log_level": settings.LOG_LEVEL
    }


# Health check - useful for Docker
@app.get("/health")
def health_check():
        return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }
@app.get("/config")
def show_config():
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "api_port": settings.API_PORT,
        "api_host": settings.API_HOST,
        "log_level": settings.LOG_LEVEL,
        "reload_enabled": settings.API_RELOAD,
        "storage_path": settings.STORAGE_PATH,
        "upload_size": settings.MAX_UPLOAD_SIZE,
        "database_url": settings.DATABASE_URL.split("://")[0] + "://***",  # Hide DB path
    }

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    """
    Get all users from database.
    
    This connects FastAPI → SQLAlchemy → Database!
    """
    users = db.query(User).all()
    
    return {
        "count": len(users),
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "created_at": str(user.created_at)
            }
            for user in users
        ]
    }