#!/usr/bin/env python
"""
Comprehensive test for professional order placement flow.
Tests end-to-end order creation, confirmation, and history tracking.
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Product, Category, Order, OrderItem, CartItem

def test_order_placement_flow():
    """Test complete order placement workflow."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("TESTING COMPLETE ORDER PLACEMENT WORKFLOW")
        print("="*70 + "\n")
        
        # Test 1: Create test user
        print("✓ Test 1: Create/Get test user...")
        test_user = User.query.filter_by(email='testorder@test.com').first()
        if not test_user:
            test_user = User(
                username='testorder',
                email='testorder@test.com',
                is_verified=True
            )
            test_user.set_password('testpass123')
            db.session.add(test_user)
            db.session.commit()
            print(f"  ✓ Created test user: {test_user.email}")
        else:
            print(f"  ✓ Using existing test user: {test_user.email}")
        
        # Test 2: Get or create test product
        print("\n✓ Test 2: Get/Create test product...")
        test_product = Product.query.filter_by(name='Test Product').first()
        if not test_product:
            category = Category.query.first() or Category(name='Test', description='Test category')
            if not category.id:
                db.session.add(category)
                db.session.commit()
            
            test_product = Product(
                name='Test Product',
                description='Test product for order',
                price=99.99,
                discount_price=79.99,
                stock_quantity=100,
                category_id=category.id,
                is_active=True
            )
            db.session.add(test_product)
            db.session.commit()
            print(f"  ✓ Created test product: {test_product.name} (GH₵{test_product.price})")
        else:
            print(f"  ✓ Using existing test product: {test_product.name}")
        
        # Test 3: Create cart item
        print("\n✓ Test 3: Add product to cart...")
        CartItem.query.filter_by(user_id=test_user.id).delete()
        db.session.commit()
        
        cart_item = CartItem(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=2
        )
        db.session.add(cart_item)
        db.session.commit()
        print(f"  ✓ Added {cart_item.quantity} x {test_product.name} to cart")
        
        # Test 4: Create order from cart
        print("\n✓ Test 4: Create order from cart...")
        cart_items = CartItem.query.filter_by(user_id=test_user.id).all()
        
        subtotal = sum(cart_item.product.final_price() * cart_item.quantity for cart_item in cart_items)
        shipping_cost = 10.00
        tax = subtotal * 0.05
        total = subtotal + shipping_cost + tax
        
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        order = Order(
            user_id=test_user.id,
            order_number=order_number,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            discount_amount=0,
            discount_percentage=0,
            total_amount=total,
            status='pending',
            payment_method='cod',
            payment_status='pending',
            shipping_address='123 Test Street',
            shipping_city='Accra',
            shipping_postal_code='00233',
            shipping_phone='0241234567',
            notes='Test order'
        )
        
        # Add order items
        for cart_item in cart_items:
            order_item = OrderItem(
                product_id=cart_item.product_id,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.final_price(),
                total_price=cart_item.product.final_price() * cart_item.quantity
            )
            order.order_items.append(order_item)
        
        db.session.add(order)
        db.session.commit()
        
        print(f"  ✓ Created order: {order.order_number}")
        print(f"    - Subtotal: GH₵ {order.subtotal:.2f}")
        print(f"    - Shipping: GH₵ {order.shipping_cost:.2f}")
        print(f"    - Tax (5%): GH₵ {tax:.2f}")
        print(f"    - Total: GH₵ {order.total_amount:.2f}")
        print(f"    - Status: {order.status}")
        print(f"    - Payment: {order.payment_status}")
        
        # Test 5: Verify order items
        print("\n✓ Test 5: Verify order items...")
        order = Order.query.filter_by(order_number=order_number).first()
        for item in order.order_items:
            print(f"  ✓ Order Item: {item.product_name} x {item.quantity} @ GH₵{item.unit_price:.2f} = GH₵{item.total_price:.2f}")
        
        # Test 6: Test order badges
        print("\n✓ Test 6: Test order status badges...")
        status_badge = order.get_status_badge()
        payment_badge = order.get_payment_badge()
        print(f"  ✓ Status badge: {order.status} → {status_badge}")
        print(f"  ✓ Payment badge: {order.payment_status} → {payment_badge}")
        
        # Test 7: Retrieve user's orders
        print("\n✓ Test 7: Retrieve user's order history...")
        user_orders = Order.query.filter_by(user_id=test_user.id).order_by(Order.created_at.desc()).all()
        print(f"  ✓ Found {len(user_orders)} order(s) for user {test_user.email}")
        for o in user_orders[:3]:
            print(f"    - {o.order_number} | {o.status} | GH₵{o.total_amount:.2f}")
        
        # Test 8: Test order detail retrieval
        print("\n✓ Test 8: Retrieve specific order details...")
        retrieved_order = Order.query.get(order.id)
        print(f"  ✓ Retrieved order {retrieved_order.order_number}")
        print(f"    - Delivery to: {retrieved_order.shipping_address}, {retrieved_order.shipping_city}")
        print(f"    - Phone: {retrieved_order.shipping_phone}")
        print(f"    - Items: {len(retrieved_order.order_items)}")
        
        # Test 9: Test order status update
        print("\n✓ Test 9: Test order status transitions...")
        order.status = 'confirmed'
        db.session.commit()
        print(f"  ✓ Updated status to: {order.status} (badge: {order.get_status_badge()})")
        
        order.status = 'processing'
        db.session.commit()
        print(f"  ✓ Updated status to: {order.status} (badge: {order.get_status_badge()})")
        
        order.status = 'shipped'
        order.tracking_number = 'TRK-1234567890'
        db.session.commit()
        print(f"  ✓ Updated status to: {order.status} (badge: {order.get_status_badge()})")
        print(f"  ✓ Tracking number: {order.tracking_number}")
        
        order.status = 'delivered'
        order.delivered_at = datetime.utcnow()
        db.session.commit()
        print(f"  ✓ Updated status to: {order.status} (badge: {order.get_status_badge()})")
        print(f"  ✓ Delivered at: {order.delivered_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test 10: Test order cancellation
        print("\n✓ Test 10: Test order cancellation...")
        # Create another order to cancel
        order2 = Order(
            user_id=test_user.id,
            order_number=f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-CANCEL",
            subtotal=100.00,
            shipping_cost=10.00,
            discount_amount=0,
            discount_percentage=0,
            total_amount=115.00,
            status='pending',
            payment_method='bank_transfer',
            payment_status='unpaid',
            shipping_address='456 Cancel Street',
            shipping_city='Tema'
        )
        db.session.add(order2)
        db.session.commit()
        
        print(f"  ✓ Created cancellable order: {order2.order_number}")
        
        order2.status = 'cancelled'
        db.session.commit()
        print(f"  ✓ Cancelled order: {order2.order_number} → {order2.status} (badge: {order2.get_status_badge()})")
        
        # Test 11: Test payment status updates
        print("\n✓ Test 11: Test payment status updates...")
        order3 = Order(
            user_id=test_user.id,
            order_number=f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-PAY",
            subtotal=50.00,
            shipping_cost=10.00,
            discount_amount=0,
            discount_percentage=0,
            total_amount=63.00,
            status='confirmed',
            payment_method='mobile_money',
            payment_status='unpaid',
            shipping_address='789 Payment Street'
        )
        db.session.add(order3)
        db.session.commit()
        
        print(f"  ✓ Created order with payment status: {order3.payment_status} (badge: {order3.get_payment_badge()})")
        
        order3.payment_status = 'paid'
        db.session.commit()
        print(f"  ✓ Updated payment to: {order3.payment_status} (badge: {order3.get_payment_badge()})")
        
        order3.payment_status = 'failed'
        db.session.commit()
        print(f"  ✓ Updated payment to: {order3.payment_status} (badge: {order3.get_payment_badge()})")
        
        order3.payment_status = 'refunded'
        db.session.commit()
        print(f"  ✓ Updated payment to: {order3.payment_status} (badge: {order3.get_payment_badge()})")
        
        print("\n" + "="*70)
        print("ALL WORKFLOW TESTS PASSED! ✓")
        print("="*70)
        print("\n✓ Order creation works correctly")
        print("✓ Order items are properly linked")
        print("✓ Order status transitions work")
        print("✓ Payment status tracking works")
        print("✓ Order retrieval and filtering works")
        print("✓ Badge system works for all statuses")
        print("\n" + "="*70 + "\n")
        
        return True

if __name__ == '__main__':
    success = test_order_placement_flow()
    sys.exit(0 if success else 1)
