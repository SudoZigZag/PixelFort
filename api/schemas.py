"""
Pydantic schemas for request/response validation.

These are DIFFERENT from database models:
- Models (models.py) = database tables
- Schemas (schemas.py) = API request/response shapes
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    Used to validate incoming POST request data.
    """
    email: EmailStr  # Validates email format!
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    """
    Schema for user response.
    What we send back to the client.
    """
    id: int
    email: str
    username: str
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Allows creating from SQLAlchemy model

class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    All fields are optional - only update what's provided.
    """
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)


class PhotoCreate(BaseModel):
    """
    Schema for creating a photo (metadata only for now).
    """
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str = "image/jpeg"
    user_id: int


class PhotoResponse(BaseModel):
    """
    Schema for photo response.
    """
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    file_hash: str
    user_id: int
    uploaded_at: datetime 
    thumbnail_path: Optional[str] = None
    # EXIF metadata (all optional - might not exist)
    date_taken: Optional[datetime] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    
    class Config:
        from_attributes = True
    
# Authentication Schemas

class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenData(BaseModel):
    """Schema for data stored in JWT token."""
    user_id: Optional[int] = None
