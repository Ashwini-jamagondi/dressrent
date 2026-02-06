import sys
sys.path.insert(0, 'backend')

from backend.app.database import SessionLocal
from backend.app.models import User

db = SessionLocal()
users = db.query(User).all()

print(f"Total users in database: {len(users)}")
for user in users:
    print(f"  - Username: {user.username}, Email: {user.email}")

db.close()