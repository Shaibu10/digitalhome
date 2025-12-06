#!/usr/bin/env python
"""Initialize database using Flask shell context"""
import os
import sys

# Remove existing database
if os.path.exists('digitalhome.db'):
    os.remove('digitalhome.db')
    print("✓ Removed existing database")

# Import all models to register them with db
os.environ.setdefault("FLASK_APP", "app.py")
os.environ.setdefault("FLASK_ENV", "development")

from app import create_app
from extensions import db

# Create app with proper context
app = create_app()

# Push app context
with app.app_context():
    # Import all models here to ensure they're registered
    from models import (
        User, Product, Category, Order, OrderItem, CartItem, 
        HeroSection, UserActivity, SystemSettings, DynamicMessage, 
        ProductReview, Payment, PaymentLog
    )
    
    print("Importing all models...")
    print(f"  - User: {User}")
    print(f"  - Order: {Order}")
    print(f"  - Payment: {Payment}")
    print(f"  - PaymentLog: {PaymentLog}")
    
    print("\nCreating all tables...")
    db.create_all()
    print("✓ Tables created")
    
    # Verify
    import sqlite3
    conn = sqlite3.connect('digitalhome.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n✓ Database now has {len(tables)} tables:")
    for table in tables:
        cursor.execute(f'PRAGMA table_info([{table[0]}])')
        cols = cursor.fetchall()
        print(f"  - {table[0]:20} ({len(cols):2} cols)")
        if table[0] in ('order', 'payment', 'payment_log'):
            print(f"    Columns: {[col[1] for col in cols]}")
    conn.close()
    
    print("\n✓ Database initialization complete!")
