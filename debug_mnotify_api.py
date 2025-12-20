 #!/usr/bin/env python
"""Debug mNotify API endpoints to find working balance endpoint"""

import os
import requests

API_KEY = os.environ.get('MNOTIFY_API_KEY')
BASE_URL = "https://api.mnotify.com/api"

def test_endpoint(endpoint_name, method='GET', endpoint_path='', payload=None):
    """Test an API endpoint"""
    print(f"\n{'='*70}")
    print(f"Testing: {endpoint_name}")
    print(f"URL: {BASE_URL}{endpoint_path}")
    print(f"Method: {method}")
    print(f"API Key configured: {'Yes' if API_KEY else 'NO'}")
    print(f"{'='*70}")
    
    if not API_KEY:
        print("⚠️ MNOTIFY_API_KEY not configured - cannot test")
        return
    
    try:
        params = {'key': API_KEY}
        
        if method == 'GET':
            response = requests.get(f"{BASE_URL}{endpoint_path}", params=params, timeout=10)
        else:
            response = requests.post(f"{BASE_URL}{endpoint_path}", json=payload, params=params, timeout=10)
        
        print(f"\n📊 Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"\n📝 Body:")
        print(f"   {response.text[:500]}")  # First 500 chars
        
        try:
            json_resp = response.json()
            print(f"\n📦 Parsed JSON:")
            import json
            print(json.dumps(json_resp, indent=2)[:1000])  # First 1000 chars
        except:
            print("   (Could not parse as JSON)")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    print("\n🔍 mNotify API Endpoint Discovery\n")
    
    # Test possible balance endpoints
    test_endpoint("Account Balance (current)", 'GET', '/account/balance')
    test_endpoint("Credits Endpoint", 'GET', '/account/credits')
    test_endpoint("Account Info", 'GET', '/account/info')
    test_endpoint("Wallet", 'GET', '/account/wallet')
    
    print("\n" + "="*70)
    print("💡 TIP: If balance endpoint fails but SMS sending works,")
    print("   the balance might be included in the send response!")
    print("="*70 + "\n")
