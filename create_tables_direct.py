#!/usr/bin/env python
"""Create Payment and PaymentLog tables with detailed error reporting"""

import sqlite3
from datetime import datetime

# Direct SQL to create tables
create_payment_sql = """
CREATE TABLE IF NOT EXISTS payment (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    customer_email VARCHAR(120) NOT NULL,
    customer_phone VARCHAR(20),
    amount FLOAT NOT NULL,
    currency VARCHAR(3) DEFAULT 'GHS',
    paystack_reference VARCHAR(100) UNIQUE NOT NULL,
    paystack_authorization_code VARCHAR(100),
    paystack_customer_id INTEGER,
    payment_method VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    status_reason VARCHAR(255),
    initiated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY(order_id) REFERENCES \"order\"(id)
)
"""

create_payment_log_sql = """
CREATE TABLE IF NOT EXISTS payment_log (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    payment_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(payment_id) REFERENCES payment(id)
)
"""

try:
    conn = sqlite3.connect('digitalhome.db')
    cursor = conn.cursor()
    
    # Create payment table
    print("Creating payment table...")
    cursor.execute(create_payment_sql)
    print("✓ Payment table created")
    
    # Create payment_log table
    print("Creating payment_log table...")
    cursor.execute(create_payment_log_sql)
    print("✓ Payment log table created")
    
    conn.commit()
    
    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('payment', 'payment_log')")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("\nVerification:")
    print(f"  - payment table: {'✓ EXISTS' if 'payment' in tables else '✗ MISSING'}")
    print(f"  - payment_log table: {'✓ EXISTS' if 'payment_log' in tables else '✗ MISSING'}")
    
    # Show column info
    if 'payment' in tables:
        cursor.execute("PRAGMA table_info(payment)")
        print("\nPayment table columns:")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    print("\n✓ Payment tables created successfully!")

except Exception as e:
    print(f"✗ Error creating tables: {e}")
    import traceback
    traceback.print_exc()
