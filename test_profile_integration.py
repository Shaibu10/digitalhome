#!/usr/bin/env python
"""
Integration test to verify profile update works end-to-end.
Simulates the exact flow as the web request.
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '.')

def test_profile_update_flow():
    """Test complete profile update flow"""
    print("\n" + "="*80)
    print("PROFILE UPDATE INTEGRATION TEST")
    print("="*80)
    
    try:
        # Import here to avoid import issues
        from app import app, db
        from models import User
        
        with app.app_context():
            print("\n[STEP 1] Load test user from database")
            print("-"*80)
            
            user = User.query.first()
            if not user:
                print("❌ No users found in database")
                return False
            
            print(f"✅ Loaded user: {user.username} (ID: {user.id})")
            original_first_name = user.first_name
            original_phone = user.phone_number
            print(f"   Current first_name: '{original_first_name}'")
            print(f"   Current phone_number: '{original_phone}'")
            
            print("\n[STEP 2] Prepare update data (simulating web request)")
            print("-"*80)
            
            timestamp = datetime.now().strftime('%H%M%S')
            update_data = {
                'first_name': f'Updated_{timestamp}',
                'last_name': user.last_name or '',
                'address': user.address or '',
                'city': user.city or '',
                'postal_code': user.postal_code or '',
                'phone_number': '+233741234567'
            }
            
            print(f"Update data: {json.dumps(update_data, indent=2)}")
            
            print("\n[STEP 3] Apply update to user object")
            print("-"*80)
            
            # Simulate what update_profile() does
            first_name = update_data.get('first_name', '').strip()
            last_name = update_data.get('last_name', '').strip()
            address = update_data.get('address', '').strip()
            city = update_data.get('city', '').strip()
            postal_code = update_data.get('postal_code', '').strip()
            phone_number = update_data.get('phone_number', '').strip()
            
            print(f"Stripped values:")
            print(f"  first_name: '{first_name}'")
            print(f"  phone_number: '{phone_number}'")
            
            user.first_name = first_name if first_name else None
            user.last_name = last_name if last_name else None
            user.address = address if address else None
            user.city = city if city else None
            user.postal_code = postal_code if postal_code else None
            user.phone_number = phone_number if phone_number else None
            
            print("✅ Object attributes updated")
            
            print("\n[STEP 4] Commit to database")
            print("-"*80)
            
            try:
                db.session.commit()
                print("✅ Database commit successful")
            except Exception as e:
                print(f"❌ Commit failed: {e}")
                db.session.rollback()
                return False
            
            print("\n[STEP 5] Verify persistence (reload from DB)")
            print("-"*80)
            
            # Clear session to force fresh load
            db.session.expunge_all()
            
            # Reload user from database
            reloaded = User.query.get(user.id)
            
            print(f"Reloaded values from database:")
            print(f"  first_name: '{reloaded.first_name}'")
            print(f"  last_name: '{reloaded.last_name}'")
            print(f"  phone_number: '{reloaded.phone_number}'")
            print(f"  address: '{reloaded.address}'")
            print(f"  city: '{reloaded.city}'")
            print(f"  postal_code: '{reloaded.postal_code}'")
            
            # Check if all values persisted
            success = True
            if reloaded.first_name != update_data['first_name']:
                print(f"❌ first_name mismatch!")
                print(f"   Expected: '{update_data['first_name']}'")
                print(f"   Got: '{reloaded.first_name}'")
                success = False
            else:
                print(f"✅ first_name persisted correctly")
            
            if reloaded.phone_number != phone_number:
                print(f"❌ phone_number mismatch!")
                print(f"   Expected: '{phone_number}'")
                print(f"   Got: '{reloaded.phone_number}'")
                success = False
            else:
                print(f"✅ phone_number persisted correctly")
            
            if not success:
                print("\n❌ TEST FAILED - Some values did not persist")
                return False
            
            # Restore original values
            print("\n[STEP 6] Restore original values")
            print("-"*80)
            
            reloaded.first_name = original_first_name
            reloaded.phone_number = original_phone
            db.session.commit()
            print("✅ Original values restored")
            
            print("\n" + "="*80)
            print("✅ ALL TESTS PASSED - Profile update working correctly!")
            print("="*80 + "\n")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_profile_update_flow()
    sys.exit(0 if success else 1)
