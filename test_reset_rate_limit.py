#!/usr/bin/env python
"""Check and fix rate limiting for user"""

from app import create_app, db
from models import User, TokenRateLimit
from datetime import datetime

app = create_app()
with app.app_context():
    test_email = 'shaibu5278@gmail.com'
    
    user = User.query.filter_by(email=test_email).first()
    
    if user:
        print(f"✅ Found user: {user.username}")
        print(f"   Email: {user.email}")
        
        # Check rate limit
        print(f"\n📋 Checking rate limit status...")
        rate_limit = TokenRateLimit.query.filter_by(email=test_email).first()
        
        if rate_limit:
            print(f"   Attempt count: {rate_limit.attempt_count}")
            print(f"   Last attempt: {rate_limit.last_attempt_at}")
            print(f"   Locked until: {rate_limit.locked_until}")
            print(f"   Is locked: {rate_limit.is_locked()}")
            
            # Reset the rate limit
            print(f"\n🔄 Resetting rate limit...")
            rate_limit.attempt_count = 0
            rate_limit.locked_until = None
            db.session.commit()
            print(f"   ✅ Rate limit reset!")
        else:
            print(f"   No rate limit record found")
        
        # Now try to generate token again
        print(f"\n🔄 Generating new verification token...")
        from auth.utils import TokenGenerator
        
        token_result = TokenGenerator.generate_email_token(
            user,
            token_type='email_verification',
            expires_in_hours=24
        )
        
        if token_result['success']:
            email_token = token_result['token']
            print(f"   ✅ Token generated successfully!")
            print(f"   Verification Code: {email_token.verification_code}")
            print(f"   Token: {email_token.token[:30]}...")
            print(f"   Expires: {email_token.expires_at}")
            
            # Send verification notifications
            print(f"\n📧 Sending verification notifications...")
            try:
                from emails.service import send_verification_email
                from sms.service import send_verification_sms
                
                verification_url = f"http://localhost:5000/auth/verify-email/{email_token.token}"
                
                # Send email
                print(f"   📧 Sending email to {user.email}...")
                email_result = send_verification_email(
                    user,
                    email_token.verification_code,
                    verification_url
                )
                print(f"      Result: {'✅ Sent' if email_result else '❌ Failed'}")
                
                # Send SMS
                print(f"   📱 Sending SMS to {user.phone_number}...")
                sms_result = send_verification_sms(
                    user,
                    email_token.verification_code
                )
                print(f"      Result: {'✅ Sent' if sms_result else '❌ Failed'}")
                
                print(f"\n{'='*60}")
                print(f"✅ VERIFICATION CODE SENT!")
                print(f"{'='*60}")
                print(f"Code: {email_token.verification_code}")
                print(f"Email: {user.email}")
                print(f"Phone: {user.phone_number}")
                print(f"\n📍 Verify at: http://localhost:5000/auth/verify-code")
                print(f"⏰ Code expires in 24 hours")
                print(f"{'='*60}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   ❌ Failed: {token_result['message']}")
    else:
        print(f"❌ User not found")
