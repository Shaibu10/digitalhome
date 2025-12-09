#!/usr/bin/env python
"""Initialize the database by running Flask app context"""

import os
import sys
from app import app, db

def init_database():
    """Initialize database tables."""
    print("=" * 60)
    print("Starting Database Initialization")
    print("=" * 60)
    
    with app.app_context():
        print(f"App context: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
        
        try:
            # Create all tables based on models
            print("Creating all tables from models...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # List all tables
            import sqlite3
            db_path = app.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///digitalhome.db').replace('sqlite:///', '')
            print(f"Database location: {db_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"\n✅ Total tables created: {len(tables)}")
            print("\nTable list:")
            for table in tables:
                print(f"  ✓ {table[0]}")
            
            conn.close()
            print("\n" + "=" * 60)
            print("Database initialization completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error during database initialization: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    init_database()
