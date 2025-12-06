#!/usr/bin/env python
"""Check if Payment tables exist in database"""

import sqlite3

conn = sqlite3.connect('digitalhome.db')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print("Existing tables:")
for table in sorted(tables):
    print(f"  - {table}")

print("\nPayment tables status:")
print(f"  - payment: {'✓ EXISTS' if 'payment' in tables else '✗ MISSING'}")
print(f"  - payment_log: {'✓ EXISTS' if 'payment_log' in tables else '✗ MISSING'}")

if 'payment' in tables:
    cursor.execute("PRAGMA table_info(payment)")
    print("\nPayment table columns:")
    for col in cursor.fetchall():
        print(f"  - {col[1]} ({col[2]})")

conn.close()
