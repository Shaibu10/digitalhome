#!/usr/bin/env python
"""
DigitalHome - Paystack Integration Test Suite
Comprehensive testing of Paystack payment integration
"""

import os
import sys
from datetime import datetime

print("\n" + "="*70)
print(" 🧪 PAYSTACK INTEGRATION - COMPREHENSIVE TEST SUITE")
print("="*70 + "\n")

# Test 1: Import all modules
print("TEST 1: Module Imports")
print("-" * 70)
try:
    from app import app, db
    from models import User, Order, OrderItem, Payment, PaymentLog
    from payments.paystack_gateway import PaystackGateway
    from payments.routes import payment_bp
    print("✓ All modules imported successfully")
    print(f"  - Flask app: {app}")
    print(f"  - Database: {db}")
    print(f"  - Payment models: Payment, PaymentLog")
    print(f"  - Paystack gateway: {PaystackGateway}")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Database context
print("\n\nTEST 2: Database Context")
print("-" * 70)
try:
    with app.app_context():
        # Check if tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        payment_tables = ['payment', 'payment_log']
        missing = [t for t in payment_tables if t not in tables]
        
        if not missing:
            print(f"✓ Database tables found: {payment_tables}")
            print(f"  Total tables in database: {len(tables)}")
            
            # Get payment table columns
            payment_cols = inspector.get_columns('payment')
            print(f"  Payment table columns ({len(payment_cols)}):")
            for col in payment_cols:
                print(f"    - {col['name']}: {col['type']}")
        else:
            print(f"✗ Missing tables: {missing}")
