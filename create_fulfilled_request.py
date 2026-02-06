"""
Create a Saree request and mark it as fulfilled
Run: python create_fulfilled_request.py
"""

import sqlite3
from datetime import datetime

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

print("\n" + "="*60)
print("📝 CREATING SAREE REQUEST")
print("="*60)

# User Aishu (ID: 5) made bookings for Saree
user_id = 5
dress_id = 19  # Latest booking is for dress 19

# Get dress details
cursor.execute("""
    SELECT id, name, size, color, category, price_per_day
    FROM products
    WHERE id = ?
""", (dress_id,))

dress = cursor.fetchone()

if dress:
    print(f"\n✅ Found dress:")
    print(f"   Dress ID: {dress[0]}")
    print(f"   Name: {dress[1]}")
    print(f"   Size: {dress[2]}")
    print(f"   Color: {dress[3]}")
    print(f"   Category: {dress[4]}")
    print(f"   Price: ₹{dress[5]}/day")

# Create the request
print(f"\n📝 Creating request for user Aishu (ID: {user_id})...")

now = datetime.now().isoformat()

cursor.execute("""
    INSERT INTO requests 
    (user_id, dress_type, description, size, color_preference, 
     occasion, budget_min, budget_max, needed_by_date, 
     status, fulfilled_by_dress_id, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    user_id,
    "Saree",
    "Looking for a traditional Saree",
    dress[2] if dress else "S",  # Use dress size
    dress[3] if dress else None,  # Use dress color
    "Wedding",
    200,
    200,
    None,
    "fulfilled",  # Mark as fulfilled
    dress_id,  # Fulfilled by dress 19
    now,
    now
))

conn.commit()
request_id = cursor.lastrowid

print(f"   ✅ Request created! ID: {request_id}")

# Verify
cursor.execute("""
    SELECT id, user_id, dress_type, status, fulfilled_by_dress_id
    FROM requests
    WHERE id = ?
""", (request_id,))

new_request = cursor.fetchone()

print(f"\n✅ VERIFIED:")
print(f"   Request #{new_request[0]}")
print(f"   User ID: {new_request[1]}")
print(f"   Dress Type: {new_request[2]}")
print(f"   Status: {new_request[3]}")
print(f"   Fulfilled by Dress ID: {new_request[4]}")

print("\n" + "="*60)
print("✨ Done! Now:")
print("   1. Refresh your browser (Ctrl+Shift+R)")
print("   2. You should see the fulfilled request with dress details!")
print("="*60 + "\n")

conn.close()