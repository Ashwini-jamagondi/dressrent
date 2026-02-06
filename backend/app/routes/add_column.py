import sqlite3
import os

# Find your database file
db_files = ['sql_app.db', 'app.db', 'database.db', 'ecommerce.db']
db_path = None

for db_file in db_files:
    if os.path.exists(db_file):
        db_path = db_file
        break
    # Check in backend folder
    backend_path = os.path.join('backend', db_file)
    if os.path.exists(backend_path):
        db_path = backend_path
        break

if not db_path:
    print("❌ Database file not found!")
    print("Please enter the path to your database file:")
    db_path = input().strip()

print(f"📁 Using database: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current columns
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
print("\n📋 Current columns in users table:")
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
    except sqlite3.OperationalError as e:
        print(f"❌ Error: {e}")

conn.close()
print("\n✅ Done! Restart your FastAPI server now.")