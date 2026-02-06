import sys
sys.path.insert(0, 'backend')

from backend.app.database import SessionLocal
from backend.app.models import User
import bcrypt

db = SessionLocal()

# Get user
user = db.query(User).filter(User.username == "test").first()

if user:
    print(f"✅ User found: {user.username}")
    print(f"🔒 Stored hash: {user.hashed_password[:50]}...")
    
    # Test with bcrypt directly (bypassing security.py)
    password = "password123"
    try:
        is_valid = bcrypt.checkpw(
            password.encode('utf-8'),
            user.hashed_password.encode('utf-8')
        )
        print(f"\n🔐 Direct bcrypt test: {'✅ CORRECT' if is_valid else '❌ WRONG'}")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ User not found")

db.close()