#!/usr/bin/env python
"""Test verification code system with real user data"""

from app import create_app, db
from models import User, EmailToken
from datetime import datetime

app = create_app()
with app.app_context():
    # Find the user with real email
    test_email = 'shaibu5278@gmail.com'
    phone_number = '0544765278'
    
    user = User.query.filter_by(email=test_email).first()
    
    if user:
        print(f"✅ Found user: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Phone: {user.phone_number}")
        print(f"   Is Verified: {user.is_verified}")
        print(f"   Is Active: {user.is_active}")
        
        # Check for existing verification tokens
        print(f"\n📋 Checking for existing verification tokens...")
        tokens = EmailToken.query.filter_by(
            user_id=user.id,
            token_type='email_verification'
        ).all()
        
        if tokens:
            print(f"   Found {len(tokens)} verification tokens:")
            for token in tokens:
                print(f"   - Token: {token.token[:20]}...")
                print(f"     Code: {token.verification_code}")
                print(f"     Created: {token.created_at}")
                print(f"     Expires: {token.expires_at}")
                print(f"     Used At: {token.used_at}")
                print(f"     Is Valid: {token.is_valid()}")
                print()
        else:
            print(f"   No verification tokens found")
        
        # If not verified and no valid token, generate a new one
        if not user.is_verified:
            print(f"\n🔄 User is not verified. Generating new verification token...")
            from auth.utils import TokenGenerator
            
            token_result = TokenGenerator.generate_email_token(
                user,
                token_type='email_verification',
                expires_in_hours=24
            )
            
            if token_result['success']:
                email_token = token_result['token']
                print(f"   ✅ Token generated successfully!")
                print(f"   Token: {email_token.token[:30]}...")
                print(f"   Verification Code: {email_token.verification_code}")
                print(f"   Expires: {email_token.expires_at}")
                
                # Test sending verification email and SMS
                print(f"\n📧 Testing verification email and SMS sending...")
                try:
                    from emails.service import send_verification_email
                    from sms.service import send_verification_sms
                    
                    verification_url = f"http://localhost:5000/auth/verify-email/{email_token.token}"
                    
                    # Send email
                    print(f"   Sending email...")
                    email_result = send_verification_email(
                        user,
                        email_token.verification_code,
                        verification_url
                    )
                    print(f"   Email result: {email_result}")
                    
                    # Send SMS
                    print(f"   Sending SMS...")
                    sms_result = send_verification_sms(
                        user,
                        email_token.verification_code
                    )
                    print(f"   SMS result: {sms_result}")
                    
                    print(f"\n✅ Verification code: {email_token.verification_code}")
                    print(f"   Use this code at: http://localhost:5000/auth/verify-code")
                    
                except Exception as e:
                    print(f"   ❌ Error sending notifications: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"   ❌ Token generation failed: {token_result['message']}")
        else:
            print(f"\n✅ User is already verified!")
            print(f"   Verified at: {user.verified_at}")
    else:
        print(f"❌ User not found with email: {test_email}")
