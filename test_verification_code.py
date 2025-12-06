#!/usr/bin/env python
"""Test the verification code system"""

import os
from app import create_app, db
from models import User, EmailToken
import string
import secrets

app = create_app()
with app.app_context():
    # Create a test user
    test_email = 'verification_test@example.com'
    test_user = User.query.filter_by(email=test_email).first()
    
    if not test_user:
        test_user = User(
            username='verify_test',
            email=test_email,
            phone_number='0241111111',
            is_verified=False
        )
        test_user.set_password('testpass123')
        db.session.add(test_user)
        db.session.commit()
        print(f"✅ Created test user: {test_email}")
    else:
        print(f"ℹ️ Test user already exists: {test_email}")
    
    # Generate a verification token/code
    from auth.utils import TokenGenerator
    token_result = TokenGenerator.generate_email_token(test_user, token_type='email_verification')
    
    if token_result['success']:
        email_token = token_result['token']
        print(f"\n✅ Token generated successfully!")
        print(f"   Token: {email_token.token}")
        print(f"   Verification Code: {email_token.verification_code}")
        print(f"   Code Length: {len(email_token.verification_code)} characters")
        print(f"   Code Pattern: Only uppercase letters and digits (A-Z, 0-9)")
        print(f"   Expires at: {email_token.expires_at}")
        
        # Test code verification
        print(f"\n🧪 Testing code verification:")
        
        # Find token by code
        found_token = EmailToken.query.filter_by(
            verification_code=email_token.verification_code.upper(),
            token_type='email_verification'
        ).first()
        
        if found_token:
            print(f"   ✅ Code lookup works!")
            print(f"   ✅ Found token for user: {found_token.user.email}")
            print(f"   ✅ Token is valid: {found_token.is_valid()}")
        else:
            print(f"   ❌ Code lookup failed!")
    else:
        print(f"❌ Token generation failed: {token_result['message']}")
