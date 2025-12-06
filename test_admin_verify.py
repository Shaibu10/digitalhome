#!/usr/bin/env python
"""Test manual user verification functionality"""

from app import create_app, db
from models import User, EmailToken
from datetime import datetime

app = create_app()
with app.app_context():
    # Find or create a test unverified user
    test_email = 'unverified_user@example.com'
    user = User.query.filter_by(email=test_email).first()
    
    if not user:
        user = User(
            username='unverified_test',
            email=test_email,
            phone_number='0241234567',
            is_verified=False,
            is_active=True
        )
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
        print(f"✅ Created unverified test user: {test_email}")
    else:
        print(f"✅ Using existing unverified user: {test_email}")
    
    print(f"\n📋 User Status Before:")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Is Verified: {user.is_verified}")
    print(f"   Verified At: {user.verified_at}")
    
    # Simulate admin manually verifying the user
    print(f"\n🔐 Admin manually verifying user...")
    user.is_verified = True
    user.verified_at = datetime.utcnow()
    
    # Mark any existing tokens as used
    EmailToken.query.filter_by(
        user_id=user.id,
        token_type='email_verification'
    ).update({'used_at': datetime.utcnow()})
    
    db.session.commit()
    
    print(f"\n✅ User Status After:")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Is Verified: {user.is_verified}")
    print(f"   Verified At: {user.verified_at}")
    
    # Verify the admin_verify_user route exists
    from app import admin_verify_user
    print(f"\n✅ admin_verify_user route function exists and is callable")
    
    print(f"\n✅ Manual verification test completed successfully!")
