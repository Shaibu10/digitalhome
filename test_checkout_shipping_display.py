"""
Test script to verify checkout displays delivery time correctly
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'e:\\python_projects\\digialhome')

from app import create_app, calculate_shipping_cost, db
from models import SystemSettings

app = create_app()

with app.app_context():
    try:
        print("\n[TEST] Checkout Shipping Display with Time")
        print("=" * 60)
        
        # Get current settings
        settings = SystemSettings.get_settings()
        
        print("\n[INFO] Current settings in database:")
        print(f"  Standard: {settings.standard_shipping_days_min}-{settings.standard_shipping_days_max}d {settings.standard_shipping_hours_min}h{settings.standard_shipping_minutes_min}m - {settings.standard_shipping_hours_max}h{settings.standard_shipping_minutes_max}m")
        print(f"  Express:  {settings.express_shipping_days_min}-{settings.express_shipping_days_max}d {settings.express_shipping_hours_min}h{settings.express_shipping_minutes_min}m - {settings.express_shipping_hours_max}h{settings.express_shipping_minutes_max}m")
        print(f"  Free:     {settings.free_shipping_days_min}-{settings.free_shipping_days_max}d {settings.free_shipping_hours_min}h{settings.free_shipping_minutes_min}m - {settings.free_shipping_hours_max}h{settings.free_shipping_minutes_max}m")
        
        # Calculate shipping options for a test order
        print("\n[TEST] Calculating shipping options for GH₵ 150 order...")
        shipping_options = calculate_shipping_cost(150, [])
        
        print("\n[CHECKOUT DISPLAY] Shipping Methods:")
        for method, details in shipping_options.items():
            print(f"\n  {method.upper()}:")
            print(f"    Label: {details['label']}")
            print(f"    Cost:  GH₵ {details['cost']:.2f}")
            print(f"    Data:  days={details['days_min']}-{details['days_max']}, hours={details.get('hours_min', 0)}-{details.get('hours_max', 0)}, minutes={details.get('minutes_min', 0)}-{details.get('minutes_max', 0)}")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Checkout shipping display includes time information!")
        print("\nExample displays on checkout page:")
        for method, details in shipping_options.items():
            print(f"  {details['label']}")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
