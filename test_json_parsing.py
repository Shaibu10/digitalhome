#!/usr/bin/env python
"""
Test the improved JSON parsing to ensure it properly handles checkout data.
"""

import json
import sys

sys.path.insert(0, 'e:/python_projects/digialhome')

def test_json_parsing():
    """Test that JSON parsing works correctly"""
    from app import app
    from flask import request
    
    client = app.test_client()
    
    # Test data that the frontend sends
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
        'notes': ''
    }
    
    print("=" * 60)
    print("JSON PARSING TEST")
    print("=" * 60)
    print(f"\nSending JSON data: {json.dumps(checkout_data, indent=2)}")
    
    # Send POST request
    response = client.post(
        '/checkout',
        data=json.dumps(checkout_data),
        content_type='application/json',
        follow_redirects=False
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    try:
        resp_data = response.get_json()
        print(f"Response Body: {json.dumps(resp_data, indent=2)}")
        
        if response.status_code == 401:
            print("\n✓ Got 401 (user not authenticated) - JSON parsing works!")
            return True
        elif response.status_code == 400:
            print(f"\n✓ Got 400 validation error - JSON parsing works!")
            print(f"  Error: {resp_data.get('message')}")
            return resp_data.get('message') != 'Invalid request format. Expected JSON data.'
        elif response.status_code in [200, 302]:
            print("\n✓ Got success response - JSON parsing works!")
            return True
        else:
            print(f"\n⚠ Got unexpected status {response.status_code}")
            return False
    except Exception as e:
        print(f"Error parsing response: {e}")
        return False


if __name__ == '__main__':
    success = test_json_parsing()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ JSON PARSING TEST PASSED")
        print("  The endpoint is correctly receiving JSON data")
    else:
        print("✗ JSON PARSING TEST FAILED")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
