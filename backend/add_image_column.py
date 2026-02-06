from app.database import engine
from sqlalchemy import text

def add_image_column():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR"))
            conn.commit()
            print("✅ Added image_url column to products table")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_image_column()