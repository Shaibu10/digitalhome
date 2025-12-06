#!/usr/bin/env python
"""Run migrations with detailed output."""

import sys
import os
from app import app, db
from flask_migrate import init, migrate, upgrade

with app.app_context():
    print("=" * 60)
    print("Starting migration process...")
    print("=" * 60)
    
    # Check if migrations folder exists
    if os.path.exists('migrations'):
        print("✓ Migrations folder exists")
    else:
        print("✗ Migrations folder not found - initializing...")
        init()
    
    # Try to upgrade
    print("\nRunning upgrade...")
    try:
        upgrade()
        print("✓ Upgrade completed")
    except Exception as e:
        print(f"✗ Upgrade failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Verify tables
    print("\nVerifying tables...")
    import sqlite3
    try:
        conn = sqlite3.connect('instance/digital_home.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        print(f"✓ Found {len(tables)} tables:")
        for table in tables:
            # Get column count
            cursor.execute(f"PRAGMA table_info({table[0]});")
            cols = cursor.fetchall()
            print(f"    - {table[0]} ({len(cols)} columns)")
        conn.close()
    except Exception as e:
        print(f"✗ Error checking tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Migration process complete!")
    print("=" * 60)
