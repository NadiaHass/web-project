#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Initializing database schema and data..."
psql $DATABASE_URL -f init_db.sql

echo "Running additional migrations..."
psql $DATABASE_URL -f migration_add_approval_columns.sql

echo "Seeding user accounts..."
python seed_users.py

echo "Build completed successfully!"
