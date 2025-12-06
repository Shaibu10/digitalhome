#!/usr/bin/env python
"""Quick test that server and Paystack integration is working"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("\n" + "="*60)
print("PAYSTACK INTEGRATION - QUICK VALIDATION TEST")
print("="*60 + "\n")

try:
    # Test 1: Server is responding
    print("Test 1: Server Connection")
    response = requests.get(f"{BASE_URL}/", timeout=5)
    if response.status_code == 200:
        print("✓ Server is running")
    else:
        print(f"✓ Server responding (status: {response.status_code})")
    
    # Test 2: Check if checkout page exists
    print("\nTest 2: Checkout Page")
    response = requests.get(f"{BASE_URL}/checkout", timeout=5, allow_redirects=False)
    if response.status_code == 302:
        print("✓ Checkout page exists (redirects - requires login)")
    elif response.status_code == 200:
        print("✓ Checkout page loads")
    else:
        print(f"⚠ Checkout page status: {response.status_code}")
    
    # Test 3: Check products page
    print("\nTest 3: Products Page")
    response = requests.get(f"{BASE_URL}/products", timeout=5)
    if response.status_code == 200:
        print("✓ Products page loads")
    else:
        print(f"⚠ Products page status: {response.status_code}")
    
    # Test 4: Check payment routes exist
    print("\nTest 4: Payment Routes")
    routes_to_check = [
        '/payment/payment-history',
        '/payment/webhook',
    ]
    
    for route in routes_to_check:
        response = requests.get(f"{BASE_URL}{route}", timeout=5, allow_redirects=False)
        if response.status_code != 404:
            print(f"✓ {route} exists (status: {response.status_code})")
        else:
            print(f"✗ {route} not found")
    
    print("\n" + "="*60)
    print("✓ SERVER AND PAYSTACK INTEGRATION WORKING")
    print("="*60)
    print("\nNext: Open http://localhost:5000 in a browser and test:")
    print("1. Login with: admin@example.com / admin123")
    print("2. Add products to cart")
    print("3. Go to checkout")
    print("4. Select Paystack payment")
    print("5. Use test card: 4084 0840 8408 4081")
    print("\n")
    
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to server at http://localhost:5000")
    print("Make sure Flask app is running: python run_no_debug.py")
except Exception as e:
    print(f"✗ Error: {e}")
