#!/usr/bin/env python
"""
Script to add phone_number column to user table if it doesn't exist
"""
import sqlite3
import os

db_path = 'instance/digitalhome.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Try to add the column
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN phone_number VARCHAR(20);")
        print("✅ phone_number column added successfully")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("✅ phone_number column already exists")
        else:
            raise
    
    conn.commit()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)
