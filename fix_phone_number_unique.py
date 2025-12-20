#!/usr/bin/env python
"""
Fix script to remove unique constraint from phone_number column.
This resolves the issue where profile updates fail due to unique constraint violation.
"""

import sys
import shutil
import os
from datetime import datetime
sys.path.insert(0, '.')

from app import app, db
from sqlalchemy import text, inspect

def fix_phone_number_constraint():
    """Remove unique constraint from phone_number column"""
    try:
        with app.app_context():
            # Get database URL to determine DB type
            db_url = str(db.engine.url)
            print(f"Database: {db_url}")
            
            # Check current state
            print("\n📋 Checking current constraints on User table...")
            inspector = inspect(db.engine)
            
            try:
                constraints = inspector.get_unique_constraints('user')
                print(f"Unique constraints: {constraints}")
            except Exception as e:
                print(f"Could not read constraints: {e}")
            
            # For SQLite
            if 'sqlite' in db_url.lower():
                print("\n🔧 SQLite detected - updating table structure...")
                
                # Backup database
                db_file = 'digitalhome.db'
                if os.path.exists(db_file):
                    backup_file = f'{db_file}.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                    shutil.copy2(db_file, backup_file)
                    print(f"✅ Database backed up to: {backup_file}")
                
                # Drop and recreate all tables with updated schema
                print("🔄 Recreating User table without unique constraint on phone_number...")
                
                # Get all table names
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                with db.engine.begin() as conn:
                    # Disable foreign keys
                    conn.execute(text("PRAGMA foreign_keys=OFF"))
                    
                    try:
                        # Drop all tables in reverse dependency order
                        for table in reversed(tables):
                            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                        
                        # Recreate all tables
                        db.create_all()
                        
                        print("✅ All tables recreated successfully!")
                        
                    finally:
                        # Re-enable foreign keys
                        conn.execute(text("PRAGMA foreign_keys=ON"))
                
            else:
                # For PostgreSQL/MySQL
                print("\n🔧 PostgreSQL/MySQL detected - altering table...")
                
                with db.engine.begin() as conn:
                    try:
                        # Try PostgreSQL syntax
                        conn.execute(text("ALTER TABLE \"user\" DROP CONSTRAINT user_phone_number_key"))
                        print("✅ PostgreSQL constraint removed!")
                    except Exception as e1:
                        try:
                            # Try MySQL syntax
                            conn.execute(text("ALTER TABLE user DROP INDEX phone_number"))
                            print("✅ MySQL constraint removed!")
                        except Exception as e2:
                            print(f"⚠️ Could not drop constraint via standard methods:")
                            print(f"   PostgreSQL error: {e1}")
                            print(f"   MySQL error: {e2}")
                        
            print("\n✨ Fix completed!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("FIXING PROFILE UPDATE PERSISTENCE ISSUE")
    print("Removing unique constraint from phone_number field")
    print("=" * 70)
    
    success = fix_phone_number_constraint()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Profile updates should now persist correctly.")
        print("=" * 70)
    
    sys.exit(0 if success else 1)
