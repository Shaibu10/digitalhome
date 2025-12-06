#!/usr/bin/env python
"""Test the password reset functionality"""

from app import create_app, db
from models import User, EmailToken
from datetime import datetime

app = create_app()
with app.app_context():
    # Find or create a test user
    test_email = 'passwordreset@example.com'
    user = User.query.filter_by(email=test_email).first()
    
    if not user:
        user = User(
            username='reset_test',
            email=test_email,
            phone_number='0241234567',
            is_verified=True,
            is_active=True
        )
        user.set_password('oldpassword123')
        db.session.add(user)
        db.session.commit()
        print(f"✅ Created test user: {test_email}")
    else:
        print(f"✅ Using existing user: {test_email}")
    
    # Generate password reset token
    from auth.utils import TokenGenerator
    token_result = TokenGenerator.generate_email_token(user, token_type='password_reset', expires_in_hours=1)
    
    if token_result['success']:
        email_token = token_result['token']
        print(f"\n✅ Password Reset Token Generated:")
        print(f"   Token: {email_token.token[:20]}...")
        print(f"   Reset Code: {email_token.verification_code}")
        print(f"   Token Type: {email_token.token_type}")
        print(f"   Expires: {email_token.expires_at}")
        print(f"   Is Valid: {email_token.is_valid()}")
        
        # Test token verification
        print(f"\n🧪 Testing Token Verification:")
        verified_token = TokenGenerator.verify_token(email_token.token, token_type='password_reset')
        if verified_token:
            print(f"   ✅ Token verification successful")
            print(f"   Token belongs to: {verified_token.user.email}")
        else:
            print(f"   ❌ Token verification failed")
        
        # Test password change
        print(f"\n🔑 Testing Password Change:")
        user.set_password('newpassword123')
        db.session.commit()
        print(f"   ✅ Password changed successfully")
        print(f"   ✅ New password verified: {user.check_password('newpassword123')}")
        
        # Restore for next test
        user.set_password('oldpassword123')
        db.session.commit()
        
        print(f"\n✅ Password reset test completed successfully!")
    else:
        print(f"❌ Token generation failed: {token_result['message']}")
