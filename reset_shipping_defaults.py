"""
Update shipping settings to have sensible defaults (0 hours, 0 minutes)
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
        print("\n[ACTION] Resetting shipping time to 0h 0m defaults...")
        
        settings = SystemSettings.get_settings()
        
        # Reset all hours and minutes to 0
        settings.standard_shipping_hours_min = 0
        settings.standard_shipping_hours_max = 0
        settings.standard_shipping_minutes_min = 0
        settings.standard_shipping_minutes_max = 0
        
        settings.express_shipping_hours_min = 0
        settings.express_shipping_hours_max = 0
        settings.express_shipping_minutes_min = 0
        settings.express_shipping_minutes_max = 0
        
        settings.free_shipping_hours_min = 0
        settings.free_shipping_hours_max = 0
        settings.free_shipping_minutes_min = 0
        settings.free_shipping_minutes_max = 0
        
        settings.updated_by_id = 1
        from datetime import datetime
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        print("\n[RESULT] Shipping times reset to defaults:")
        print(f"  Standard: {settings.standard_shipping_days_min}-{settings.standard_shipping_days_max}d {settings.standard_shipping_hours_min}h{settings.standard_shipping_minutes_min}m - {settings.standard_shipping_hours_max}h{settings.standard_shipping_minutes_max}m")
        print(f"  Express:  {settings.express_shipping_days_min}-{settings.express_shipping_days_max}d {settings.express_shipping_hours_min}h{settings.express_shipping_minutes_min}m - {settings.express_shipping_hours_max}h{settings.express_shipping_minutes_max}m")
        print(f"  Free:     {settings.free_shipping_days_min}-{settings.free_shipping_days_max}d {settings.free_shipping_hours_min}h{settings.free_shipping_minutes_min}m - {settings.free_shipping_hours_max}h{settings.free_shipping_minutes_max}m")
        
        print("\n[SUCCESS] Default shipping times set!")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
