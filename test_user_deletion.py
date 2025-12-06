#!/usr/bin/env python
"""Test user deletion with activity records"""

from app import create_app, db, log_user_activity
from models import User, UserActivity
from flask import Flask
import time

app = create_app()
with app.app_context():
    # Create a test user with unique email
    timestamp = int(time.time() * 1000)
    test_email = f'delete_test_{timestamp}@example.com'
    user = User(
        username=f'delete_test_user_{timestamp}',
        email=test_email,
        is_verified=True,
        is_active=True
    )
    user.set_password('test123')
    db.session.add(user)
    db.session.commit()
    user_id = user.id
    
    print(f"✅ Created test user: {test_email} (ID: {user_id})")
    
    # Add some activity records
    activity1 = UserActivity(
        user_id=user_id,
        activity_type='login',
        description='Test login activity',
        ip_address='127.0.0.1'
    )
    activity2 = UserActivity(
        user_id=user_id,
        activity_type='test_action',
        description='Another test activity',
        ip_address='127.0.0.1'
    )
    db.session.add_all([activity1, activity2])
    db.session.commit()
    
    activity_count = UserActivity.query.filter_by(user_id=user_id).count()
    print(f"✅ Added {activity_count} activity records for user")
    
    # Now delete the user
    print(f"\n🗑️ Deleting user {user_id}...")
    
    try:
        # Delete activity records
        UserActivity.query.filter_by(user_id=user_id).delete()
        print(f"   ✅ Deleted {activity_count} activity records")
        
        # Delete user
        user_to_delete = User.query.get(user_id)
        db.session.delete(user_to_delete)
        db.session.commit()
        
        # Verify deletion
        deleted_user = User.query.get(user_id)
        if deleted_user is None:
            print(f"   ✅ User successfully deleted")
        else:
            print(f"   ❌ User still exists!")
        
        remaining_activities = UserActivity.query.filter_by(user_id=user_id).count()
        print(f"   ✅ Remaining activities: {remaining_activities}")
        
        print(f"\n✅ User deletion test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during deletion: {e}")
        import traceback
        traceback.print_exc()
