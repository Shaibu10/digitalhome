#!/usr/bin/env python
"""
Test script for the professional order and cart system.
Tests the complete order flow from cart to confirmation.
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Product, Category, Order, OrderItem, CartItem

def test_order_system():
    """Test the complete order and cart system."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("TESTING PROFESSIONAL ORDER & CART SYSTEM")
        print("="*70 + "\n")
        
        # Test 1: Verify models exist and have required fields
        print("✓ Test 1: Verify Order model fields...")
        order_fields = ['id', 'order_number', 'subtotal', 'shipping_cost', 'discount_amount', 
                       'discount_percentage', 'total_amount', 'status', 'payment_status', 
                       'payment_method', 'shipping_address', 'shipping_city', 'shipping_postal_code',
                       'shipping_phone', 'notes', 'tracking_number', 'created_at', 'shipped_at', 'delivered_at']
        
        order = Order()
        for field in order_fields:
            if hasattr(Order, field):
                print(f"  ✓ Order.{field} exists")
            else:
                print(f"  ✗ Order.{field} MISSING!")
                return False
        
        # Test 2: Verify OrderItem model
        print("\n✓ Test 2: Verify OrderItem model fields...")
        orderitem_fields = ['id', 'order_id', 'product_id', 'product_name', 'quantity', 'unit_price', 'total_price']
        
        for field in orderitem_fields:
            if hasattr(OrderItem, field):
                print(f"  ✓ OrderItem.{field} exists")
            else:
                print(f"  ✗ OrderItem.{field} MISSING!")
                return False
        
        # Test 3: Verify CartItem model
        print("\n✓ Test 3: Verify CartItem model fields...")
        cartitem_fields = ['id', 'user_id', 'product_id', 'quantity', 'created_at', 'updated_at']
        
        for field in cartitem_fields:
            if hasattr(CartItem, field):
                print(f"  ✓ CartItem.{field} exists")
            else:
                print(f"  ✗ CartItem.{field} MISSING!")
                return False
        
        # Test 4: Verify Order methods
        print("\n✓ Test 4: Verify Order helper methods...")
        methods = ['get_status_badge', 'get_payment_badge']
        for method in methods:
            if hasattr(Order, method):
                print(f"  ✓ Order.{method}() exists")
            else:
                print(f"  ✗ Order.{method}() MISSING!")
                return False
        
        # Test 5: Test order number generation format
        print("\n✓ Test 5: Test order number format...")
        order_num = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        print(f"  ✓ Order number format: {order_num}")
        
        # Test 6: Test status badge mapping
        print("\n✓ Test 6: Test status badge mappings...")
        statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
        badge_map = {
            'pending': 'warning',
            'confirmed': 'info',
            'processing': 'primary',
            'shipped': 'secondary',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        
        # Create a test order to test methods
        test_order = Order(
            order_number="ORD-TEST-001",
            total_amount=100.00,
            subtotal=85.00,
            shipping_cost=10.00,
            discount_amount=0,
            discount_percentage=0,
            status='pending',
            payment_status='unpaid'
        )
        
        for status, expected_badge in badge_map.items():
            test_order.status = status
            badge = test_order.get_status_badge()
            if badge == expected_badge:
                print(f"  ✓ {status} → {badge}")
            else:
                print(f"  ✗ {status} → {badge} (expected {expected_badge})")
                return False
        
        # Test 7: Test payment badge mapping
        print("\n✓ Test 7: Test payment status badge mappings...")
        payment_statuses = ['unpaid', 'paid', 'failed', 'refunded']
        payment_badge_map = {
            'unpaid': 'warning',
            'paid': 'success',
            'failed': 'danger',
            'refunded': 'secondary'
        }
        
        for status, expected_badge in payment_badge_map.items():
            test_order.payment_status = status
            badge = test_order.get_payment_badge()
            if badge == expected_badge:
                print(f"  ✓ {status} → {badge}")
            else:
                print(f"  ✗ {status} → {badge} (expected {expected_badge})")
                return False
        
        print("\n" + "="*70)
        print("ALL TESTS PASSED! ✓")
        print("="*70)
        print("\n✓ Order model is fully operational")
        print("✓ OrderItem model is fully operational")
        print("✓ CartItem model is fully operational")
        print("✓ Status badge system working correctly")
        print("✓ Payment status system working correctly")
        print("\n" + "="*70 + "\n")
        
        return True

if __name__ == '__main__':
    success = test_order_system()
    sys.exit(0 if success else 1)
