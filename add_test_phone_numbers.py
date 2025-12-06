#!/usr/bin/env python
"""
Script to add test phone numbers to existing users for SMS testing
"""
import os
from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    # Get all users without phone numbers
    users = User.query.filter(User.phone_number.is_(None)).all()
    
    if not users:
        print("No users without phone numbers found.")
        exit(0)
    
    print(f"Found {len(users)} users without phone numbers:\n")
    
    for i, user in enumerate(users, 1):
        print(f"{i}. {user.username} ({user.email})")
    
    print("\n" + "="*50)
    print("ADDING TEST PHONE NUMBERS")
    print("="*50 + "\n")
    
    test_phones = [
        '0241234567',
        '0241234568',
        '0241234569',
        '0201111111',
        '0202222222',
        '0203333333',
    ]
    
    for i, user in enumerate(users):
        phone = test_phones[i % len(test_phones)]
        user.phone_number = phone
        db.session.add(user)
        print(f"✅ {user.username}: {phone}")
    
    try:
        db.session.commit()
        print(f"\n✅ Successfully added phone numbers to {len(users)} users!")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error: {str(e)}")
        exit(1)
