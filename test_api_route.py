"""
Test if the calculate-checkout endpoint works with proper encoding
"""
import sys
import os
import io

# Fix encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'e:\\python_projects\\digialhome')

try:
    from app import create_app
    import json
    
    app = create_app()
    
    print("\n[TEST] API Endpoint Registration")
    print("=" * 60)
    
    # Check if route is registered
    found = False
    for rule in app.url_map.iter_rules():
        if 'calculate' in str(rule):
            print(f"\n[SUCCESS] Found route: {rule}")
            print(f"  Methods: {rule.methods}")
            found = True
    
    if not found:
        print("\n[ERROR] Route not found in URL map")
        print("\nAll API routes:")
        for rule in app.url_map.iter_rules():
            if 'api' in str(rule) and not rule.rule.startswith('/static'):
                print(f"  {rule}")
    
    # Try to test with test client
    with app.test_client() as client:
        # Create a mock user session
        print("\n[TEST] Making request to endpoint...")
        response = client.post('/api/calculate-checkout',
            data=json.dumps({'shipping_method': 'standard'}),
            content_type='application/json'
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 401:
            print("  [OK] Returns 401 (requires login) - endpoint exists!")
        else:
            print(f"  Response: {response.get_json()}")

except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
