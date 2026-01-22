#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run SQL migration
psql $DATABASE_URL -f migration_add_approval_columns.sql

# Run seed script
python seed_users.py
