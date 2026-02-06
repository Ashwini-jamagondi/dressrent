import sys
sys.path.insert(0, 'backend')

from backend.app.database import SessionLocal, engine
from backend.app.models import Base, User, Product
from backend.app.utils.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Delete all data
db.query(User).delete()
db.query(Product).delete()
db.commit()

print("Creating user...")

# Create user
password_hash = get_password_hash("password123")

if password_hash:
    user = User(
        email="test@test.com",
        username="test",
        hashed_password=password_hash,
        full_name="Test User",
        phone="1234567890",
        address="Test Address",
        is_active=True,
        is_admin=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"✅ User created: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Password: password123")
    
    # Create dress
    dress = Product(
        owner_id=user.id,
        name="Test Saree",
        description="Beautiful test saree",
        category="Saree",
        size="M",
        color="Red",
        brand="Test",
        price=500.0,
        security_deposit=2000.0,
        condition="New",
        stock_quantity=1
    )
    
    db.add(dress)
    db.commit()
    print("✅ Dress added!")
else:
    print("❌ Failed to hash password")

db.close()