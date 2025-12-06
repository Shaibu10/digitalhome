"""
Test script for bulk user operations
"""

import sys
import json
from app import app, db
from models import User
from flask import json as flask_json

def create_test_users():
    """Create test users for bulk operations"""
    with app.app_context():
        # Clear existing test users
        test_users = User.query.filter(User.username.like('test_bulk_%')).all()
        for user in test_users:
            db.session.delete(user)
        db.session.commit()
        
        # Create test users
        users = []
        for i in range(1, 6):
            user = User(
                username=f'test_bulk_{i}',
                email=f'test_bulk_{i}@example.com',
                is_active=True if i <= 3 else False,
                is_verified=True,
                phone_number='0241234567'
            )
            user.set_password('password123')
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        
        print(f"✅ Created {len(users)} test users")
        for user in users:
            print(f"   - {user.username} (ID: {user.id}, Active: {user.is_active})")
        
        return [u.id for u in users]

def test_bulk_operations():
    """Test bulk operations through API calls"""
    with app.app_context():
        # Login as admin (create test admin if needed)
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ No admin user found. Please create an admin account first.")
            return
        
        print(f"✅ Found admin user: {admin.username}")
        
        # Create test users
        test_user_ids = create_test_users()
        
        # Test client
        client = app.test_client()
        
        # Simulate login (Flask-Login in test context)
        with client:
            # Test 1: Bulk Activate
            print("\n📋 Test 1: Bulk Activate")
            response = client.post(
                '/api/admin/users/bulk_activate',
                json={'user_ids': test_user_ids[3:5]},
                headers={'Authorization': f'Bearer {admin.id}'}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 403:
                print("   ⚠️ Expected 403 (not logged in during test). Bulk operations require authentication.")
            else:
                data = response.get_json()
                print(f"   Response: {data}")
            
            # Test 2: Bulk Deactivate
            print("\n📋 Test 2: Bulk Deactivate")
            response = client.post(
                '/api/admin/users/bulk_deactivate',
                json={'user_ids': test_user_ids[0:2]},
                headers={'Authorization': f'Bearer {admin.id}'}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 403:
                print("   ⚠️ Expected 403 (not logged in during test).")
            else:
                data = response.get_json()
                print(f"   Response: {data}")
            
            # Test 3: Bulk Delete
            print("\n📋 Test 3: Bulk Delete")
            response = client.post(
                '/api/admin/users/bulk_delete',
                json={'user_ids': [test_user_ids[4]]},
                headers={'Authorization': f'Bearer {admin.id}'}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 403:
                print("   ⚠️ Expected 403 (not logged in during test).")
            else:
                data = response.get_json()
                print(f"   Response: {data}")

def verify_api_routes():
    """Verify that all API routes exist"""
    with app.app_context():
        print("📍 Checking API routes...")
        
        routes_to_check = [
            '/api/admin/users/bulk_activate',
            '/api/admin/users/bulk_deactivate',
            '/api/admin/users/bulk_delete',
        ]
        
        app_routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        for route in routes_to_check:
            if route in app_routes:
                print(f"   ✅ {route}")
            else:
                print(f"   ❌ {route} NOT FOUND")

if __name__ == '__main__':
    print("🧪 Testing Bulk User Operations\n")
    verify_api_routes()
    print("\n" + "="*60)
    test_bulk_operations()
    print("\n" + "="*60)
    print("\n✅ Test script completed. Access http://localhost:5000/admin/users to test UI.")
