# PixelFort - Minimal FastAPI Application
# Let's start with the simplest possible API server.

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.schemas import UserCreate, UserResponse, UserUpdate
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
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    - Validates email format
    - Checks for duplicates
    - Hashes password (fake for now)
    - Saves to database
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user (in real app, hash the password!)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=f"fake_hash_{user_data.password}"  # TODO: Use bcrypt!
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Get the generated ID

    logger.info(f"Created user: {new_user.username} ({new_user.email})")

    return new_user

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID.

    - Returns 404 if user doesn't exist
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID.

    - Returns 404 if user doesn't exist
    - Returns 204 No Content on success
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    db.delete(user)
    db.commit()

    logger.info(f"Deleted user: {user.username} (id={user.id})")

    # 204 returns no content (return None or nothing)
@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user's information.
    
    - Only provided fields are updated
    - Returns 404 if user doesn't exist
    - Returns 400 if email/username already taken
    """
    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Check if new email already exists (if email being updated)
    if user_data.email and user_data.email != user.email:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check if new username already exists (if username being updated)
    if user_data.username and user_data.username != user.username:
        existing = db.query(User).filter(User.username == user_data.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update only provided fields
    if user_data.email:
        user.email = user_data.email
    if user_data.username:
        user.username = user_data.username
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"Updated user {user_id}: {user.username}")
    
    return user