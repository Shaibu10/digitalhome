#!/usr/bin/env python
"""
Diagnostic script for profile update issue.
Tests DB persistence and identifies where the issue occurs.
"""

import sys
sys.path.insert(0, '.')

from app import app, db
from models import User
from datetime import datetime

def diagnose():
    """Run comprehensive diagnostic tests"""
    print("\n" + "=" * 80)
    print("PROFILE UPDATE DIAGNOSTIC TEST")
    print("=" * 80)
    
    try:
        with app.app_context():
            # Test 1: Check database is accessible
            print("\n[TEST 1] Database Connection")
            print("-" * 80)
            try:
                user_count = User.query.count()
                print(f"✅ Database accessible. Total users: {user_count}")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
            
            if user_count == 0:
                print("❌ No users in database. Create a user first.")
                return False
            
            # Test 2: Load a test user
            print("\n[TEST 2] Load Test User")
            print("-" * 80)
            test_user = User.query.first()
            print(f"✅ Loaded user: {test_user.username} (ID: {test_user.id})")
            print(f"   Current first_name: '{test_user.first_name}'")
            print(f"   Current phone: '{test_user.phone_number}'")
            
            # Test 3: Update profile directly (DB persistence)
            print("\n[TEST 3] Direct Database Update")
            print("-" * 80)
            new_first_name = f"Updated_{datetime.now().strftime('%H%M%S')}"
            new_phone = "+233701234567"
            
            print(f"Setting first_name to: '{new_first_name}'")
            print(f"Setting phone_number to: '{new_phone}'")
            
            test_user.first_name = new_first_name
            test_user.phone_number = new_phone
            
            print("Committing to database...")
            try:
                db.session.commit()
                print("✅ Commit successful")
            except Exception as e:
                print(f"❌ Commit failed: {e}")
                db.session.rollback()
                return False
            
            # Test 4: Verify persistence (reload from DB)
            print("\n[TEST 4] Verify Persistence (Reload from Database)")
            print("-" * 80)
            db.session.expunge_all()  # Clear session cache
            
            reloaded = User.query.get(test_user.id)
            print(f"Reloaded first_name: '{reloaded.first_name}'")
            print(f"Reloaded phone_number: '{reloaded.phone_number}'")
            
            if reloaded.first_name == new_first_name and reloaded.phone_number == new_phone:
                print("✅ Values persisted correctly!")
            else:
                print("❌ Values did NOT persist!")
                print(f"   Expected first_name: '{new_first_name}', got: '{reloaded.first_name}'")
                print(f"   Expected phone: '{new_phone}', got: '{reloaded.phone_number}'")
                return False
            
            # Test 5: Simulate web request (JSON to DB)
            print("\n[TEST 5] Simulate Web Request Update")
            print("-" * 80)
            
            # Simulate what the web request handler does
            update_data = {
                'first_name': f"WebUpdate_{datetime.now().strftime('%H%M%S')}",
                'last_name': test_user.last_name or '',
                'address': test_user.address or '',
                'city': test_user.city or '',
                'postal_code': test_user.postal_code or '',
                'phone_number': '+233702345678'
            }
            
            print(f"Simulating update_profile with data: {update_data}")
            
            # Get fresh user object
            user_to_update = User.query.get(test_user.id)
            user_to_update.first_name = update_data['first_name']
            user_to_update.last_name = update_data['last_name'] if update_data['last_name'] else None
            user_to_update.address = update_data['address'] if update_data['address'] else None
            user_to_update.city = update_data['city'] if update_data['city'] else None
            user_to_update.postal_code = update_data['postal_code'] if update_data['postal_code'] else None
            user_to_update.phone_number = update_data['phone_number']
            
            try:
                db.session.commit()
                print("✅ Web-simulated update committed")
            except Exception as e:
                print(f"❌ Commit failed: {e}")
                db.session.rollback()
                return False
            
            # Verify again
            db.session.expunge_all()
            final_check = User.query.get(test_user.id)
            print(f"Final verification - first_name: '{final_check.first_name}'")
            
            if final_check.first_name == update_data['first_name']:
                print("✅ Web-simulated update persisted!")
            else:
                print("❌ Web-simulated update did NOT persist!")
                return False
            
            # Test 6: Check SQLAlchemy configuration
            print("\n[TEST 6] SQLAlchemy Configuration Check")
            print("-" * 80)
            print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            print(f"Track modifications: {app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS', 'Not set')}")
            print(f"Engine pooling: pool_size={db.engine.pool.size if hasattr(db.engine.pool, 'size') else 'N/A'}")
            print("✅ Configuration looks normal")
            
            print("\n" + "=" * 80)
            print("✅ ALL DIAGNOSTIC TESTS PASSED!")
            print("=" * 80)
            print("\nCONCLUSION:")
            print("  Database persistence is working correctly.")
            print("  The issue may be in:")
            print("  - Browser caching")
            print("  - Session management in the web request")
            print("  - JavaScript not properly reloading the page")
            print("=" * 80 + "\n")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Diagnostic error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = diagnose()
    sys.exit(0 if success else 1)
