"""
Quick setup script for new features
Run this after updating all files
"""
import sys
import os

sys.path.insert(0, 'backend')

from backend.app.database import SessionLocal, engine
from backend.app.models import Base, User, Product
from backend.app.utils.security import get_password_hash

print("🚀 Setting up new features...")
print("="*60)

# Create all tables
print("\n1️⃣ Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created")

# Create directories
print("\n2️⃣ Creating upload directories...")
os.makedirs("uploads/products", exist_ok=True)
os.makedirs("uploads/profiles", exist_ok=True)
print("✅ Directories created")

# Check if data exists
db = SessionLocal()
user_count = db.query(User).count()
product_count = db.query(Product).count()

print(f"\n📊 Current database status:")
print(f"   Users: {user_count}")
print(f"   Products: {product_count}")

if user_count == 0:
    print("\n3️⃣ Creating sample user...")
    
    try:
        user = User(
            email="demo@dressrent.com",
            username="demo",
            hashed_password=get_password_hash("demo123"),
            full_name="Demo User",
            phone="1234567890",
            address="Demo Address",
            bio="This is a demo account",
            is_active=True,
            is_admin=False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print("✅ Demo user created")
        print(f"   Username: demo")
        print(f"   Password: demo123")
        
        # Add sample dress
        print("\n4️⃣ Creating sample dress...")
        dress = Product(
            owner_id=user.id,
            name="Sample Elegant Saree",
            description="Beautiful sample saree for testing",
            category="Saree",
            size="M",
            color="Red",
            brand="Sample Brand",
            price=500.0,
            security_deposit=2000.0,
            condition="New",
            stock_quantity=1
        )
        
        db.add(dress)
        db.commit()
        print("✅ Sample dress created")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
else:
    print("\n✅ Users already exist, skipping sample data creation")

db.close()

print("\n" + "="*60)
print("🎉 Setup complete!")
print("="*60)
print("\n📋 Next steps:")
print("1. Start server: cd backend && uvicorn app.main:app --reload")
print("2. Visit: http://127.0.0.1:8000")
print("3. Login with: demo / demo123")
print("\n✨ New features available:")
print("   - Reviews & Ratings")
print("   - Messaging System")
print("   - Booking Calendar")
print("   - User Profiles")
print("   - Image Upload")
print("\n")