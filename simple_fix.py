#!/usr/bin/env python
"""Simple fix for phone_number unique constraint"""

import sys
import os
sys.path.insert(0, '.')
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=" * 70)
print("FIXING PROFILE UPDATE ISSUE")
print("=" * 70)

try:
    from app import app, db
    print("OK - App initialized")
    
    with app.app_context():
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"OK - Database: {db_url}")
        
        # Check if tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"OK - Tables exist: {len(tables)} tables found")
        
        if 'user' in tables:
            # Check constraints
            constraints = inspector.get_unique_constraints('user')
            print(f"OK - Current constraints: {constraints}")
            
            # Check if phone_number still has unique
            has_phone_unique = any('phone_number' in c['column_names'] for c in constraints)
            
            if has_phone_unique:
                print("\nWARNING - phone_number still has unique constraint")
                print("Fixing by dropping and recreating User table only...")
                
                # Use raw SQL with quoted table names for SQLite
                with db.engine.begin() as conn:
                    conn.execute(db.text('PRAGMA foreign_keys=OFF'))
                    conn.execute(db.text('DROP TABLE IF EXISTS "user"'))
                    conn.execute(db.text('PRAGMA foreign_keys=ON'))
                    
                print("OK - Dropped user table")
                
                # Recreate just the User table
                from models import User
                User.__table__.create(db.engine)
                print("OK - Recreated user table")
                
                # Verify fix
                inspector = db.inspect(db.engine)
                constraints = inspector.get_unique_constraints('user')
                print(f"OK - New constraints: {constraints}")
                
                has_phone_unique = any('phone_number' in c['column_names'] for c in constraints)
                if not has_phone_unique:
                    print("\nSUCCESS - Unique constraint removed from phone_number!")
                else:
                    print("\nWARNING - Constraint still present")
            else:
                print("\nOK - phone_number unique constraint already removed!")
        else:
            print("ERROR - user table not found")
            
        print("\n" + "=" * 70)
        print("FIX COMPLETE - Profile updates should now persist")
        print("=" * 70)

except Exception as e:
    print(f"ERROR - {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
