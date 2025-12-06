#!/usr/bin/env python
"""Create Payment and PaymentLog tables directly in database"""

from app import app, db
from models import Payment, PaymentLog

with app.app_context():
    # Create tables
    db.create_all()
    
    # Check if tables were created
    import sqlite3
    conn = sqlite3.connect('digitalhome.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('payment', 'payment_log')")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("Payment table creation status:")
    print(f"  - payment: {'✓ CREATED' if 'payment' in tables else '✗ FAILED'}")
    print(f"  - payment_log: {'✓ CREATED' if 'payment_log' in tables else '✗ FAILED'}")
    
    if 'payment' in tables:
        cursor.execute("PRAGMA table_info(payment)")
        print("\nPayment table columns:")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    print("\n✓ Database tables created successfully!")
