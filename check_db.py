from app import app, db
import sqlite3
import os

# Check database
db_path = 'instance/digital_home.db'
if not os.path.exists(db_path):
    print("Database file doesn't exist, creating...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_review'")
exists = cursor.fetchone()

if exists:
    print("✓ product_review table exists")
    cursor.execute("PRAGMA table_info(product_review)")
    columns = cursor.fetchall()
    print(f"✓ Table has {len(columns)} columns")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("✗ product_review table does NOT exist")
    print("Creating all tables...")
    with app.app_context():
        db.create_all()
    print("✓ All tables created!")

conn.close()
