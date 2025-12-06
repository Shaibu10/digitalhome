#!/usr/bin/env python
"""Manually execute migrations with proper transaction handling."""

import os
import sqlite3
from app import app

# Remove the empty database file
db_path = 'instance/digital_home.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print("✓ Removed old database file")

# Create a fresh connection with isolation_level set properly
conn = sqlite3.connect(db_path)
conn.isolation_level = None  # Autocommit mode
cursor = conn.cursor()

print("Creating alembic_version table...")
cursor.execute("""
    CREATE TABLE alembic_version (
        version_num VARCHAR(32) NOT NULL,
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
    )
""")
conn.commit()
print("✓ Created alembic_version table")

# Now run migrations using Alembic
with app.app_context():
    from flask_migrate import upgrade
    print("\nRunning Alembic upgrade...")
    try:
        upgrade()
        print("✓ Upgrade completed")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

# Verify the results
print("\nVerifying database...")
conn2 = sqlite3.connect(db_path)
cursor2 = conn2.cursor()
cursor2.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor2.fetchall()
print(f"✓ Tables created: {len(tables)}")
for table in tables:
    print(f"    - {table[0]}")

# Check versions
cursor2.execute("SELECT version_num FROM alembic_version;")
versions = cursor2.fetchall()
print(f"\nAlembic versions applied:")
for v in versions:
    print(f"    - {v[0]}")

conn2.close()
print("\n✓ Migration complete!")
