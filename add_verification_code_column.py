#!/usr/bin/env python
"""Add verification_code column to email_token table"""

import os
import sys
from app import create_app, db
from models import EmailToken

app = create_app()
with app.app_context():
    # Check if column exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('email_token')]
    
    if 'verification_code' not in columns:
        print("✅ Adding verification_code column to email_token table...")
        
        # Use direct SQL to add column
        with db.engine.connect() as conn:
            try:
                conn.execute(db.text("ALTER TABLE email_token ADD COLUMN verification_code VARCHAR(10)"))
                conn.commit()
                print("✅ Column added successfully!")
            except Exception as e:
                print(f"❌ Error adding column: {e}")
                conn.rollback()
    else:
        print("ℹ️ verification_code column already exists")
    
    # Update existing tokens with random codes if needed
    from sqlalchemy import func
    import secrets
    import string
    
    tokens_without_code = EmailToken.query.filter_by(verification_code=None).all()
    if tokens_without_code:
        print(f"⚠️ Found {len(tokens_without_code)} existing tokens without verification codes")
        print("Generating random codes for existing tokens...")
        
        for token in tokens_without_code:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            token.verification_code = code
            print(f"   Generated code: {code} for user {token.user_id}")
        
        db.session.commit()
        print("✅ Existing tokens updated with verification codes!")
    else:
        print("✅ All tokens have verification codes")
