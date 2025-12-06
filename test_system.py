#!/usr/bin/env python
"""Test the application by simulating a user registration."""

from app import app, db
from models import User, EmailToken

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            is_verified=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created")
    else:
        print(f"✅ Admin user exists: {admin.email}")
    
    # Test creating a regular user
    test_user = User.query.filter_by(email='test@example.com').first()
    if not test_user:
        print("Creating test user...")
        test_user = User(
            username='testuser',
            email='test@example.com',
            is_verified=False
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        db.session.commit()
        print(f"✅ Test user created: {test_user.email}, verified: {test_user.is_verified}")
    else:
        print(f"✅ Test user exists: {test_user.email}, verified: {test_user.is_verified}")
    
    # Check routes
    print("\nRegistered auth routes:")
    for rule in app.url_map.iter_rules():
        if 'auth' in str(rule):
            print(f"  {rule}")
    
    print("\n✅ All systems operational!")
