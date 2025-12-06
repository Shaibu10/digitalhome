#!/usr/bin/env python
"""
Final verification test - confirms all order system components work together.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Product, Category, Order, OrderItem, CartItem

def verify_system():
    """Verify all components of the order system."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("FINAL ORDER & CART SYSTEM VERIFICATION")
        print("="*70 + "\n")
        
        checks_passed = 0
        checks_total = 0
        
        # Check 1: Database connection
        checks_total += 1
        print("✓ Check 1: Database connectivity...")
        try:
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            print("  ✓ Database connection successful")
            checks_passed += 1
        except Exception as e:
            print(f"  ✗ Database connection failed: {e}")
        
        # Check 2: All tables exist
        checks_total += 1
        print("\n✓ Check 2: All required tables exist...")
        required_tables = ['user', 'product', 'category', 'cart_item', 'order', 'order_item']
        all_tables_exist = True
        for table_name in required_tables:
            if table_name in db.metadata.tables:
                print(f"  ✓ {table_name} table exists")
            else:
                print(f"  ✗ {table_name} table MISSING!")
                all_tables_exist = False
        if all_tables_exist:
            checks_passed += 1
        
        # Check 3: Models instantiate correctly
        checks_total += 1
        print("\n✓ Check 3: Models instantiate without errors...")
        try:
            order = Order()
            order_item = OrderItem()
            cart_item = CartItem()
            print("  ✓ Order model instantiates")
            print("  ✓ OrderItem model instantiates")
            print("  ✓ CartItem model instantiates")
            checks_passed += 1
        except Exception as e:
            print(f"  ✗ Model instantiation failed: {e}")
        
        # Check 4: Required routes exist in view functions
        checks_total += 1
        print("\n✓ Check 4: Required route functions registered...")
        required_functions = [
            'checkout',
            'order_confirmation',
            'view_orders',
            'order_detail',
            'clear_cart'
        ]
        functions_exist = True
        for func_name in required_functions:
            if func_name in app.view_functions:
                print(f"  ✓ {func_name} function exists")
            else:
                print(f"  ✗ {func_name} function NOT FOUND!")
                functions_exist = False
        if functions_exist:
            checks_passed += 1
        
        # Check 5: Templates exist
        checks_total += 1
        print("\n✓ Check 5: Required templates exist...")
        required_templates = [
            'templates/cart.html',
            'templates/checkout.html',
            'templates/order_confirmation.html',
            'templates/order_history.html',
            'templates/order_detail.html'
        ]
        templates_exist = True
        for template_path in required_templates:
            full_path = os.path.join(os.path.dirname(__file__), template_path)
            if os.path.exists(full_path):
                print(f"  ✓ {template_path} exists")
            else:
                print(f"  ✗ {template_path} MISSING!")
                templates_exist = False
        if templates_exist:
            checks_passed += 1
        
        # Check 6: Test data can be created
        checks_total += 1
        print("\n✓ Check 6: Test data creation...")
        try:
            # Clean up test data
            User.query.filter_by(email='verify_test@test.com').delete()
            db.session.commit()
            
            # Create test user
            user = User(
                username='verify_test',
                email='verify_test@test.com',
                is_verified=True
            )
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()
            
            # Create test product
            cat = Category.query.first()
            if not cat:
                cat = Category(name='Test', description='Test')
                db.session.add(cat)
                db.session.commit()
            
            product = Product(
                name='Verify Test Product',
                price=50.00,
                stock_quantity=10,
                category_id=cat.id,
                is_active=True
            )
            db.session.add(product)
            db.session.commit()
            
            # Create test cart item
            cart = CartItem(user_id=user.id, product_id=product.id, quantity=1)
            db.session.add(cart)
            db.session.commit()
            
            # Create test order
            order = Order(
                user_id=user.id,
                order_number='ORD-VERIFY-TEST-001',
                subtotal=50.00,
                shipping_cost=10.00,
                discount_amount=0,
                discount_percentage=0,
                total_amount=63.00,
                status='pending',
                payment_method='cod',
                payment_status='unpaid',
                shipping_address='Test Address',
                shipping_city='Test City'
            )
            order.order_items.append(OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=1,
                unit_price=50.00,
                total_price=50.00
            ))
            db.session.add(order)
            db.session.commit()
            
            print("  ✓ User created successfully")
            print("  ✓ Product created successfully")
            print("  ✓ CartItem created successfully")
            print("  ✓ Order created successfully")
            checks_passed += 1
        except Exception as e:
            print(f"  ✗ Test data creation failed: {e}")
        
        # Check 7: Data retrieval
        checks_total += 1
        print("\n✓ Check 7: Data retrieval...")
        try:
            retrieved_user = User.query.filter_by(email='verify_test@test.com').first()
            retrieved_order = Order.query.filter_by(order_number='ORD-VERIFY-TEST-001').first()
            
            if retrieved_user and retrieved_order:
                print(f"  ✓ Retrieved user: {retrieved_user.email}")
                print(f"  ✓ Retrieved order: {retrieved_order.order_number}")
                print(f"  ✓ Order status: {retrieved_order.status}")
                print(f"  ✓ Order items: {len(retrieved_order.order_items)}")
                checks_passed += 1
            else:
                print("  ✗ Failed to retrieve test data")
        except Exception as e:
            print(f"  ✗ Data retrieval failed: {e}")
        
        # Check 8: Badge methods work
        checks_total += 1
        print("\n✓ Check 8: Badge generation methods...")
        try:
            test_order = Order.query.filter_by(order_number='ORD-VERIFY-TEST-001').first()
            status_badge = test_order.get_status_badge()
            payment_badge = test_order.get_payment_badge()
            
            if status_badge and payment_badge:
                print(f"  ✓ Status badge: {test_order.status} → {status_badge}")
                print(f"  ✓ Payment badge: {test_order.payment_status} → {payment_badge}")
                checks_passed += 1
            else:
                print("  ✗ Badge methods failed")
        except Exception as e:
            print(f"  ✗ Badge method test failed: {e}")
        
        # Check 9: Order status transitions work
        checks_total += 1
        print("\n✓ Check 9: Order status transitions...")
        try:
            test_order = Order.query.filter_by(order_number='ORD-VERIFY-TEST-001').first()
            
            # Test transitions
            test_order.status = 'confirmed'
            db.session.commit()
            print(f"  ✓ Updated to confirmed")
            
            test_order.status = 'shipped'
            test_order.tracking_number = 'TRK-VERIFY-123'
            db.session.commit()
            print(f"  ✓ Updated to shipped with tracking")
            
            test_order.status = 'delivered'
            db.session.commit()
            print(f"  ✓ Updated to delivered")
            
            checks_passed += 1
        except Exception as e:
            print(f"  ✗ Status transition failed: {e}")
        
        # Check 10: Query operations work
        checks_total += 1
        print("\n✓ Check 10: Database queries...")
        try:
            # Query by user
            user_orders = Order.query.filter_by(user_id=retrieved_user.id).all()
            print(f"  ✓ Found {len(user_orders)} order(s) for user")
            
            # Query by status
            pending_orders = Order.query.filter_by(status='pending').all()
            print(f"  ✓ Found {len(pending_orders)} pending order(s)")
            
            # Query with ordering
            recent = Order.query.order_by(Order.created_at.desc()).limit(1).all()
            print(f"  ✓ Found {len(recent)} recent order(s)")
            
            checks_passed += 1
        except Exception as e:
            print(f"  ✗ Query test failed: {e}")
        
        # Summary
        print("\n" + "="*70)
        print(f"VERIFICATION COMPLETE: {checks_passed}/{checks_total} checks passed")
        print("="*70)
        
        if checks_passed == checks_total:
            print("\n🎉 ALL SYSTEMS OPERATIONAL - READY FOR PRODUCTION 🎉\n")
            return True
        else:
            print(f"\n⚠️  {checks_total - checks_passed} check(s) failed - review above\n")
            return False

if __name__ == '__main__':
    success = verify_system()
    sys.exit(0 if success else 1)
