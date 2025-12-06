#!/usr/bin/env python
"""Add shipping-related columns to user and order tables"""

import sqlite3
from datetime import datetime

try:
    conn = sqlite3.connect('digitalhome.db')
    cursor = conn.cursor()
    
    print("Adding shipping columns to user table...")
    
    # Add columns to user table
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN first_name VARCHAR(100)")
        print("✓ Added first_name to user")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ first_name already exists in user")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN last_name VARCHAR(100)")
        print("✓ Added last_name to user")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ last_name already exists in user")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN address TEXT")
        print("✓ Added address to user")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ address already exists in user")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN city VARCHAR(100)")
        print("✓ Added city to user")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ city already exists in user")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN postal_code VARCHAR(20)")
        print("✓ Added postal_code to user")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ postal_code already exists in user")
        else:
            raise
    
    print("\nAdding shipping columns to order table...")
    
    # Add columns to order table
    try:
        cursor.execute("ALTER TABLE \"order\" ADD COLUMN shipping_first_name VARCHAR(100)")
        print("✓ Added shipping_first_name to order")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ shipping_first_name already exists in order")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE \"order\" ADD COLUMN shipping_last_name VARCHAR(100)")
        print("✓ Added shipping_last_name to order")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ shipping_last_name already exists in order")
        else:
            raise
    
    conn.commit()
    
    # Verify columns exist
    cursor.execute("PRAGMA table_info(user)")
    user_columns = [col[1] for col in cursor.fetchall()]
    
    cursor.execute("PRAGMA table_info(\"order\")")
    order_columns = [col[1] for col in cursor.fetchall()]
    
    print("\nVerification - User table columns:")
    required_user_cols = ['first_name', 'last_name', 'address', 'city', 'postal_code']
    for col in required_user_cols:
        print(f"  - {col}: {'✓ EXISTS' if col in user_columns else '✗ MISSING'}")
    
    print("\nVerification - Order table columns:")
    required_order_cols = ['shipping_first_name', 'shipping_last_name']
    for col in required_order_cols:
        print(f"  - {col}: {'✓ EXISTS' if col in order_columns else '✗ MISSING'}")
    
    conn.close()
    print("\n✓ All shipping columns added successfully!")

except Exception as e:
    print(f"✗ Error adding columns: {e}")
    import traceback
    traceback.print_exc()
