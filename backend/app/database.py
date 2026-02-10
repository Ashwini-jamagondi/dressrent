from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"🔍 DATABASE_URL found: {bool(DATABASE_URL)}")

# Fix Render PostgreSQL URL (postgres:// -> postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"✅ Using PostgreSQL: {DATABASE_URL[:50]}...")

# Fallback to SQLite for local development
if not DATABASE_URL or DATABASE_URL == "":
    DATABASE_URL = "sqlite:///./ecommerce.db"
    print("⚠️ Using SQLite (local development)")
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    print(f"✅ Connecting to PostgreSQL...")
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=True  # Enable SQL logging for debugging
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables on startup
def init_db():
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")