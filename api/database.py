from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from api.config import settings

# Create database engine
# Engine = the connection to the database
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite only
    echo=settings.is_development  # Log SQL queries in development
)

# SessionLocal = factory for creating database sessions
# A session = a "conversation" with the database
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base = parent class for all our database models
# When we define models, they'll inherit from this
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db  # Give the session to the route
    finally:
        db.close()  # Always close when done