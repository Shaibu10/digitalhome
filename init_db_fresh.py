#!/usr/bin/env python
"""Initialize database with all tables."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def init_database():
    """Initialize database from models."""
    app = create_app()
    
    with app.app_context():
        print("\n🔄 Initializing database from models...")
        
        # Drop all existing tables
        print("🗑️  Dropping existing tables...")
        db.drop_all()
        
        # Create all tables from models
        print("📝 Creating tables from models...")
        db.create_all()
        
        print("✅ Database initialized successfully!")
        print("\nTables created:")
        for table in db.metadata.sorted_tables:
            print(f"  ✓ {table.name}")
        
        return True

if __name__ == '__main__':
    init_database()
