from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from api.database import Base


class User(Base):
    """
    User table.
    
    Represents a user of the PixelFort system.
    """
    
    # Table name in database
    __tablename__ = "users"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Timestamps (automatically set)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    photos = relationship("Photo", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation (for debugging)"""
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

class Photo(Base):
    """
    Photo table.
    
    Stores metadata about uploaded photos.
    """
    __tablename__ = "photos"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String)   # image/jpeg, image/png, etc.
    file_hash = Column(String, unique=True, index=True, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="photos")
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Photo(id={self.id}, filename={self.filename})>"