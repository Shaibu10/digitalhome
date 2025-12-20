#!/usr/bin/env python
"""
Test script to verify profile updates now persist correctly.
"""

import sys
sys.path.insert(0, '.')

from app import app, db
from models import User

def test_profile_update():
    """Test profile update functionality"""
    print("\n" + "=" * 70)
    print("TESTING PROFILE UPDATE PERSISTENCE")
    print("=" * 70)
    
    try:
        with app.app_context():
            # Get first user or create one
            test_user = User.query.first()
            
            if not test_user:
                print("\n❌ No users found in database. Please create a test user first.")
                return False
            
            print(f"\n📝 Test user: {test_user.username} (ID: {test_user.id})")
            
            # Record original values
            original_first_name = test_user.first_name
            original_phone = test_user.phone_number
            
            print(f"\n📊 Original values:")
            print(f"   First Name: {original_first_name}")
            print(f"   Phone: {original_phone}")
            
            # Update profile fields
            print(f"\n🔄 Updating profile...")
            test_user.first_name = "Test User Updated"
            test_user.phone_number = "+233241234567"
            
            try:
                db.session.commit()
                print("✅ Profile update committed successfully!")
            except Exception as e:
                print(f"❌ Database commit failed: {e}")
                db.session.rollback()
                return False
            
            # Verify changes persisted
            print(f"\n🔍 Verifying persistence...")
            
            # Clear session to force database reload
            db.session.expunge_all()
            
            # Reload user from database
            reloaded_user = User.query.get(test_user.id)
            
            print(f"\n📊 New values (from database):")
            print(f"   First Name: {reloaded_user.first_name}")
            print(f"   Phone: {reloaded_user.phone_number}")
            
            # Check if values persisted
            if reloaded_user.first_name == "Test User Updated" and reloaded_user.phone_number == "+233241234567":
                print("\n✅ SUCCESS! Profile updates are persisting correctly!")
                
                # Restore original values
                reloaded_user.first_name = original_first_name
                reloaded_user.phone_number = original_phone
                db.session.commit()
                print("   (Restored original values)")
                
                return True
            else:
                print("\n❌ Profile updates NOT persisting!")
                return False
                
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_profile_update()
    
    print("\n" + "=" * 70)
    if success:
        print("✨ PROFILE UPDATE FIX VERIFIED - ALL TESTS PASSED!")
    else:
        print("⚠️  TESTS FAILED - Profile update issue not resolved")
    print("=" * 70 + "\n")
    
    sys.exit(0 if success else 1)
