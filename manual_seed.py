import sys
sys.path.insert(0, 'backend')

from backend.app.database import SessionLocal, engine
from backend.app.models import Base, User, Product

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Delete existing users (if any)
db.query(User).delete()
db.query(Product).delete()
db.commit()

# Create user with bcrypt hash for "password123"
user1 = User(
    email="test@test.com",
    username="test",
    hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    full_name="Test User",
    phone="1234567890",
    address="Test Address",
    is_active=True,
    is_admin=False
)

db.add(user1)
db.commit()

print("✅ User created!")
print("Username: test")
print("Password: password123")

# Add a test dress
dress = Product(
    owner_id=user1.id,
    name="Test Saree",
    description="Beautiful test saree",
    category="Saree",
    size="M",
    color="Red",
    brand="Test Brand",
    price=500.0,
    security_deposit=2000.0,
    condition="New",
    stock_quantity=1
)

db.add(dress)
db.commit()

print("✅ Dress added!")
db.close()