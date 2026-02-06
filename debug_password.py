"""
Run this script to check and fix the password for user 'priya'
Place this in your backend folder and run: python debug_password.py
"""

from app.database import SessionLocal, engine
from app.models import User
from app.utils.security import get_password_hash, verify_password

def check_and_fix_password():
    db = SessionLocal()
    
    try:
        # Get the user
        user = db.query(User).filter(User.username == "priya").first()
        
        if not user:
            print("❌ User 'priya' not found!")
            return
        
        print(f"✅ User found: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🔐 Current hash (first 50 chars): {user.hashed_password[:50]}...")
        
        # Test the current password
        test_password = "password123"
        print(f"\n🧪 Testing password: '{test_password}'")
        
        is_valid = verify_password(test_password, user.hashed_password)
        print(f"Current password works: {is_valid}")
        
        if not is_valid:
            print("\n🔧 Password doesn't work. Generating new hash...")
            new_hash = get_password_hash(test_password)
            print(f"New hash (first 50 chars): {new_hash[:50]}...")
            
            # Update the user
            user.hashed_password = new_hash
            db.commit()
            print("✅ Password updated!")
            
            # Verify it works now
            is_valid_now = verify_password(test_password, user.hashed_password)
            print(f"New password works: {is_valid_now}")
        else:
            print("\n✅ Password is already correct!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    check_and_fix_password()