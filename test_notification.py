"""
Test script to manually create notification for Aishu
Run: python test_notification.py
"""

import sqlite3
from datetime import datetime

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

print("\n" + "="*60)
print("🔔 TESTING NOTIFICATION SYSTEM")
print("="*60)

# Get Aishu's user ID
cursor.execute("SELECT id, username FROM users WHERE username = 'Aishu'")
aishu = cursor.fetchone()

if not aishu:
    print("❌ Aishu not found!")
    conn.close()
    exit()

aishu_id = aishu[0]
print(f"\n✅ Found Aishu - User ID: {aishu_id}")

# Get Aishu's open requests
cursor.execute("""
    SELECT id, dress_type, size
    FROM requests
    WHERE user_id = ? AND status = 'open'
""", (aishu_id,))

requests = cursor.fetchall()
print(f"\n📝 Aishu's Open Requests: {len(requests)}")
for req in requests:
    print(f"   Request #{req[0]}: {req[1]} (Size: {req[2]})")

# Get recently uploaded dresses (not by Aishu)
cursor.execute("""
    SELECT p.id, p.name, p.category, p.size, p.owner_id, u.username
    FROM products p
    JOIN users u ON p.owner_id = u.id
    WHERE p.owner_id != ?
    ORDER BY p.id DESC
    LIMIT 5
""", (aishu_id,))

recent_dresses = cursor.fetchall()
print(f"\n👗 Recent Dresses (not by Aishu): {len(recent_dresses)}")
for dress in recent_dresses:
    print(f"   Dress #{dress[0]}: {dress[1]} (Category: {dress[2]}, Owner: {dress[5]})")

# Find matches
print(f"\n🔍 Looking for matches...")
matches = []

for request in requests:
    request_id, dress_type, size = request
    
    for dress in recent_dresses:
        dress_id, dress_name, category, dress_size, owner_id, owner_name = dress
        
        # Check if matches
        if dress_type.lower() in dress_name.lower() or dress_type.lower() in category.lower():
            print(f"   ✅ MATCH: Request '{dress_type}' matches Dress '{dress_name}'")
            matches.append({
                'request_id': request_id,
                'dress_id': dress_id,
                'dress_name': dress_name,
                'owner_name': owner_name
            })

if matches:
    print(f"\n🎉 Found {len(matches)} match(es)! Creating notifications...")
    
    for match in matches:
        # Check if notification already exists
        cursor.execute("""
            SELECT id FROM notifications
            WHERE user_id = ? AND related_id = ? AND request_id = ?
        """, (aishu_id, match['dress_id'], match['request_id']))
        
        existing = cursor.fetchone()
        
        if existing:
            print(f"   ⚠️ Notification already exists for dress {match['dress_id']}")
        else:
            # Create notification
            cursor.execute("""
                INSERT INTO notifications
                (user_id, type, title, message, related_id, request_id, is_read, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                aishu_id,
                "dress_match",
                "New Dress Match!",
                f"'{match['dress_name']}' from {match['owner_name']} matches your request!",
                match['dress_id'],
                match['request_id'],
                0
            ))
            
            conn.commit()
            print(f"   ✅ Created notification for dress '{match['dress_name']}'")
else:
    print(f"   ℹ️ No matches found")

print("\n" + "="*60)
print("✨ Done! Refresh Aishu's page to see notifications")
print("="*60 + "\n")

conn.close()