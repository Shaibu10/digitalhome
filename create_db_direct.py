#!/usr/bin/env python
"""Create database directly."""

import os
import sys

# Clean up old database
db_path = 'instance/digital_home.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print("✓ Removed old database")

# Import after cleanup
from app import app, db
from models import User, Category, Product, Order, OrderItem, CartItem, HeroSection, UserActivity, EmailToken, TokenRateLimit

print(f"\nDatabase config:")
print(f"  URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    print(f"\nCreating tables...")
    db.create_all()
    print(f"✓ Created tables")
    
    # Verify with direct SQL
    import sqlite3
    # Find the actual database file
    for f in os.listdir('instance'):
        if f.endswith('.db'):
            db_file = os.path.join('instance', f)
            print(f"\nChecking {db_file}...")
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = cursor.fetchall()
            print(f"  Tables: {len(tables)}")
            for t in tables:
                cursor.execute(f"PRAGMA table_info({t[0]});")
                cols = cursor.fetchall()
                print(f"    - {t[0]} ({len(cols)} cols)")
            conn.close()

print("\n✓ Complete")
