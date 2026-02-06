import os
import sys

backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app.database import SessionLocal
from app.models import User
from app.utils.security import verify_password

db = SessionLocal()

print("\n=== Checking Database ===")

# Get all users
users = db.query(User).all()
print(f"\nTotal users in database: {len(users)}")

if users:
    for user in users:
        print(f"\n✅ User: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Full name: {user.full_name}")
        
        # Test password
        if verify_password("password123", user.hashed_password):
            print(f"   ✅ Password 'password123' is CORRECT")
        else:
            print(f"   ❌ Password 'password123' is WRONG")
else:
    print("\n❌ No users found in database!")
    print("Run: python seed_data.py")

db.close()