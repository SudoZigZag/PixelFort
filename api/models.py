from sqlalchemy import Column, Integer, String, DateTime
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
    
    def __repr__(self):
        """String representation (for debugging)"""
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"