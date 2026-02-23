# PixelFort - Minimal FastAPI Application
# Let's start with the simplest possible API server.

from typing import List
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from api.schemas import UserCreate, UserResponse, UserUpdate, PhotoCreate, PhotoResponse
import logging
import hashlib

# Import our settings
from api.config import settings
from api.database import get_db 
from api.models import User, Photo

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

@app.post("/photos", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
def create_photo(photo_data: PhotoCreate, db: Session = Depends(get_db)):
    """
    Create a new photo record.
    
    For now, just stores metadata (no actual file upload).
    """
    # Verify user exists
    user = db.query(User).filter(User.id == photo_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {photo_data.user_id} not found"
        )
    
    # Create photo record
    new_photo = Photo(**photo_data.model_dump())
    
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    
    logger.info(f"Created photo: {new_photo.filename} for user {photo_data.user_id}")
    
    return new_photo

@app.get("/photos", response_model=List[PhotoResponse])
def list_photos(db: Session = Depends(get_db)):
    """
    Get all photos.
    """
    photos = db.query(Photo).all()
    return photos


@app.get("/photos/{photo_id}", response_model=PhotoResponse)
def get_photo(photo_id: int, db: Session = Depends(get_db)):
    """
    Get a specific photo by ID.
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id {photo_id} not found"
        )
    
    return photo

@app.get("/photos", response_model=list[PhotoResponse])
def list_photos(db: Session = Depends(get_db)):
    """
    Get all photos.
    """
    photos = db.query(Photo).all()
    return photos

@app.post("/photos/upload", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile = File(...),
    user_id: int = Form(...),  # For now, hardcoded (TODO: get from auth)
    db: Session = Depends(get_db)
):
    """
    Upload a photo file with content-addressable storage.
    
    - Computes SHA256 hash of file content
    - Saves with hash as filename (deduplication!)
    - Stores metadata in database
    - Returns 400 if file already exists (duplicate)
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Read file content
    contents = await file.read()
    
    # Compute SHA256 hash (content-addressable!)
    file_hash = hashlib.sha256(contents).hexdigest()
    
    # Check if file already exists (deduplication)
    existing_photo = db.query(Photo).filter(Photo.file_hash == file_hash).first()
    if existing_photo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File already exists with id {existing_photo.id}"
        )
    
    # Determine file extension from original filename
    original_name = file.filename or "unknown"
    extension = Path(original_name).suffix or ".jpg"
    
    # Create filename from hash (content-addressable storage!)
    filename = f"{file_hash}{extension}"
    file_path = f"/app/storage/photos/{filename}"
    
    # Ensure storage directory exists
    storage_dir = Path("/app/storage/photos")
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(contents)
    
    logger.info(f"Saved file: {filename} ({len(contents)} bytes, hash: {file_hash[:16]}...)")
    
    # Create database record
    new_photo = Photo(
        filename=filename,
        original_filename=original_name,
        file_path=file_path,
        file_size=len(contents),
        mime_type=file.content_type or "application/octet-stream",
        file_hash=file_hash,
        user_id=user_id
    )
    
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    
    logger.info(f"Created photo record: id={new_photo.id}")
    
    return new_photo

@app.get("/photos/{photo_id}/download")
def download_photo(photo_id: int, db: Session = Depends(get_db)):
    """
    Download the actual photo file.
    
    - Returns the file for browser download
    - Sets proper content-type header
    - Uses original filename for download
    """
    # Find photo in database
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id {photo_id} not found"
        )
    
    # Check if file exists on disk
    file_path = Path(photo.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo file not found on disk: {photo.file_path}"
        )
    
    logger.info(f"Serving file: {photo.filename} (original: {photo.original_filename})")
    
    # Return file
    return FileResponse(
        path=photo.file_path,
        media_type=photo.mime_type,
        filename=photo.original_filename  # Browser will use this name when downloading
    )

@app.get("/photos/{photo_id}/view")
def view_photo(photo_id: int, db: Session = Depends(get_db)):
    """
    View photo in browser (inline, not download).
    
    - Returns file for inline display
    - Good for viewing images in browser
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id {photo_id} not found"
        )
    
    file_path = Path(photo.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo file not found on disk"
        )
    
    # Return file for inline viewing
    return FileResponse(
        path=photo.file_path,
        media_type=photo.mime_type,
        headers={"Content-Disposition": "inline"}  # View in browser, not download
    )

@app.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    """
    Delete a photo by ID.
    
    - Removes database record
    - Deletes actual file from disk
    - Returns 204 No Content on success
    """
    # Find photo in database
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id {photo_id} not found"
        )
    
    # Store file path before deleting database record
    file_path = Path(photo.file_path)
    filename = photo.filename
    
    # Delete database record first
    db.delete(photo)
    db.commit()
    
    logger.info(f"Deleted photo record: {filename} (id={photo_id})")
    
    # Now delete the actual file from disk
    if file_path.exists():
        try:
            file_path.unlink()  # Delete the file
            logger.info(f"Deleted file from disk: {file_path}")
        except Exception as e:
            # File deletion failed, but DB record already gone
            # Log error but don't fail the request
            logger.error(f"Failed to delete file {file_path}: {e}")
            # Note: Database record is already deleted, so we don't rollback
    else:
        logger.warning(f"File not found on disk (already deleted?): {file_path}")
    
    # Return 204 No Content (successful deletion)
@app.get("/users/{user_id}/photos", response_model=List[PhotoResponse])
def get_user_photos(user_id: int, db: Session = Depends(get_db)):
    """
    Get all photos for a specific user.
    
    - Returns empty list if user has no photos
    - Returns 404 if user doesn't exist
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Get user's photos using relationship
    photos = user.photos  # ← This uses the SQLAlchemy relationship!
    
    logger.info(f"Retrieved {len(photos)} photos for user {user_id}")
    
    return photos