#!/usr/bin/env python
"""Initialize the database with migrations."""

from app import app, db
from flask_migrate import upgrade

with app.app_context():
    print("Running migrations...")
    upgrade()
    print("✅ Migrations complete!")
    
    # Verify tables
    import sqlite3
    conn = sqlite3.connect('instance/digital_home.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"\nTables created: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
    conn.close()
