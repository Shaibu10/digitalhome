#!/usr/bin/env python
"""Test script to verify settings implementation"""

from app import app, db
from models import SystemSettings, User
from flask import url_for

print("=" * 60)
print("Testing Dynamic Settings Implementation")
print("=" * 60)

try:
    with app.app_context():
        # Create all tables
        db.create_all()
        print("\n✅ Database tables created")
        
        # Test SystemSettings initialization
        settings = SystemSettings.get_settings()
        print(f"\n✅ SystemSettings retrieved:")
        print(f"   - Standard Shipping: GH₵ {settings.standard_shipping_cost}")
        print(f"   - Express Shipping: GH₵ {settings.express_shipping_cost}")
        print(f"   - Free Threshold: GH₵ {settings.free_shipping_threshold}")
        print(f"   - Tax Rate: {settings.tax_rate * 100}%")
        
        # Test route registration
        with app.test_request_context():
            admin_settings_url = url_for('admin_settings')
            print(f"\n✅ Admin Settings Route: {admin_settings_url}")
        
        # Test update methods
        settings.update_shipping_settings(12.00, 18.00, 120.00, None)
        db.session.commit()
        updated_settings = SystemSettings.get_settings()
        print(f"\n✅ Settings updated successfully:")
        print(f"   - Standard Shipping: GH₵ {updated_settings.standard_shipping_cost}")
        print(f"   - Express Shipping: GH₵ {updated_settings.express_shipping_cost}")
        print(f"   - Free Threshold: GH₵ {updated_settings.free_shipping_threshold}")
        
        # Reset to defaults
        settings.update_shipping_settings(10.00, 15.00, 100.00, None)
        settings.update_tax_settings(0.05, None)
        db.session.commit()
        print(f"\n✅ Settings reset to defaults")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
