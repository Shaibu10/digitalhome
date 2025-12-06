#!/usr/bin/env python
"""Initialize the database by running Flask app context"""

from app import app, db

if __name__ == '__main__':
    print("Initializing database...")
    with app.app_context():
        # Create all tables based on models
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # List all tables
        import sqlite3
        conn = sqlite3.connect('digitalhome.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("\nCreated tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        conn.close()
