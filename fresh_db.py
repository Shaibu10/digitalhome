#!/usr/bin/env python
"""Fresh database initialization - creates tables only"""

import os
import sys

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Delete old database if it exists
if os.path.exists('digitalhome.db'):
    os.remove('digitalhome.db')
    print("✓ Removed old database")

# Import app and db
from app import app, db

# Create all tables
print("Creating database tables...")
with app.app_context():
    db.create_all()
    print("✓ Database tables created successfully!")
    
    # Verify tables
    import sqlite3
    conn = sqlite3.connect('digitalhome.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("\nCreated tables:")
    for table in tables:
        print(f"  - {table[0]}")
        # Show columns for user table
        if table[0] == 'user':
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print("    Columns:")
            for col in columns:
                print(f"      - {col[1]} ({col[2]})")
    
    conn.close()

print("\n✓ Database initialized! You can now run the app.")
