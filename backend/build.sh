#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating database tables..."
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

echo "Running migrations..."
psql $DATABASE_URL -f migration_add_approval_columns.sql 2>/dev/null || echo "Migration already applied"

echo "Seeding initial data..."
python seed_data.py

echo "Seeding user accounts..."
python seed_users.py

echo "Build completed successfully!"
