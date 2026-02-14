"""
Pydantic schemas for request/response validation.

These are DIFFERENT from database models:
- Models (models.py) = database tables
- Schemas (schemas.py) = API request/response shapes
"""

from pydantic import BaseModel, EmailStr, Field


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
    
    class Config:
        from_attributes = True  # Allows creating from SQLAlchemy model

class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    All fields are optional - only update what's provided.
    """
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)