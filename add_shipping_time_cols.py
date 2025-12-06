"""
Script to add shipping time columns to SystemSettings table directly
Works with SQLite or any SQL database
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'e:\\python_projects\\digialhome')

from app import create_app, db
from sqlalchemy import inspect, text

app = create_app()

with app.app_context():
    try:
        # Get the inspector to check existing columns
        inspector = inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('system_settings')]
        
        print("\n[INFO] Existing columns in system_settings:")
        for col in existing_columns:
            print(f"   - {col}")
        
        # Define the columns to add
        new_columns = [
            'standard_shipping_hours_min',
            'standard_shipping_hours_max',
            'standard_shipping_minutes_min',
            'standard_shipping_minutes_max',
            'express_shipping_hours_min',
            'express_shipping_hours_max',
            'express_shipping_minutes_min',
            'express_shipping_minutes_max',
            'free_shipping_hours_min',
            'free_shipping_hours_max',
            'free_shipping_minutes_min',
            'free_shipping_minutes_max',
        ]
        
        print("\n[ACTION] Adding new columns...")
        added_count = 0
        skipped_count = 0
        
        for col in new_columns:
            if col not in existing_columns:
                try:
                    # Use text() for SQL execution with proper connection
                    with db.engine.connect() as conn:
                        conn.execute(text(f"ALTER TABLE system_settings ADD COLUMN {col} INTEGER DEFAULT 0"))
                        conn.commit()
                    added_count += 1
                    print(f"   [OK] Added column: {col}")
                except Exception as e:
                    print(f"   [FAIL] Could not add {col}: {str(e)}")
            else:
                skipped_count += 1
                print(f"   [EXISTS] Column already exists: {col}")
        
        print(f"\n[SUCCESS] Migration complete!")
        print(f"   - {added_count} new columns added")
        print(f"   - {skipped_count} columns already existed")
        print("\n[SUCCESS] Admin can now set shipping days AND times!")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
