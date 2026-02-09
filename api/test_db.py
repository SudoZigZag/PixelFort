from api.database import SessionLocal
from api.models import User


def test_create_user():
    """Create a test user."""
    # Create a database session
    db = SessionLocal()
    
    try:
        # Create a new user object
        new_user = User(
            email="alice@example.com",
            username="alice",
            hashed_password="fake_hashed_password_123"  # In real app, hash this!
        )
        
        # Add to database
        db.add(new_user)
        db.commit()  # Save changes
        db.refresh(new_user)  # Get the ID that was generated
        
        print(f"✅ Created user: {new_user}")
        print(f"   ID: {new_user.id}")
        print(f"   Email: {new_user.email}")
        print(f"   Username: {new_user.username}")
        print(f"   Created: {new_user.created_at}")
        
    finally:
        db.close()


def test_query_users():
    """Query all users."""
    db = SessionLocal()
    
    try:
        # Query all users
        users = db.query(User).all()
        
        print(f"\n📋 Found {len(users)} user(s):")
        for user in users:
            print(f"   - {user.username} ({user.email})")
            
    finally:
        db.close()


if __name__ == "__main__":
    print("Testing database operations...\n")
    test_create_user()
    test_query_users()