"""
Check and fix the requests table
Run: python check_and_fix.py
"""

import sqlite3

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

print("\n" + "="*60)
print("🔍 CHECKING DATABASE")
print("="*60)

# Check columns
cursor.execute("PRAGMA table_info(requests)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

print("\n📋 Columns in requests table:")
for col in column_names:
    print(f"   - {col}")

# Check if fulfilled_by_dress_id exists
has_fulfilled_column = 'fulfilled_by_dress_id' in column_names

if not has_fulfilled_column:
    print("\n⚠️  Column 'fulfilled_by_dress_id' is MISSING!")
    print("   Adding column now...")
    cursor.execute("ALTER TABLE requests ADD COLUMN fulfilled_by_dress_id INTEGER")
    conn.commit()
    print("   ✅ Column added!")
else:
    print("\n✅ Column 'fulfilled_by_dress_id' exists")

# Check Saree requests
print("\n📝 Saree Requests:")
cursor.execute("""
    SELECT id, dress_type, status, fulfilled_by_dress_id, user_id
    FROM requests 
    WHERE dress_type LIKE '%Saree%'
""")

requests = cursor.fetchall()
if requests:
    for req in requests:
        print(f"   Request #{req[0]}: {req[1]}")
        print(f"      Status: {req[2]}")
        print(f"      Fulfilled by dress ID: {req[3]}")
        print(f"      User ID: {req[4]}")
else:
    print("   ❌ No Saree requests found!")

# Update to fulfilled if needed
if requests:
    print("\n🔧 Updating request to fulfilled...")
    cursor.execute("""
        UPDATE requests 
        SET status = 'fulfilled', 
            fulfilled_by_dress_id = 5
        WHERE dress_type LIKE '%Saree%'
    """)
    
    rows_updated = cursor.rowcount
    conn.commit()
    
    print(f"   ✅ Updated {rows_updated} request(s)")
    
    # Verify
    cursor.execute("""
        SELECT id, dress_type, status, fulfilled_by_dress_id
        FROM requests 
        WHERE dress_type LIKE '%Saree%'
    """)
    
    updated = cursor.fetchone()
    print(f"\n✅ VERIFIED:")
    print(f"   Request #{updated[0]}: {updated[1]}")
    print(f"   Status: {updated[2]}")
    print(f"   Fulfilled by dress ID: {updated[3]}")

print("\n" + "="*60)
print("✨ Done! Now refresh your browser with Ctrl+Shift+R")
print("="*60 + "\n")

conn.close()