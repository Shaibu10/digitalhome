#!/usr/bin/env python
"""Test database connection."""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

print(f"Database URI: {Config.SQLALCHEMY_DATABASE_URI}")
print(f"Database path: {Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')}")

# Create app
app = Flask(__name__)
app.config.from_object(Config)

# Create DB
db = SQLAlchemy(app)

print(f"\nApp created: {app}")
print(f"DB created: {db}")

# Check if we can create tables
with app.app_context():
    print(f"DB engine: {db.engine}")
    print("\n--- In app context ---")
    print(f"Engine URL: {db.engine.url}")
    
    # Try to execute a simple command
    with db.engine.connect() as conn:
        print("✓ Connected to database")
        # Create a test table
        from sqlalchemy import text
        conn.execute(text("CREATE TABLE test_table (id INTEGER PRIMARY KEY)"))
        conn.commit()
        print("✓ Created test table")
        
        # Check tables
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        print(f"✓ Tables: {tables}")
