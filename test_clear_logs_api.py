#!/usr/bin/env python
"""Test the clear old logs API endpoint"""

import requests
import json
from datetime import datetime, timedelta

# Test the endpoint
def test_clear_logs_api():
    """Test clearing old logs via API"""
    
    # First, login to get a session
    session = requests.Session()
    
    # Login as admin
    login_url = "http://localhost:5000/auth/login"
    login_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    
    print("Logging in as admin...")
    response = session.post(login_url, data=login_data, allow_redirects=True)
    print(f"Login response status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    # Now try to clear old logs
    print("\nCalling clear old logs endpoint...")
    clear_url = "http://localhost:5000/admin/clear-old-logs"
    headers = {
        'Content-Type': 'application/json',
    }
    
    response = session.post(clear_url, headers=headers, json={})
    print(f"Clear logs response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response JSON: {json.dumps(data, indent=2)}")
            if data.get('success'):
                print("✅ Clear logs operation was successful!")
            else:
                print(f"❌ Clear logs failed: {data.get('message')}")
        except json.JSONDecodeError:
            print(f"❌ Response is not valid JSON: {response.text}")
    else:
        print(f"❌ API returned status {response.status_code}")
        print(f"Response: {response.text[:500]}")

if __name__ == '__main__':
    test_clear_logs_api()
