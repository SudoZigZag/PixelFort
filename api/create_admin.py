"""
Create the first admin user.

Usage: docker-compose exec api python create_admin.py
"""

from api.database import SessionLocal
from api.models import User
from api.auth import hash_password

def create_admin():
    db = SessionLocal()
    
    # Check if admin exists
    existing = db.query(User).filter(User.email == "admin@pixelfort.com").first()
    if existing:
        print("❌ Admin user already exists")
        return
    
    # Create admin
    admin = User(
        email="admin@pixelfort.com",
        username="admin",
        hashed_password=hash_password("ChangeThisPassword123!"),  # ← Change!
        is_admin=True
    )
    
    db.add(admin)
    db.commit()
    
    print("✅ Admin user created!")
    print(f"   Email: {admin.email}")
    print(f"   Username: {admin.username}")
    print("   Password: ChangeThisPassword123!")
    print("")
    print("⚠️  Please login and change the password immediately!")
    
    db.close()

if __name__ == "__main__":
    create_admin()