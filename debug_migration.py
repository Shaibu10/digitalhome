#!/usr/bin/env python
"""Debug migration issues."""

import os
import sqlite3
from app import app

print("Database path:", app.config['SQLALCHEMY_DATABASE_URI'])
print("Instance folder exists:", os.path.exists('instance'))
print("Database file exists:", os.path.exists('instance/digital_home.db'))

if os.path.exists('instance/digital_home.db'):
    print("\nDatabase file info:")
    print(f"Size: {os.path.getsize('instance/digital_home.db')} bytes")
    
    conn = sqlite3.connect('instance/digital_home.db')
    cursor = conn.cursor()
    
    # Check alembic_version table
    try:
        cursor.execute("SELECT version_num FROM alembic_version;")
        versions = cursor.fetchall()
        print(f"Alembic versions: {versions}")
    except Exception as e:
        print(f"Alembic version check failed: {e}")
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    conn.close()
else:
    print("\nDatabase file not created yet")

# Now try to create the app context and check extensions
with app.app_context():
    print("\nChecking Flask-Migrate extension:")
    if 'migrate' in app.extensions:
        print("✓ migrate extension found")
    else:
        print("✗ migrate extension NOT found")
    
    print("\nChecking database configuration:")
    from app import db
    print(f"Database: {db}")
    print(f"Database engine: {db.engine}")
    print(f"Database URL: {db.engine.url}")
