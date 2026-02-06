"""
Run this script to manually fulfill existing Saree request
Place in your project root directory and run: python fix_existing_request.py
"""

import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

print("\n" + "="*60)
print("🔧 FIXING EXISTING REQUEST STATUS")
print("="*60)

# Find the Saree booking
cursor.execute("""
    SELECT b.id, b.dress_id, b.renter_id, p.name, p.category 
    FROM bookings b
    JOIN products p ON b.dress_id = p.id
    WHERE p.name LIKE '%Saree%' OR p.category LIKE '%Saree%'
    ORDER BY b.created_at DESC
    LIMIT 1
""")

booking = cursor.fetchone()

if not booking:
    print("❌ No Saree booking found")
    conn.close()
    exit()

booking_id, dress_id, renter_id, dress_name, dress_category = booking
print(f"\n✅ Found Booking:")
print(f"   ID: {booking_id}")
print(f"   Dress: {dress_name}")
print(f"   Category: {dress_category}")
print(f"   Dress ID: {dress_id}")
print(f"   Renter ID: {renter_id}")

# Find matching open request
cursor.execute("""
    SELECT id, dress_type, status 
    FROM requests 
    WHERE user_id = ? 
    AND dress_type LIKE '%Saree%'
    AND status = 'open'
    ORDER BY created_at DESC
    LIMIT 1
""", (renter_id,))

request = cursor.fetchone()

if not request:
    print("\n❌ No open Saree request found for this user")
    conn.close()
    exit()

request_id, dress_type, current_status = request
print(f"\n✅ Found Request:")
print(f"   ID: {request_id}")
print(f"   Dress Type: {dress_type}")
print(f"   Current Status: {current_status}")

# Update the request
cursor.execute("""
    UPDATE requests 
    SET status = 'fulfilled', 
        fulfilled_by_dress_id = ?
    WHERE id = ?
""", (dress_id, request_id))

conn.commit()

# Verify update
cursor.execute("""
    SELECT status, fulfilled_by_dress_id 
    FROM requests 
    WHERE id = ?
""", (request_id,))

updated = cursor.fetchone()
print(f"\n✅ Request Updated Successfully!")
print(f"   New Status: {updated[0]}")
print(f"   Fulfilled By Dress ID: {updated[1]}")

print("\n" + "="*60)
print("✨ Now refresh your 'My Requests' page to see the fulfilled request!")
print("="*60 + "\n")

conn.close()