import sys
sys.path.insert(0, 'backend')

from backend.app.database import SessionLocal
from backend.app.models import User
import bcrypt

db = SessionLocal()

# Generate new hash
password = "password123"
salt = bcrypt.gensalt()
new_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Update user
user = db.query(User).filter(User.username == "test").first()
if user:
    user.hashed_password = new_hash
    db.commit()
    print("✅ Password updated!")
    print(f"New hash: {new_hash}")
    
    # Test it
    is_valid = bcrypt.checkpw(password.encode('utf-8'), new_hash.encode('utf-8'))
    print(f"Verification test: {'✅ WORKS' if is_valid else '❌ FAILED'}")
else:
    print("❌ User not found")

db.close()