except Exception as e:
    print(f"✗ Database check failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Paystack Gateway Configuration
print("\n\nTEST 3: Paystack Gateway Configuration")
print("-" * 70)
try:
    with app.app_context():
        gateway = PaystackGateway()
        
        # Check configuration
        if gateway.public_key:
            print(f"✓ Public Key: {gateway.public_key[:20]}...")
            print(f"  Is test key: {'pk_test_' in gateway.public_key}")
        else:
            print("✗ Public Key not configured")
        
        if gateway.secret_key:
            print(f"✓ Secret Key: {gateway.secret_key[:20]}...")
            print(f"  Is test key: {'sk_test_' in gateway.secret_key}")
        else:
            print("✗ Secret Key not configured")
        
        print(f"✓ Callback URL: {gateway.callback_url}")
except Exception as e:
    print(f"✗ Gateway configuration failed: {e}")

# Test 4: Create test user and order
print("\n\nTEST 4: Create Test User and Order")
print("-" * 70)
try:
    with app.app_context():
        # Create test user
        test_email = f"test_{datetime.now().timestamp()}@digitalhome.test"
        test_user = User.query.filter_by(email=test_email).first()
        
        if not test_user:
            test_user = User(
                username=f"testuser_{int(datetime.now().timestamp())}",
                email=test_email,
                is_verified=True
            )
            test_user.set_password('testpass123')
            db.session.add(test_user)
            db.session.commit()
            print(f"✓ Created test user: {test_email}")
        else:
            print(f"✓ Using existing test user: {test_email}")
        
        # Create test order
        test_order = Order(
            user_id=test_user.id,
            order_number=f"ORD-{int(datetime.now().timestamp())}",
            total_amount=100.0,
            subtotal=100.0,
            shipping_cost=0,
            discount_amount=0,
            status='pending',
            payment_status='unpaid',
            payment_method='paystack'
        )
        db.session.add(test_order)
        db.session.commit()
        
        print(f"✓ Created test order: {test_order.order_number}")
        print(f"  Order ID: {test_order.id}")
        print(f"  Amount: GH₵ {test_order.total_amount}")
        print(f"  Status: {test_order.status}")
        print(f"  Payment Status: {test_order.payment_status}")
        
except Exception as e:
    print(f"✗ Test user/order creation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Create Payment Record
print("\n\nTEST 5: Create Payment Record")
print("-" * 70)
try:
    with app.app_context():
        # Get the test order we just created
        test_orders = Order.query.order_by(Order.id.desc()).limit(1).all()
        if test_orders:
            test_order = test_orders[0]
            
            # Create payment record
            payment = Payment(
                order_id=test_order.id,
                customer_email=test_order.user.email,
                customer_phone='+233123456789',
                amount=test_order.total_amount,
                currency='GHS',
                paystack_reference=f"TEST-{test_order.id}-{int(datetime.now().timestamp())}",
                payment_method='card',
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            
            print(f"✓ Created payment record: {payment.paystack_reference}")
            print(f"  Payment ID: {payment.id}")
            print(f"  Amount: GH₵ {payment.amount}")
            print(f"  Status: {payment.status}")
            print(f"  Created: {payment.initiated_at}")
            
            # Test 6: Create PaymentLog Entry
            print("\n\nTEST 6: Create PaymentLog Entry")
            print("-" * 70)
            try:
                log = PaymentLog(
                    payment_id=payment.id,
                    action='initiated',
                    details='Payment initiated with reference: ' + payment.paystack_reference
                )
                db.session.add(log)
                db.session.commit()
                
                print(f"✓ Created payment log entry: {log.action}")
                print(f"  Log ID: {log.id}")
                print(f"  Payment ID: {log.payment_id}")
                print(f"  Details: {log.details}")
                print(f"  Timestamp: {log.timestamp}")
                
            except Exception as e:
                print(f"✗ PaymentLog creation failed: {e}")
        else:
            print("✗ No test orders found")
            
except Exception as e:
    print(f"✗ Payment record creation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Query Payment Records
print("\n\nTEST 7: Query Payment Records")
print("-" * 70)
try:
    with app.app_context():
        payments = Payment.query.all()
        print(f"✓ Total payments in database: {len(payments)}")
        
        if payments:
            latest = payments[-1]
            print(f"\n  Latest Payment:")
            print(f"    - ID: {latest.id}")
            print(f"    - Reference: {latest.paystack_reference}")
            print(f"    - Amount: GH₵ {latest.amount}")
            print(f"    - Status: {latest.status}")
            print(f"    - Order: #{latest.order_id}")
            
            # Check associated logs
            logs = PaymentLog.query.filter_by(payment_id=latest.id).all()
            print(f"    - Log entries: {len(logs)}")
            for log in logs:
                print(f"      • {log.action}: {log.details}")
except Exception as e:
    print(f"✗ Query failed: {e}")

# Test 8: Check routes
print("\n\nTEST 8: Flask Routes")
print("-" * 70)
try:
    with app.app_context():
        routes = []
        for rule in app.url_map.iter_rules():
            if 'payment' in rule.rule or 'checkout' in rule.rule or rule.rule == '/':
                routes.append({
                    'rule': rule.rule,
                    'methods': list(rule.methods - {'OPTIONS', 'HEAD'}),
                    'endpoint': rule.endpoint
                })
        
        if routes:
            print(f"✓ Found {len(routes)} relevant routes:")
            for route in sorted(routes, key=lambda x: x['rule']):
                methods = ', '.join(sorted(route['methods']))
                print(f"  - {route['rule']:40} [{methods}]")
        else:
            print("✗ No relevant routes found")
            
except Exception as e:
    print(f"✗ Route check failed: {e}")

# Final Summary
print("\n\n" + "="*70)
print(" ✅ TEST SUITE COMPLETE")
print("="*70 + "\n")
print("Integration Status: READY FOR TESTING")
print("\nNext Steps:")
print("  1. Start Flask server: python run.py")
print("  2. Navigate to http://127.0.0.1:5000/checkout")
print("  3. Test payment flow with test card: 4084 0840 8408 4081")
print("  4. Verify payment records in database")
print("\n")
