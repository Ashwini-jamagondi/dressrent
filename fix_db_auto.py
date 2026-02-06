import sqlite3
import os
from pathlib import Path

# Search for the database in common locations
search_paths = [
    Path("ecommerce.db"),
    Path("backend/ecommerce.db"),
    Path("backend/app/ecommerce.db"),
    Path("../ecommerce.db"),
]

db_path = None
for path in search_paths:
    if path.exists():
        db_path = path
        break

# If not found, search the entire directory
if not db_path:
    print("🔍 Searching for ecommerce.db...")
    for root, dirs, files in os.walk('.'):
        if 'ecommerce.db' in files:
            db_path = Path(root) / 'ecommerce.db'
            break

if not db_path:
    print("❌ Database file 'ecommerce.db' not found!")
    print("Please run this command to find it:")
    print("   dir ecommerce.db /s")
    exit(1)

print(f"📁 Found database: {db_path.absolute()}")

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check current columns
print("\n📋 Current columns in users table:")
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(f"   - {col[1]} ({col[2]})")

# Check if profile_photo_url exists
column_names = [col[1] for col in columns]

if 'profile_photo_url' in column_names:
    print("\n✅ Column 'profile_photo_url' already exists!")
else:
    print("\n➕ Adding 'profile_photo_url' column...")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_photo_url TEXT")
        conn.commit()
        print("✅ Column 'profile_photo_url' added successfully!")
        
        # Verify
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\n✅ Updated columns in users table:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
            
    except sqlite3.OperationalError as e:
        print(f"❌ Error: {e}")

conn.close()
print("\n🔄 Done! Now restart your FastAPI server.")
print(f"   Database location: {db_path.absolute()}")