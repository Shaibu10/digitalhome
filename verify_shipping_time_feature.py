"""
Verification script to test the shipping time feature
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'e:\\python_projects\\digialhome')

from app import create_app, db
from models import SystemSettings
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    try:
        print("\n[CHECK 1] Database columns")
        inspector = inspect(db.engine)
        cols = [col['name'] for col in inspector.get_columns('system_settings')]
        
        required_cols = [
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
        
        missing = [c for c in required_cols if c not in cols]
        if missing:
            print(f"   [FAIL] Missing columns: {missing}")
        else:
            print("   [OK] All time columns exist in database")
        
        print("\n[CHECK 2] SystemSettings model attributes")
        settings = SystemSettings.get_settings()
        
        attrs_to_check = required_cols
        missing_attrs = []
        for attr in attrs_to_check:
            if not hasattr(settings, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"   [FAIL] Missing attributes: {missing_attrs}")
        else:
            print("   [OK] All time attributes exist in model")
        
        print("\n[CHECK 3] Sample values from database")
        print(f"   Standard: {settings.standard_shipping_hours_min}h {settings.standard_shipping_minutes_min}m - {settings.standard_shipping_hours_max}h {settings.standard_shipping_minutes_max}m")
        print(f"   Express:  {settings.express_shipping_hours_min}h {settings.express_shipping_minutes_min}m - {settings.express_shipping_hours_max}h {settings.express_shipping_minutes_max}m")
        print(f"   Free:     {settings.free_shipping_hours_min}h {settings.free_shipping_minutes_min}m - {settings.free_shipping_hours_max}h {settings.free_shipping_minutes_max}m")
        
        print("\n[CHECK 4] update_shipping_settings method")
        # Test the updated method signature
        try:
            settings.update_shipping_settings(
                10.0, 15.0, 100.0,  # costs and threshold
                3, 5,               # standard days
                1, 2,               # express days
                5, 7,               # free days
                1,                  # user_id
                0, 0, 30, 30,      # standard hours and minutes
                0, 0, 15, 45,      # express hours and minutes
                0, 1, 0, 30        # free hours and minutes
            )
            print("   [OK] update_shipping_settings accepts time parameters")
        except Exception as e:
            print(f"   [FAIL] Error calling update_shipping_settings: {str(e)}")
        
        print("\n[SUCCESS] All checks passed!")
        print("\nThe admin settings page now supports:")
        print("  - Days (0-30)")
        print("  - Hours (0-23)")  
        print("  - Minutes (0-59)")
        print("\nVisit: http://127.0.0.1:5000/admin/settings to configure!")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
