#!/usr/bin/env python
"""Verify Paystack Integration is Working Correctly"""

import sqlite3
import sys
from pathlib import Path

def check_environment():
    """Check .env configuration"""
    print("\n" + "="*60)
    print("1. ENVIRONMENT CONFIGURATION")
    print("="*60)
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        paystack_public = os.getenv('PAYSTACK_PUBLIC_KEY', '')
        paystack_secret = os.getenv('PAYSTACK_SECRET_KEY', '')
        
        print(f"✓ PAYSTACK_PUBLIC_KEY: {'✓ Set' if paystack_public else '✗ MISSING'}")
        if paystack_public:
            print(f"  - Starts with: {paystack_public[:10]}...")
            print(f"  - Is test key: {'✓ Yes' if paystack_public.startswith('pk_test_') else '✗ No (likely live)'}")
        
        print(f"✓ PAYSTACK_SECRET_KEY: {'✓ Set' if paystack_secret else '✗ MISSING'}")
        if paystack_secret:
            print(f"  - Starts with: {paystack_secret[:10]}...")
        
        callback_url = os.getenv('PAYSTACK_CALLBACK_URL', '')
        print(f"✓ PAYSTACK_CALLBACK_URL: {callback_url if callback_url else '✗ MISSING'}")
        
        return paystack_public and paystack_secret
    
    except Exception as e:
        print(f"✗ Error checking environment: {e}")
        return False


def check_database():
    """Check database tables and structure"""
    print("\n" + "="*60)
    print("2. DATABASE VERIFICATION")
    print("="*60)
    
    try:
        conn = sqlite3.connect('instance/digitalhome.db')
        cursor = conn.cursor()
        
        # Check for payment tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('payment', 'payment_log')")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"✓ payment table: {'✓ EXISTS' if 'payment' in tables else '✗ MISSING'}")
        print(f"✓ payment_log table: {'✓ EXISTS' if 'payment_log' in tables else '✗ MISSING'}")
        
        if 'payment' in tables:
            cursor.execute("PRAGMA table_info(payment)")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"\n  Payment table columns ({len(columns)}):")
            expected = ['id', 'order_id', 'customer_email', 'amount', 'paystack_reference', 'status']
            for col in expected:
                status = '✓' if col in columns else '✗'
                print(f"    {status} {col}")
        
        # Check for existing records
        cursor.execute("SELECT COUNT(*) FROM payment")
        payment_count = cursor.fetchone()[0]
        print(f"\n✓ Payment records in database: {payment_count}")
        
        if payment_count > 0:
            cursor.execute("SELECT id, status, amount FROM payment ORDER BY id DESC LIMIT 3")
            print("  Recent payments:")
            for row in cursor.fetchall():
                print(f"    - ID: {row[0]}, Status: {row[1]}, Amount: {row[2]}")
        
        # Check Order model has payment_status
        cursor.execute("PRAGMA table_info(\"order\")")
        order_columns = [row[1] for row in cursor.fetchall()]
        has_payment_status = 'payment_status' in order_columns
        print(f"\n✓ Order.payment_status field: {'✓ EXISTS' if has_payment_status else '✗ MISSING'}")
        
        conn.close()
        return 'payment' in tables and 'payment_log' in tables
    
    except Exception as e:
        print(f"✗ Error checking database: {e}")
        return False


def check_code_files():
    """Check required code files exist"""
    print("\n" + "="*60)
    print("3. CODE FILES VERIFICATION")
    print("="*60)
    
    files_to_check = {
        'payments/paystack_gateway.py': 'Paystack gateway service',
        'payments/routes.py': 'Payment routes',
        'templates/checkout.html': 'Checkout template',
        'templates/payment_status.html': 'Payment status template',
        'templates/payment_history.html': 'Payment history template',
        'models.py': 'Database models',
        'app.py': 'Main application',
        'config.py': 'Configuration',
    }
    
    all_exist = True
    for file_path, description in files_to_check.items():
        exists = Path(file_path).exists()
        status = '✓' if exists else '✗'
        print(f"{status} {description:.<40} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist


def check_imports():
    """Check if imports work"""
    print("\n" + "="*60)
    print("4. PYTHON IMPORTS VERIFICATION")
    print("="*60)
    
    try:
        print("✓ Importing Payment model...", end=' ')
        from models import Payment
        print("✓ Success")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    try:
        print("✓ Importing PaymentLog model...", end=' ')
        from models import PaymentLog
        print("✓ Success")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    try:
        print("✓ Importing PaystackGateway...", end=' ')
        from payments.paystack_gateway import PaystackGateway
        print("✓ Success")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    try:
        print("✓ Importing payment routes...", end=' ')
        from payments.routes import payment_bp
        print("✓ Success")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    return True


def check_templates():
    """Check template files have required content"""
    print("\n" + "="*60)
    print("5. TEMPLATE CONTENT VERIFICATION")
    print("="*60)
    
    checks = {
        'templates/checkout.html': [
            'payment_paystack',
            'js.paystack.co',
            'handlePaystackCheckout',
            'PAYSTACK_PUBLIC_KEY'
        ],
        'templates/payment_status.html': [
            'payment_status',
            'Payment Successful',
            'Payment Failed'
        ],
        'templates/payment_history.html': [
            'payment_history',
            'Payment History',
            'paystack_reference'
        ]
    }
    
    all_good = True
    for file_path, required_strings in checks.items():
        print(f"\n✓ {file_path}:")
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            for check_str in required_strings:
                if check_str in content:
                    print(f"  ✓ Contains '{check_str}'")
                else:
                    print(f"  ✗ Missing '{check_str}'")
                    all_good = False
        
        except Exception as e:
            print(f"  ✗ Error reading file: {e}")
            all_good = False
    
    return all_good


def check_app_routes():
    """Check if payment routes are registered"""
    print("\n" + "="*60)
    print("6. APPLICATION ROUTES VERIFICATION")
    print("="*60)
    
    try:
        from app import app
        
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            if 'payment' in rule.rule:
                routes.append(f"{rule.rule} [{','.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
        
        expected_routes = [
            '/payment/initiate',
            '/payment/verify',
            '/payment/paystack-callback',
            '/payment/webhook',
            '/payment/payment-history',
            '/payment/status',
        ]
        
        print(f"✓ Payment routes found: {len(routes)}")
        for route in sorted(routes):
            print(f"  ✓ {route}")
        
        for expected in expected_routes:
            found = any(expected in route for route in routes)
            status = '✓' if found else '✗'
            print(f"{status} {expected}")
        
        # Check payment_confirmed route
        payment_confirmed = any('payment-confirmed' in rule.rule for rule in app.url_map.iter_rules())
        print(f"{'✓' if payment_confirmed else '✗'} /payment-confirmed/<reference>")
        
        return len(routes) >= 6
    
    except Exception as e:
        print(f"✗ Error checking routes: {e}")
        return False


def main():
    """Run all verification checks"""
    print("\n" + "█"*60)
    print("█  PAYSTACK INTEGRATION VERIFICATION SCRIPT")
    print("█"*60)
    
    results = {
        'Environment': check_environment(),
        'Database': check_database(),
        'Code Files': check_code_files(),
        'Python Imports': check_imports(),
        'Template Content': check_templates(),
        'App Routes': check_app_routes(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for check_name, passed in results.items():
        status = '✓ PASS' if passed else '✗ FAIL'
        print(f"{status}: {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL CHECKS PASSED - System is ready for testing!")
    else:
        print("✗ Some checks failed - Please review the issues above")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
