#!/usr/bin/env python
"""Test script to verify both orders page and order detail page update functionality."""

import json
import sys
sys.path.insert(0, '.')

from app import app, db
from models import Order, User

def test_orders_page_update():
    """Test update from /admin/orders page."""
    print("\n" + "="*70)
    print("TEST 1: Orders List Page (/admin/orders) Update")
    print("="*70)
    
    with app.app_context():
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ No admin user found")
            return False
        
        order = Order.query.first()
        if not order:
            print("❌ No orders found")
            return False
        
        with app.test_client() as client:
            # Login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(admin.id)
            
            # Get the orders page
            response = client.get('/admin/orders')
            print(f"✓ GET /admin/orders - Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Failed to load orders page")
                return False
            
            # Check if page contains update button
            page_content = response.get_data(as_text=True)
            if 'updateStatus(' in page_content and 'confirmUpdateStatus()' in page_content:
                print(f"✓ Page contains update functionality")
            else:
                print(f"❌ Page missing update functionality")
                return False
            
            # Test the update API
            payload = {
                'order_id': order.id,
                'status': 'processing',
                'tracking_number': 'TRACK-FROM-LIST'
            }
            
            response = client.post(
                '/api/update_order_status',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"✓ POST /api/update_order_status - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print(f"✓ Update successful")
                    print(f"  Changes: {data.get('changes')}")
                    db.session.refresh(order)
                    print(f"  DB confirms - Status: {order.status}, Tracking: {order.tracking_number}")
                    return True
                else:
                    print(f"❌ API returned error: {data.get('error')}")
                    return False
            else:
                print(f"❌ API returned status {response.status_code}")
                print(f"   Response: {response.get_data(as_text=True)}")
                return False

def test_order_detail_page_update():
    """Test update from /admin/order/<id> detail page."""
    print("\n" + "="*70)
    print("TEST 2: Order Detail Page (/admin/order/{id}) Update")
    print("="*70)
    
    with app.app_context():
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ No admin user found")
            return False
        
        order = Order.query.first()
        if not order:
            print("❌ No orders found")
            return False
        
        with app.test_client() as client:
            # Login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(admin.id)
            
            # Get the order detail page
            response = client.get(f'/admin/order/{order.id}')
            print(f"✓ GET /admin/order/{order.id} - Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Failed to load order detail page")
                return False
            
            # Check if page contains update button
            page_content = response.get_data(as_text=True)
            if 'confirmUpdateStatus()' in page_content:
                print(f"✓ Page contains update functionality")
            else:
                print(f"❌ Page missing update functionality")
                return False
            
            # Test the update API with all fields
            payload = {
                'order_id': order.id,
                'status': 'shipped',
                'payment_status': 'paid',
                'tracking_number': 'TRACK-FROM-DETAIL',
                'estimated_delivery': '2025-12-10',
                'internal_notes': 'Test note from automation script',
                'notify_customer': True,
                'notify_team': False
            }
            
            response = client.post(
                '/api/update_order_status',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"✓ POST /api/update_order_status (full fields) - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print(f"✓ Update successful")
                    print(f"  Changes: {data.get('changes')}")
                    db.session.refresh(order)
                    print(f"  DB confirms:")
                    print(f"    Status: {order.status}")
                    print(f"    Payment: {order.payment_status}")
                    print(f"    Tracking: {order.tracking_number}")
                    print(f"    Delivery: {order.shipped_at}")
                    print(f"    Notes: {order.notes[:100] if order.notes else 'None'}")
                    return True
                else:
                    print(f"❌ API returned error: {data.get('error')}")
                    return False
            else:
                print(f"❌ API returned status {response.status_code}")
                print(f"   Response: {response.get_data(as_text=True)}")
                return False

if __name__ == '__main__':
    results = []
    
    results.append(("Orders Page Update", test_orders_page_update()))
    results.append(("Order Detail Page Update", test_order_detail_page_update()))
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(r for _, r in results)
    print("\n" + ("✓ ALL TESTS PASSED!" if all_passed else "❌ SOME TESTS FAILED"))
    
    sys.exit(0 if all_passed else 1)
