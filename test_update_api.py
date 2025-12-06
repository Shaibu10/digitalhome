#!/usr/bin/env python
"""Test script to verify the update_order_status API endpoint."""

import json
import sys
sys.path.insert(0, '.')

from app import app, db
from models import Order, User
from flask_login import login_user

def test_update_endpoint():
    """Test the update endpoint with a real request."""
    with app.app_context():
        # Get or create test admin user
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ No admin user found in database")
            return False
        
        # Get a test order
        order = Order.query.first()
        if not order:
            print("❌ No orders found in database")
            return False
        
        print(f"✓ Found admin user: {admin.username}")
        print(f"✓ Found test order: {order.id}")
        print(f"  Current status: {order.status}")
        print(f"  Current tracking: {order.tracking_number}")
        
        # Simulate the API request
        with app.test_client() as client:
            # Login as admin
            with client.session_transaction() as sess:
                from flask_login import login_fresh
                sess['_user_id'] = str(admin.id)
            
            # Make the API request
            payload = {
                'order_id': order.id,
                'status': 'processing',
                'tracking_number': 'TEST123'
            }
            
            print(f"\n📝 Sending payload: {json.dumps(payload, indent=2)}")
            
            response = client.post(
                '/api/update_order_status',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"\n📊 Response Status: {response.status_code}")
            print(f"📊 Response Headers: {dict(response.headers)}")
            print(f"📊 Response Body: {response.get_data(as_text=True)}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"\n✓ API returned success: {data.get('success')}")
                print(f"✓ Message: {data.get('message')}")
                print(f"✓ Changes: {data.get('changes')}")
                
                # Verify in database
                db.session.refresh(order)
                print(f"\n✓ Order updated in DB:")
                print(f"  New status: {order.status}")
                print(f"  New tracking: {order.tracking_number}")
                return True
            else:
                print(f"\n❌ API returned error")
                return False

if __name__ == '__main__':
    test_update_endpoint()
