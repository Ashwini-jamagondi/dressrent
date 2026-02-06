import sqlite3
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent
db_path = BASE_DIR / "ecommerce.db"

print(f"📁 Database path: {db_path}")

# Check if database exists
if not db_path.exists():
    print("❌ Database file not found!")
    exit(1)

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