#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create database tables
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

echo "Build completed successfully!"