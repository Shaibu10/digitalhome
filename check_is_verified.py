#!/usr/bin/env python
"""Check if is_verified column exists in user table."""

import sqlite3

# Try both database names
for db_name in ['instance/digitalhome.db', 'instance/digital_home.db']:
    print(f"\nChecking {db_name}:")
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(user);")
        columns = cursor.fetchall()
        
        if not columns:
            print("  No user table found")
            conn.close()
            continue
        
        print("  User table columns:")
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            print(f"    - {col_name} ({col_type})")

        has_is_verified = any(col[1] == 'is_verified' for col in columns)
        has_verified_at = any(col[1] == 'verified_at' for col in columns)

        print(f"\n  ✓ has is_verified: {has_is_verified}")
        print(f"  ✓ has verified_at: {has_verified_at}")

        if has_is_verified and has_verified_at:
            print("\n  ✅ All email verification columns present!")
        else:
            print("\n  ⚠️ Missing email verification columns")
        
        conn.close()
    except Exception as e:
        print(f"  Error: {e}")
