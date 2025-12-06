#!/usr/bin/env python
"""Test the change password functionality - debug version"""

import requests

def test_change_password():
    """Test changing password via the profile page"""
    
    session = requests.Session()
    
    # Login as admin
    print("Logging in as admin...")
    login_url = "http://localhost:5000/auth/login"
    login_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=True)
    print(f"Login status: {response.status_code}")
    
    # Test the change password endpoint
    print("\nTesting change password endpoint...")
    change_pw_url = "http://localhost:5000/auth/change-password"
    
    change_data = {
        'current_password': 'wrongpassword',
        'new_password': 'newpass123',
        'confirm_password': 'newpass123'
    }
    
    response = session.post(change_pw_url, data=change_data)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Text: {response.text[:500]}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

if __name__ == '__main__':
    test_change_password()
