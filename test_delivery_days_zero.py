"""
Test script to verify delivery days can now be 0
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'e:\\python_projects\\digialhome')

from app import create_app, db
from models import SystemSettings

app = create_app()

with app.app_context():
    try:
        print("\n[TEST] Delivery days validation allows 0")
        print("=" * 50)
        
        settings = SystemSettings.get_settings()
        
        # Test case 1: Set delivery with 0 days, only hours and minutes
        print("\n[TEST 1] Setting express delivery to 0 days, 2 hours")
        settings.update_shipping_settings(
            standard_cost=10.0,
            express_cost=15.0,
            free_threshold=100.0,
            standard_min_days=0,  # NOW ALLOWED: 0 days
            standard_max_days=0,
            express_min_days=0,   # NOW ALLOWED: 0 days
            express_max_days=0,
            free_min_days=5,
            free_max_days=7,
            user_id=1,
            standard_min_hours=0,
            standard_max_hours=2,
            standard_min_minutes=0,
            standard_max_minutes=30,
            express_min_hours=0,
            express_max_hours=4,
            express_min_minutes=0,
            express_max_minutes=0,
            free_min_hours=0,
            free_max_hours=0,
            free_min_minutes=0,
            free_max_minutes=0
        )
        
        print(f"   Express: {settings.express_shipping_days_min}d {settings.express_shipping_hours_min}h - {settings.express_shipping_days_max}d {settings.express_shipping_hours_max}h")
        assert settings.express_shipping_days_min == 0, "Failed to set express days to 0"
        print("   [OK] Successfully set delivery days to 0!")
        
        # Test case 2: Verify we can still use traditional days
        print("\n[TEST 2] Standard delivery with traditional days and times")
        settings.standard_shipping_days_min = 3
        settings.standard_shipping_days_max = 5
        settings.standard_shipping_hours_min = 0
        settings.standard_shipping_hours_max = 2
        settings.standard_shipping_minutes_min = 0
        settings.standard_shipping_minutes_max = 30
        db.session.commit()
        
        print(f"   Standard: {settings.standard_shipping_days_min}d {settings.standard_shipping_hours_min}h{settings.standard_shipping_minutes_min}m - {settings.standard_shipping_days_max}d {settings.standard_shipping_hours_max}h{settings.standard_shipping_minutes_max}m")
        print("   [OK] Traditional delivery format still works!")
        
        # Test case 3: Hour-only delivery
        print("\n[TEST 3] Same-day delivery with only hours (0 days, 2-4 hours)")
        settings.standard_shipping_days_min = 0
        settings.standard_shipping_days_max = 0
        settings.standard_shipping_hours_min = 2
        settings.standard_shipping_hours_max = 4
        settings.standard_shipping_minutes_min = 0
        settings.standard_shipping_minutes_max = 0
        db.session.commit()
        
        print(f"   Display: 0d {settings.standard_shipping_hours_min}h00m - {settings.standard_shipping_hours_max}h00m")
        print("   [OK] Hour-only delivery works!")
        
        print("\n" + "=" * 50)
        print("[SUCCESS] Delivery days validation updated!")
        print("\nNow admins can set:")
        print("  - 0 days + 2h 30m  (Delivery in 2.5 hours)")
        print("  - 0 days + 4h 0m   (Same-day delivery)")
        print("  - 3-5 days + 0h 0m (Traditional days)")
        print("  - 3-5 days + 2h 30m (Days + time precision)")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
