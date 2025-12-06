#!/usr/bin/env python
"""
Test script to verify the HTTP 415 fix for POST endpoints.
This simulates frontend form submission with JSON data.
"""

import json
import sys

# Add project to path
sys.path.insert(0, 'e:/python_projects/digialhome')

def test_checkout_endpoint():
    """Test the checkout endpoint with JSON content-type"""
    from app import app
    
    client = app.test_client()
    
    # Test data that the frontend would send
    checkout_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'address': '123 Test St',
        'city': 'Accra',
        'postal_code': '00000',
        'payment_method': 'cod',
        'shipping_method': 'standard',
        'notes': 'Please deliver in the morning'
    }
    
    print("Testing POST /checkout with JSON data...")
    print(f"Sending: {json.dumps(checkout_data, indent=2)}")
    
    # Send POST request with application/json content-type
    response = client.post(
        '/checkout',
        data=json.dumps(checkout_data),
        content_type='application/json',
        follow_redirects=False
    )
    
    print(f"\nResponse Status Code: {response.status_code}")
    
    # Check if we get a 415 error
    if response.status_code == 415:
        print("❌ ERROR: Got HTTP 415 - Fix did not work!")
        print(f"Response: {response.data}")
        return False
    elif response.status_code == 401:
        print("✓ Got 401 Unauthorized (expected - user not logged in)")
        print("  This is correct! The endpoint is working and validating auth.")
        return True
    elif response.status_code == 302:
        print("✓ Got 302 Redirect (expected - redirected to login)")
        print("  This is correct! The endpoint is working and validating auth.")
        return True
    elif response.status_code in [200, 400]:
        print(f"✓ Got {response.status_code} response")
        try:
            data = response.get_json()
            print(f"  Response: {json.dumps(data, indent=2)}")
        except:
            print(f"  Response (not JSON): {response.data}")
        return True
    else:
        print(f"⚠ Got status {response.status_code}")
        print(f"Response: {response.data}")
        return response.status_code != 415


if __name__ == '__main__':
    print("=" * 60)
    print("HTTP 415 FIX VERIFICATION TEST")
    print("=" * 60)
    
    success = test_checkout_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ TEST PASSED - Fix is working correctly!")
        print("  POST endpoints no longer return HTTP 415")
    else:
        print("✗ TEST FAILED - HTTP 415 error still occurring")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
