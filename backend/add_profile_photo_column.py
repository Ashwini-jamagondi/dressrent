# Save as: backend/add_profile_photo_column.py
# Run this ONCE to add the profile_photo_url column to your database

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'ecommerce.db')

def add_profile_photo_column():
    print("🔧 Adding profile_photo_url column to users table...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'profile_photo_url' in columns:
            print("✅ Column already exists!")
        else:
            # Add the column
            cursor.execute("ALTER TABLE users ADD COLUMN profile_photo_url VARCHAR")
            conn.commit()
            print("✅ Column added successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_profile_photo_column()