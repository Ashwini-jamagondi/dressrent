import sys
sys.path.insert(0, 'backend')

from backend.app.database import SessionLocal
from backend.app.models import User
from backend.app.utils.security import verify_password

db = SessionLocal()

# Get the test user
user = db.query(User).filter(User.username == "test").first()

if user:
    print(f"✅ User found: {user.username}")
    print(f"📧 Email: {user.email}")
    print(f"🔒 Hashed password: {user.hashed_password[:50]}...")
    
    # Test password verification
    test_password = "password123"
    is_valid = verify_password(test_password, user.hashed_password)
    
    print(f"\n🔐 Testing password 'password123':")
    print(f"   Result: {'✅ CORRECT' if is_valid else '❌ WRONG'}")
else:
    print("❌ User 'test' not found in database!")

db.close()