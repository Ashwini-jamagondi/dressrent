import os
import sys

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Now import

from app.database import SessionLocal, engine
from app.utils.security import get_password_hash

# Import models after setting up the path
import app.models as models

# Create tables
models.Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    
    # Check if data exists
    db.query(models.Product).delete()
    db.query(models.User).delete()
    db.commit()
    
    # Create sample users
    users = [
        models.User(
            email="priya@dressrent.com",
            username="priya",
            hashed_password=get_password_hash("password123"),
            full_name="Priya Sharma",
            phone="9876543210",
            address="Mumbai, Maharashtra",
            location="Mumbai, Maharashtra",
            bio="Fashion enthusiast and dress collector"
        ),
        models.User(
            email="rahul@dressrent.com",
            username="rahul",
            hashed_password=get_password_hash("password123"),
            full_name="Rahul Kumar",
            phone="9876543211",
            address="Delhi, India",
            location="Delhi, India",
            bio="Love sharing my designer collection"
        ),
        models.User(
            email="anita@dressrent.com",
            username="anita",
            hashed_password=get_password_hash("password123"),
            full_name="Anita Verma",
            phone="9876543212",
            address="Bangalore, Karnataka",
            location="Bangalore, Karnataka",
            bio="Passionate about ethnic wear"
        )
    ]
    
    for user in users:
        db.add(user)
    
    db.commit()
    
    # Create sample dresses
    dresses = [
        # Sarees
        models.Product(
            owner_id=1,
            name="Elegant Silk Saree - Red",
            description="Beautiful red silk saree perfect for weddings and festivals",
            category="Saree",
            size="Free Size",
            color="Red",
            brand="Kanchipuram Silks",
            price_per_day=50.0,
            security_deposit=2000.0,
            condition="Like New",
            location="Mumbai, Maharashtra"
        ),
        models.Product(
            owner_id=1,
            name="Designer Banarasi Saree",
            description="Traditional Banarasi saree with golden work",
            category="Saree",
            size="Free Size",
            color="Blue",
            brand="Varanasi Weaves",
            price_per_day=60.0,
            security_deposit=2500.0,
            condition="Excellent",
            location="Mumbai, Maharashtra"
        ),
        
        # Lehengas
        models.Product(
            owner_id=2,
            name="Bridal Lehenga - Pink",
            description="Stunning pink bridal lehenga with heavy embroidery",
            category="Lehenga",
            size="M",
            color="Pink",
            brand="Manish Malhotra",
            price_per_day=200.0,
            security_deposit=10000.0,
            condition="Like New",
            location="Delhi, India"
        ),
        models.Product(
            owner_id=2,
            name="Party Wear Lehenga - Green",
            description="Beautiful green lehenga for parties and functions",
            category="Lehenga",
            size="L",
            color="Green",
            brand="Sabyasachi",
            price_per_day=150.0,
            security_deposit=7000.0,
            condition="Good",
            location="Delhi, India"
        ),
        
        # Gowns
        models.Product(
            owner_id=3,
            name="Evening Gown - Black",
            description="Elegant black evening gown for formal events",
            category="Gown",
            size="M",
            color="Black",
            brand="Zara",
            price_per_day=80.0,
            security_deposit=3000.0,
            condition="Like New",
            location="Bangalore, Karnataka"
        ),
        models.Product(
            owner_id=3,
            name="Wedding Guest Gown - Maroon",
            description="Sophisticated maroon gown perfect for wedding guests",
            category="Gown",
            size="S",
            color="Maroon",
            brand="H&M",
            price_per_day=70.0,
            security_deposit=2500.0,
            condition="Good",
            location="Bangalore, Karnataka"
        ),
        
        # Suits
        models.Product(
            owner_id=1,
            name="Anarkali Suit - Purple",
            description="Beautiful purple Anarkali suit with dupatta",
            category="Suit",
            size="L",
            color="Purple",
            brand="Biba",
            price_per_day=40.0,
            security_deposit=1500.0,
            condition="Good",
            location="Mumbai, Maharashtra"
        ),
        models.Product(
            owner_id=2,
            name="Punjabi Suit - Yellow",
            description="Vibrant yellow Punjabi suit for festivals",
            category="Suit",
            size="M",
            color="Yellow",
            brand="W",
            price_per_day=35.0,
            security_deposit=1200.0,
            condition="Like New",
            location="Delhi, India"
        ),
        
        # Traditional
        models.Product(
            owner_id=3,
            name="South Indian Pattu Pavadai",
            description="Traditional South Indian dress for ceremonies",
            category="Traditional",
            size="S",
            color="Gold",
            brand="Nalli Silks",
            price_per_day=55.0,
            security_deposit=2000.0,
            condition="Excellent",
            location="Bangalore, Karnataka"
        ),
        models.Product(
            owner_id=1,
            name="Bengali Tant Saree",
            description="Traditional Bengali tant saree",
            category="Traditional",
            size="Free Size",
            color="White",
            brand="Bengal Handloom",
            price_per_day=30.0,
            security_deposit=1000.0,
            condition="Good",
            location="Mumbai, Maharashtra"
        ),
        
        # Western
        models.Product(
            owner_id=2,
            name="Cocktail Dress - Blue",
            description="Stylish blue cocktail dress for parties",
            category="Western",
            size="M",
            color="Blue",
            brand="Forever 21",
            price_per_day=45.0,
            security_deposit=1500.0,
            condition="Like New",
            location="Delhi, India"
        ),
        models.Product(
            owner_id=3,
            name="Maxi Dress - Floral",
            description="Beautiful floral maxi dress for summer events",
            category="Western",
            size="L",
            color="Multicolor",
            brand="Zara",
            price_per_day=40.0,
            security_deposit=1200.0,
            condition="Good",
            location="Bangalore, Karnataka"
        )
    ]
    
    for dress in dresses:
        db.add(dress)
    
    db.commit()
    
    print("\n" + "="*60)
    print("✅ Database seeded successfully!")
    print("="*60)
    print("\n📋 Sample Login Credentials:")
    print("-" * 60)
    print("Username: priya  | Password: password123 | Location: Mumbai")
    print("Username: rahul  | Password: password123 | Location: Delhi")
    print("Username: anita  | Password: password123 | Location: Bangalore")
    print("-" * 60)
    print("\n🎉 You can now:")
    print("  • Login with any of the above credentials")
    print("  • Browse 12 sample dresses")
    print("  • Rent dresses from other users")
    print("  • List your own dresses for rent")
    print("="*60 + "\n")
    
    db.close()

if __name__ == "__main__":
    seed_database()