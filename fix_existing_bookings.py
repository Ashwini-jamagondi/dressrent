"""
Fix existing Saree bookings to fulfill the request
Run: python fix_existing_bookings.py
"""

import sqlite3

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

print("\n" + "="*60)
print("🔧 FIXING EXISTING SAREE BOOKINGS")
print("="*60)

# Get all Saree bookings by Aishu
cursor.execute("""
    SELECT b.id, b.dress_id, b.renter_id, p.name, u.username
    FROM bookings b
    JOIN products p ON b.dress_id = p.id
    JOIN users u ON b.renter_id = u.id
    WHERE (p.name LIKE '%Saree%' OR p.category LIKE '%Saree%')
    AND u.username = 'Aishu'
    ORDER BY b.created_at DESC
""")

bookings = cursor.fetchall()
print(f"\n📦 Found {len(bookings)} Saree booking(s) by Aishu:")
for booking in bookings:
    print(f"   Booking #{booking[0]}: {booking[3]} (Dress ID: {booking[1]})")

if not bookings:
    print("❌ No Saree bookings found!")
    conn.close()
    exit()

# Get the most recent booking
latest_booking = bookings[0]
booking_id, dress_id, renter_id, dress_name, username = latest_booking

print(f"\n🎯 Using latest booking:")
print(f"   Booking ID: {booking_id}")
print(f"   Dress ID: {dress_id}")
print(f"   Renter: {username} (ID: {renter_id})")

# Find matching request
cursor.execute("""
    SELECT id, dress_type, size, status
    FROM requests
    WHERE user_id = ?
    AND dress_type LIKE '%Saree%'
    ORDER BY created_at DESC
    LIMIT 1
""", (renter_id,))

request = cursor.fetchone()

if not request:
    print("\n❌ No Saree request found for this user!")
    conn.close()
    exit()

request_id, dress_type, size, status = request
print(f"\n📝 Found matching request:")
print(f"   Request ID: {request_id}")
print(f"   Dress Type: {dress_type}")
print(f"   Size: {size}")
print(f"   Current Status: {status}")

# Update the request
if status == 'fulfilled':
    print("\n✅ Request already fulfilled!")
else:
    print(f"\n🔄 Updating request to fulfilled...")
    cursor.execute("""
        UPDATE requests
        SET status = 'fulfilled',
            fulfilled_by_dress_id = ?
        WHERE id = ?
    """, (dress_id, request_id))
    
    conn.commit()
    
    # Verify
    cursor.execute("""
        SELECT status, fulfilled_by_dress_id
        FROM requests
        WHERE id = ?
    """, (request_id,))
    
    updated = cursor.fetchone()
    print(f"   ✅ Status: {updated[0]}")
    print(f"   ✅ Fulfilled by Dress ID: {updated[1]}")

print("\n" + "="*60)
print("✨ Done! Refresh your 'My Requests' page!")
print("="*60 + "\n")

conn.close()