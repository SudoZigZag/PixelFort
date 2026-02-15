"""
Pydantic schemas for request/response validation.

These are DIFFERENT from database models:
- Models (models.py) = database tables
- Schemas (schemas.py) = API request/response shapes
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime


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
    created_at: datetime
    
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
    
    class Config:
        from_attributes = True