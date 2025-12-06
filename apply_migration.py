"""
Script to apply the shipping time migration to the database
"""
import sys
sys.path.insert(0, 'e:\\python_projects\\digialhome')

from app import create_app, db
from flask_migrate import upgrade

app = create_app()

with app.app_context():
    try:
        # Apply pending migrations
        upgrade()
        print("✓ Migration applied successfully!")
        print("✓ New columns added to system_settings table")
    except Exception as e:
        print(f"✗ Migration error: {str(e)}")
        sys.exit(1)
