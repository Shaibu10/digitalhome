#!/usr/bin/env python
"""Test profile update persistence"""

import sys
sys.path.insert(0, '.')

print("=" * 70)
print("TESTING PROFILE UPDATE PERSISTENCE")
print("=" * 70)

try:
    from app import app, db
    from models import User
    
    with app.app_context():
        # Get admin user or create test user
        user = User.query.filter_by(email='admin@example.com').first()
        user_id = user.id if user else None
        
        if not user:
            print("\nERROR: Admin user not found")
            exit(1)
        
        print(f"\nTest user: {user.username} (ID: {user_id})")
        print(f"Original values:")
        print(f"  first_name: {user.first_name}")
        print(f"  last_name: {user.last_name}")
        print(f"  phone_number: {user.phone_number}")
        
        # Update profile
        print(f"\nUpdating profile...")
        user.first_name = "Test User Updated"
        user.last_name = "Profile"
        user.phone_number = "+233241234567"
        user.city = "Accra"
        user.address = "123 Test Street"
        
        db.session.commit()
        print("  - Changes committed to database")
        
        # Reload from database fresh
        user_reloaded = User.query.get(user_id)
        print(f"\nReloaded values from database:")
        print(f"  first_name: {user_reloaded.first_name}")
        print(f"  last_name: {user_reloaded.last_name}")
        print(f"  phone_number: {user_reloaded.phone_number}")
        print(f"  city: {user_reloaded.city}")
        print(f"  address: {user_reloaded.address}")
        
        # Verify persistence
        if (user_reloaded.first_name == "Test User Updated" and
            user_reloaded.phone_number == "+233241234567"):
            print("\n" + "=" * 70)
            print("SUCCESS! Profile updates persist correctly!")
            print("=" * 70)
            exit(0)
        else:
            print("\nERROR: Profile updates did not persist!")
            exit(1)
            
except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
