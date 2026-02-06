import sys
sys.path.insert(0, 'backend')

from backend.app.database import SessionLocal
from backend.app.models import User
from backend.app.utils.security import verify_password, get_password_hash

db = SessionLocal()

# Get user
user = db.query(User).filter(User.username == "test").first()

if user:
    print(f"✅ User exists: {user.username}")
    print(f"📧 Email: {user.email}")
    print(f"🔒 Has password hash: {len(user.hashed_password)} characters")
    
    # Test verification
    test_pass = "password123"
    result = verify_password(test_pass, user.hashed_password)
    print(f"\n🔐 Password verification: {'✅ SUCCESS' if result else '❌ FAILED'}")
    
    # Generate new hash and test
    print("\n🔄 Generating fresh hash...")
    new_hash = get_password_hash(test_pass)
    if new_hash:
        print(f"✅ New hash created: {len(new_hash)} characters")
        test_new = verify_password(test_pass, new_hash)
        print(f"🔐 Fresh hash verification: {'✅ SUCCESS' if test_new else '❌ FAILED'}")
    else:
        print("❌ Failed to create hash")
else:
    print("❌ User not found")

db.close()