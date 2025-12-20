#!/usr/bin/env python
"""Direct database fix without importing app"""

import sqlite3
import os
from pathlib import Path

print("=" * 70)
print("FIXING PROFILE UPDATE ISSUE - DIRECT DB FIX")
print("=" * 70)

# Find database
db_paths = [
    'digitalhome.db',
    'instance/digitalhome.db',
]

db_path = None
for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("ERROR: Database file not found!")
    print(f"Checked: {db_paths}")
    exit(1)

print(f"\nDatabase: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get current schema
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    print(f"\nUser table columns: {len(columns)} columns")
    
    # Check unique constraints  
    cursor.execute("PRAGMA index_list(user)")
    indexes = cursor.fetchall()
    print(f"Unique indexes on user table: {len(indexes)} indexes")
    for idx in indexes:
        if idx[5] == 1:  # unique index
            print(f"  - {idx[1]} (unique)")
            
            # Get index columns
            cursor.execute(f"PRAGMA index_info({idx[1]})")
            index_cols = cursor.fetchall()
            for col in index_cols:
                print(f"    -> column: {col[2]}")
    
    # Check if phone_number has unique constraint
    
    has_phone_unique = False
    phone_index_name = None
    for idx in indexes:
        if 'phone' in idx[1].lower() and idx[5] == 1:
            has_phone_unique = True
            phone_index_name = idx[1]
            break
    
    if has_phone_unique:
        print(f"\nWARNING: Found unique index on phone_number: {phone_index_name}")
        print("Removing constraint...")
        
        # SQLite doesn't allow dropping constraints directly
        # Must recreate table without the constraint
        print("\nRecreating user table without phone_number unique constraint...")
        
        cursor.execute("PRAGMA foreign_keys=OFF")
        
        # Create new table
        cursor.execute("""
            CREATE TABLE user_new AS 
            SELECT * FROM user
        """)
        print("  - Created temporary table")
        
        # Drop old table
        cursor.execute("DROP TABLE user")
        print("  - Dropped old user table")
        
        # Rename new table
        cursor.execute("ALTER TABLE user_new RENAME TO user")
        print("  - Renamed temporary table to user")
        
        cursor.execute("PRAGMA foreign_keys=ON")
        
        conn.commit()
        print("\nSUCCESS - Unique constraint removed!")
        print("Database changes committed.")
    else:
        print("\nOK - phone_number constraint already removed or doesn't exist")
    
    conn.close()
    print("\n" + "=" * 70)
    print("FIX COMPLETE - Profile updates should now persist")
    print("=" * 70)
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
