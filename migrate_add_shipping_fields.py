#!/usr/bin/env python
"""Migrate existing database to add shipping columns"""

import sqlite3
import os

db_path = 'digitalhome.db'

if not os.path.exists(db_path):
    print(f"✗ Database file not found: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Checking existing tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Found tables: {tables}")
    
    if 'user' not in tables:
        print("✗ user table not found")
        exit(1)
    
    print("\n=== Adding columns to user table ===")
    
    # List of columns to add with their definitions
    columns_to_add = [
        ('first_name', 'VARCHAR(100)'),
        ('last_name', 'VARCHAR(100)'),
        ('address', 'TEXT'),
        ('city', 'VARCHAR(100)'),
        ('postal_code', 'VARCHAR(20)')
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
            conn.commit()
            print(f"✓ Added {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"✓ {col_name} already exists")
            else:
                print(f"✗ Error adding {col_name}: {e}")
                raise
    
    print("\n=== Adding columns to order table ===")
    
    if 'order' not in tables:
        print("✗ order table not found")
        exit(1)
    
    order_columns_to_add = [
        ('shipping_first_name', 'VARCHAR(100)'),
        ('shipping_last_name', 'VARCHAR(100)')
    ]
    
    for col_name, col_type in order_columns_to_add:
        try:
            cursor.execute(f'ALTER TABLE "order" ADD COLUMN {col_name} {col_type}')
            conn.commit()
            print(f"✓ Added {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"✓ {col_name} already exists")
            else:
                print(f"✗ Error adding {col_name}: {e}")
                raise
    
    # Verify columns were added
    print("\n=== Verification ===")
    cursor.execute("PRAGMA table_info(user)")
    user_cols = [row[1] for row in cursor.fetchall()]
    
    cursor.execute('PRAGMA table_info("order")')
    order_cols = [row[1] for row in cursor.fetchall()]
    
    print("User table columns:")
    for col in ['first_name', 'last_name', 'address', 'city', 'postal_code']:
        status = '✓' if col in user_cols else '✗'
        print(f"  {status} {col}")
    
    print("\nOrder table columns:")
    for col in ['shipping_first_name', 'shipping_last_name']:
        status = '✓' if col in order_cols else '✗'
        print(f"  {status} {col}")
    
    conn.close()
    print("\n✓ Migration completed successfully!")

except Exception as e:
    print(f"\n✗ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
