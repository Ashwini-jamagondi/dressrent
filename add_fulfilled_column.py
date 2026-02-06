"""
Add fulfilled_by_dress_id column to requests table
Run: python add_fulfilled_column.py
"""

import sqlite3

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

print("\n" + "="*60)
print("🔧 ADDING MISSING COLUMN TO REQUESTS TABLE")
print("="*60)

# Check if column already exists
cursor.execute("PRAGMA table_info(requests)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

if 'fulfilled_by_dress_id' in column_names:
    print("\n✅ Column 'fulfilled_by_dress_id' already exists!")
else:
    print("\n📝 Adding column 'fulfilled_by_dress_id'...")
    cursor.execute("""
        ALTER TABLE requests 
        ADD COLUMN fulfilled_by_dress_id INTEGER
    """)
    conn.commit()
    print("✅ Column added successfully!")

# Verify
cursor.execute("PRAGMA table_info(requests)")
columns = cursor.fetchall()
print("\n📋 Current columns in requests table:")
for col in columns:
    print(f"   - {col[1]} ({col[2]})")

print("\n" + "="*60)
print("✨ Database updated! Now run: python fix_existing_bookings.py")
print("="*60 + "\n")

conn.close()