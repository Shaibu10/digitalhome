#!/usr/bin/env python
"""Debug database engine issue."""

import os
from app import app, db
import sqlite3

print("Database config:")
print(f"  SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"  SQLALCHEMY_TRACK_MODIFICATIONS: {app.config['SQLALCHEMY_TRACK_MODIFICATIONS']}")

with app.app_context():
    print(f"\nEngine info:")
    print(f"  Engine: {db.engine}")
    print(f"  Engine URL: {db.engine.url}")
    print(f"  Engine name: {db.engine.name}")
    
    # Try to execute a direct CREATE TABLE
    from sqlalchemy import text
    with db.engine.connect() as conn:
        print(f"\n✓ Connection established")
        
        # Try creating a test table directly
        try:
            conn.execute(text("DROP TABLE IF EXISTS test_direct"))
            conn.commit()
            print("✓ Dropped test table")
        except:
            pass
        
        try:
            conn.execute(text("CREATE TABLE test_direct (id INTEGER PRIMARY KEY)"))
            conn.commit()
            print("✓ Created test table directly")
            
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            print(f"  Tables now: {[t[0] for t in tables]}")
        except Exception as e:
            print(f"✗ Failed to create test table: {e}")
    
    # Now try db.create_all()
    print(f"\nTrying db.create_all()...")
    print(f"  db.metadata: {db.metadata}")
    print(f"  db.metadata.tables: {list(db.metadata.tables.keys())}")
    
    db.create_all()
    print("✓ db.create_all() completed")
    
    # Check results
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        print(f"  Tables after create_all: {[t[0] for t in tables]}")
