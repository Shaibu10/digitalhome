#!/usr/bin/env python
"""
Quick Paystack Integration Verification
Tests without needing Flask server running
"""

import sqlite3
import os

GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(70)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def verify_database():
    """Verify database integrity"""
    print_header("PAYSTACK DATABASE VERIFICATION")
    
    db_path = 'instance/digitalhome.db'
    if not os.path.exists(db_path):
        print_error(f"Database not found at {db_path}")
        return False
    
    print_success(f"Database exists: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check all required tables
        required_tables = {
            'user': ['id', 'username', 'email'],
            'order': ['id', 'user_id', 'payment_status', 'total_amount'],
            'payment': ['id', 'order_id', 'customer_email', 'paystack_reference', 'status', 'amount'],
            'payment_log': ['id', 'payment_id', 'action', 'timestamp']
        }
        
        for table, required_cols in required_tables.items():
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cursor.fetchone():
                print_error(f"Table '{table}' not found")
                return False
            
            cursor.execute(f"PRAGMA table_info([{table}])")
            cols = {col[1]: col for col in cursor.fetchall()}
            
            for col in required_cols:
                if col not in cols:
                    print_error(f"Table '{table}' missing column '{col}'")
                    return False
            
            print_success(f"Table '{table}' verified ({len(cols)} columns)")
        
        conn.close()
        return True
    except Exception as e:
        print_error(f"Database verification failed: {e}")
        return False

def verify_files():
    """Verify required files exist"""
    print_header("FILE STRUCTURE VERIFICATION")
    
    required_files = {
        'app.py': 'Main application',
        'models.py': 'Database models',
        'config.py': 'Configuration',
        '.env': 'Environment variables',
        'templates/checkout.html': 'Checkout template',
        'templates/payment_status.html': 'Payment status template',
        'templates/payment_history.html': 'Payment history template',
        'payments/paystack_gateway.py': 'Paystack gateway',
        'payments/routes.py': 'Payment routes',
    }
    
    all_exist = True
    for filepath, description in required_files.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print_success(f"{filepath:40} ({description}) [{size} bytes]")
        else:
            print_error(f"{filepath:40} NOT FOUND")
            all_exist = False
    
    return all_exist

def verify_checkout_html():
    """Verify checkout template has Paystack integration"""
    print_header("CHECKOUT TEMPLATE VERIFICATION")
    
    try:
        with open('templates/checkout.html', 'r') as f:
            content = f.read()
        
        checks = {
            'Paystack payment option': ('id="payment_paystack"', '<input'),
            'Paystack.js library': ('js.paystack.co', '<script'),
            'Paystack popup handler': ('PaystackPop', 'function'),
            'Payment method handler': ('handlePaystackCheckout', 'function'),
            'Public key variable': ('PAYSTACK_PUBLIC_KEY', 'var'),
        }
        
        passed = 0
        for check_name, (check_str, context) in checks.items():
            if check_str in content:
                print_success(f"✓ {check_name}")
                passed += 1
            else:
                print_error(f"✗ {check_name} NOT FOUND")
        
        print(f"\n{BLUE}Result: {passed}/{len(checks)} checks passed{RESET}")
        return passed == len(checks)
    except Exception as e:
        print_error(f"Failed to verify checkout template: {e}")
        return False

def verify_app_checkout_route():
    """Verify app.py has Paystack handling"""
    print_header("APP.PY CHECKOUT ROUTE VERIFICATION")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        checks = {
            'Payment model import': 'from models import',
            'Paystack gateway import': 'PaystackGateway',
            'Paystack payment method check': "payment_method == 'paystack'",
            'Payment record creation': 'Payment(order_id=',
            'PaymentLog creation': 'PaymentLog(',
            'UUID generation': 'import uuid',
        }
        
        passed = 0
        for check_name, check_str in checks.items():
            if check_str in content:
                print_success(f"✓ {check_name}")
                passed += 1
            else:
                print_error(f"✗ {check_name} NOT FOUND")
        
        print(f"\n{BLUE}Result: {passed}/{len(checks)} checks passed{RESET}")
        return passed == len(checks)
    except Exception as e:
        print_error(f"Failed to verify app.py: {e}")
        return False

def verify_paystack_gateway():
    """Verify Paystack gateway file"""
    print_header("PAYSTACK GATEWAY VERIFICATION")
    
    try:
        with open('payments/paystack_gateway.py', 'r') as f:
            content = f.read()
        
        checks = {
            'PaystackGateway class': 'class PaystackGateway',
            'initialize_payment method': 'def initialize_payment',
            'verify_payment method': 'def verify_payment',
            'verify_signature method': 'def verify_signature',
            'HMAC-SHA512': 'hmac.sha512',
        }
        
        passed = 0
        for check_name, check_str in checks.items():
            if check_str in content:
                print_success(f"✓ {check_name}")
                passed += 1
            else:
                print_error(f"✗ {check_name} NOT FOUND")
        
        print(f"\n{BLUE}Result: {passed}/{len(checks)} checks passed{RESET}")
        return passed == len(checks)
    except Exception as e:
        print_error(f"Failed to verify Paystack gateway: {e}")
        return False

def verify_payment_routes():
    """Verify payment routes file"""
    print_header("PAYMENT ROUTES VERIFICATION")
    
    try:
        with open('payments/routes.py', 'r') as f:
            content = f.read()
        
        routes = [
            ('/payment/initiate', 'route for payment initialization'),
            ('/payment/verify/<reference>', 'route for verification'),
            ('/payment/paystack-callback', 'callback handler'),
            ('/payment/webhook', 'webhook endpoint'),
            ('/payment/payment-history', 'payment history view'),
            ('/payment/status/<payment_id>', 'status check'),
        ]
        
        passed = 0
        for route, description in routes:
            if route in content or route.replace('<', '').replace('>', '') in content:
                print_success(f"✓ {route:30} - {description}")
                passed += 1
            else:
                print_error(f"✗ {route:30} - NOT FOUND")
        
        print(f"\n{BLUE}Result: {passed}/{len(routes)} routes verified{RESET}")
        return passed == len(routes)
    except Exception as e:
        print_error(f"Failed to verify payment routes: {e}")
        return False

def verify_env_config():
    """Verify .env has Paystack config"""
    print_header("ENVIRONMENT CONFIGURATION VERIFICATION")
    
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        checks = {
            'PAYSTACK_PUBLIC_KEY': 'pk_test_',
            'PAYSTACK_SECRET_KEY': 'sk_test_',
            'PAYSTACK_CALLBACK_URL': 'localhost:5000',
        }
        
        passed = 0
        for key, pattern in checks.items():
            if key in env_content and pattern in env_content:
                print_success(f"✓ {key} configured (test environment)")
                passed += 1
            elif key in env_content:
                print_error(f"✗ {key} exists but missing {pattern}")
            else:
                print_error(f"✗ {key} NOT FOUND")
        
        print(f"\n{BLUE}Result: {passed}/{len(checks)} environment variables verified{RESET}")
        return passed == len(checks)
    except Exception as e:
        print_error(f"Failed to verify .env: {e}")
        return False

def main():
    """Run all verifications"""
    print_header("PAYSTACK INTEGRATION - COMPREHENSIVE VERIFICATION")
    
    verifications = [
        ("Database Structure", verify_database),
        ("File Structure", verify_files),
        ("Environment Config", verify_env_config),
        ("Checkout Template", verify_checkout_html),
        ("App.py Route Handler", verify_app_checkout_route),
        ("Paystack Gateway", verify_paystack_gateway),
        ("Payment Routes", verify_payment_routes),
    ]
    
    results = {}
    for name, func in verifications:
        try:
            results[name] = func()
        except Exception as e:
            print_error(f"Verification '{name}' failed: {e}")
            results[name] = False
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"{status:20} {name}")
    
    print(f"\n{BOLD}Total: {passed}/{total} verifications passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}{BOLD}✓ ALL VERIFICATIONS PASSED - System is 100% ready!{RESET}\n")
        print("Next steps:")
        print("1. Start Flask app: python run.py")
        print("2. Login with: admin@example.com / admin123")
        print("3. Add products to cart")
        print("4. Proceed to checkout")
        print("5. Select Paystack payment option")
        print("6. Use test card: 4084 0840 8408 4081")
        print("7. Complete payment and verify database")
        return 0
    else:
        print(f"{RED}{BOLD}⚠ {total - passed} verification(s) failed - Review above{RESET}\n")
        return 1

if __name__ == '__main__':
    exit(main())
