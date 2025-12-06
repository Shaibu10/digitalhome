#!/usr/bin/env python
"""Test password reset with SMS functionality"""

from app import create_app, db
from models import User
from datetime import datetime

app = create_app()
with app.app_context():
    # Find or create a test user with phone
    test_email = 'sms_reset_test@example.com'
    user = User.query.filter_by(email=test_email).first()
    
    if not user:
        user = User(
            username='sms_reset_test',
            email=test_email,
            phone_number='0241234567',
            is_verified=True,
            is_active=True
        )
        user.set_password('oldpass123')
        db.session.add(user)
        db.session.commit()
        print(f"✅ Created test user: {test_email} with phone: 0241234567")
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
        print(f"   Expires: {email_token.expires_at}")
        
        # Test sending email and SMS
        print(f"\n📧 Testing Email + SMS Sending:")
        try:
            from emails.service import send_password_reset_email
            from sms.service import send_password_reset_sms
            
            reset_url = f"http://localhost:5000/auth/reset-password/{email_token.token}"
            reset_code = email_token.verification_code
            
            # Send email
            email_result = send_password_reset_email(user, reset_code, reset_url)
            print(f"   Email sent: {email_result}")
            
            # Send SMS
            sms_result = send_password_reset_sms(user, reset_code)
            print(f"   SMS sent: {sms_result}")
            
            print(f"\n✅ Password reset with SMS test completed successfully!")
            print(f"   Reset Code: {reset_code}")
            print(f"   Would send to: {user.phone_number}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Token generation failed: {token_result['message']}")
