#!/usr/bin/env python
"""Test the change password functionality"""

import requests
import json

def test_change_password():
    """Test changing password via the profile page"""
    
    session = requests.Session()
    
    # Login as a regular user
    print("Logging in as test user...")
    login_url = "http://localhost:5000/auth/login"
    login_data = {
        'email': 'shaibu5278@gmail.com',
        'password': 'password123'
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=True)
    print(f"Login status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Login failed, trying admin account...")
        login_data = {
            'email': 'admin@example.com',
            'password': 'admin123'
        }
        response = session.post(login_url, data=login_data, allow_redirects=True)
        print(f"Admin login status: {response.status_code}")
    
    # Now test the change password endpoint
    print("\nTesting change password endpoint...")
    change_pw_url = "http://localhost:5000/auth/change-password"
    
    # Test 1: Try with current password (should fail - not real password)
    print("\n--- Test 1: Wrong current password ---")
    change_data = {
        'current_password': 'wrongpassword',
        'new_password': 'newpass123',
        'confirm_password': 'newpass123'
    }
    
    response = session.post(change_pw_url, data=change_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Try with mismatched new passwords
    print("\n--- Test 2: Mismatched new passwords ---")
    if login_data['email'] == 'admin@example.com':
        current = 'admin123'
    else:
        current = 'password123'
        
    change_data = {
        'current_password': current,
        'new_password': 'newpass123',
        'confirm_password': 'differentpass123'
    }
    
    response = session.post(change_pw_url, data=change_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Try with password too short
    print("\n--- Test 3: Password too short ---")
    change_data = {
        'current_password': current,
        'new_password': '123',
        'confirm_password': '123'
    }
    
    response = session.post(change_pw_url, data=change_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print("\n✅ All tests completed!")

if __name__ == '__main__':
    test_change_password()
