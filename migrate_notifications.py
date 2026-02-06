# Save as: migrate_notifications.py
# Run with: python migrate_notifications.py

import sqlite3
import os

# Path to your database
DB_PATH = "ecommerce.db"  # Update this if your database is in a different location

def migrate_notifications_table():
    """Add missing columns to notifications table"""
    
    print("🔄 Starting migration...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        print("Please update DB_PATH in the script")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        if not cursor.fetchone():
            print("❌ Notifications table doesn't exist. Creating from scratch...")
            cursor.execute("""
                CREATE TABLE notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    message TEXT NOT NULL,
                    related_id INTEGER,
                    request_id INTEGER,
                    is_read BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (request_id) REFERENCES dress_requests(id)
                )
            """)
            print("✅ Created notifications table")
            conn.commit()
            conn.close()
            return
        
        # Get current columns
        cursor.execute("PRAGMA table_info(notifications)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Current columns: {columns}")
        
        # Add missing columns
        columns_to_add = []
        
        if 'type' not in columns:
            columns_to_add.append(("type", "VARCHAR(50) NOT NULL DEFAULT 'message'"))
        
        if 'title' not in columns:
            columns_to_add.append(("title", "VARCHAR(200) NOT NULL DEFAULT 'Notification'"))
        
        if 'related_id' not in columns:
            columns_to_add.append(("related_id", "INTEGER"))
        
        if not columns_to_add:
            print("✅ All columns already exist!")
            conn.close()
            return
        
        # Add each missing column
        for col_name, col_def in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE notifications ADD COLUMN {col_name} {col_def}")
                print(f"✅ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"⚠️  Column {col_name} might already exist: {e}")
        
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(notifications)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"\n📋 Updated columns: {new_columns}")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_notifications_table()