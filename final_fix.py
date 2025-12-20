#!/usr/bin/env python
"""Direct database fix - checking the right database"""

import sqlite3
import os

print("=" * 70)
print("FIXING PROFILE UPDATE ISSUE - DIRECT DB FIX")
print("=" * 70)

db_path = 'instance/digitalhome.db'

if not os.path.exists(db_path):
    print(f"ERROR: Database file not found at {db_path}!")
    exit(1)

print(f"\nDatabase: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")
    
    # Get user table schema
    if any(t[0] == 'user' for t in tables):
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        print(f"\nUser table columns ({len(columns)} columns):")
        for col in columns:
            print(f"  {col[1]}: {col[2]}")
        
        # Check indexes on user table
        cursor.execute("PRAGMA index_list(user)")
        indexes = cursor.fetchall()
        print(f"\nIndexes on user table:")
        has_phone_unique = False
        for idx in indexes:
            if len(idx) > 5:
                is_unique = "UNIQUE" if idx[5] == 1 else "regular"
                print(f"  - {idx[1]}: {is_unique}")
                
                cursor.execute(f"PRAGMA index_info({idx[1]})")
                cols = cursor.fetchall()
                for col in cols:
                    col_name = col[2]
                    print(f"      column: {col_name}")
                    if col_name == 'phone_number':
                        has_phone_unique = True
        
        if has_phone_unique:
            print("\n" + "=" * 70)
            print("FOUND: phone_number has a unique constraint")
            print("FIXING: Recreating user table without unique constraint...")
            print("=" * 70)
            
            cursor.execute("PRAGMA foreign_keys=OFF")
            
            # Create new table with same schema but no unique on phone_number
            cursor.execute("""
                CREATE TABLE user_new (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    phone_number VARCHAR(20),
                    password_hash VARCHAR(255),
                    is_admin BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    is_verified BOOLEAN DEFAULT 0,
                    verified_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    address TEXT,
                    city VARCHAR(100),
                    postal_code VARCHAR(20)
                )
            """)
            print("  - Created new user table without phone_number unique constraint")
            
            # Copy data
            cursor.execute("""
                INSERT INTO user_new
                SELECT * FROM user
            """)
            print(f"  - Copied data from old table")
            
            # Drop old table
            cursor.execute("DROP TABLE user")
            print("  - Dropped old user table")
            
            # Rename new table
            cursor.execute("ALTER TABLE user_new RENAME TO user")
            print("  - Renamed new table to user")
            
            cursor.execute("PRAGMA foreign_keys=ON")
            conn.commit()
            
            print("\n" + "=" * 70)
            print("SUCCESS - Unique constraint removed from phone_number!")
            print("=" * 70)
        else:
            print("\nOK - phone_number does not have a unique constraint")
    else:
        print("\nERROR: user table not found")
    
    conn.close()
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
