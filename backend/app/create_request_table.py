# create_request_table.py
from backend.app.database import engine, Base
from backend.app.models import Request  # Import to register the model

print("Creating Request table...")
Base.metadata.create_all(bind=engine)
print("✅ Request table created successfully!")