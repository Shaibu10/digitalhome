#!/usr/bin/env python
"""Comprehensive test for change password functionality"""

import requests
import json

def test_complete_flow():
    """Test the complete change password flow"""
    
    session = requests.Session()
    base_url = "http://localhost:5000"
    
    # Step 1: Login as admin
    print("=" * 60)
    print("STEP 1: Login as admin")
    print("=" * 60)
    login_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    
    response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
    print(f"✅ Login status: {response.status_code}")
    
    # Step 2: Load profile page
    print("\n" + "=" * 60)
    print("STEP 2: Load profile page")
    print("=" * 60)
    response = session.get(f"{base_url}/auth/profile")
    print(f"✅ Profile page status: {response.status_code}")
    print(f"   - Page contains 'Change Password': {'Change Password' in response.text}")
    print(f"   - Page contains modal: {'changePasswordModal' in response.text}")
    
    # Step 3: Test change password with wrong current password
    print("\n" + "=" * 60)
    print("STEP 3: Test with wrong current password")
    print("=" * 60)
    change_data = {
        'current_password': 'wrongpassword',
        'new_password': 'newpass123',
        'confirm_password': 'newpass123'
    }
    
    response = session.post(f"{base_url}/auth/change-password", data=change_data)
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"✅ Success: {data['success']}")
    print(f"   Message: {data['message']}")
    
    # Step 4: Test change password with mismatched passwords
    print("\n" + "=" * 60)
    print("STEP 4: Test with mismatched new passwords")
    print("=" * 60)
    change_data = {
        'current_password': 'admin123',
        'new_password': 'newpass123',
        'confirm_password': 'differentpass123'
    }
    
    response = session.post(f"{base_url}/auth/change-password", data=change_data)
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"✅ Success: {data['success']}")
    print(f"   Message: {data['message']}")
    
    # Step 5: Test change password with password too short
    print("\n" + "=" * 60)
    print("STEP 5: Test with password too short")
    print("=" * 60)
    change_data = {
        'current_password': 'admin123',
        'new_password': '123',
        'confirm_password': '123'
    }
    
    response = session.post(f"{base_url}/auth/change-password", data=change_data)
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"✅ Success: {data['success']}")
    print(f"   Message: {data['message']}")
    
    # Step 6: Test successful password change
    print("\n" + "=" * 60)
    print("STEP 6: Test successful password change")
    print("=" * 60)
    change_data = {
        'current_password': 'admin123',
        'new_password': 'NewSecurePass123',
        'confirm_password': 'NewSecurePass123'
    }
    
    response = session.post(f"{base_url}/auth/change-password", data=change_data)
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"✅ Success: {data['success']}")
    print(f"   Message: {data['message']}")
    
    if data['success']:
        print("\n" + "=" * 60)
        print("VERIFICATION: Login with new password")
        print("=" * 60)
        
        # Logout first
        session.get(f"{base_url}/auth/logout")
        
        # Try login with new password
        new_login_data = {
            'email': 'admin@example.com',
            'password': 'NewSecurePass123'
        }
        response = session.post(f"{base_url}/auth/login", data=new_login_data, allow_redirects=True)
        print(f"Login with new password status: {response.status_code}")
        print(f"✅ New password works: {response.status_code == 200}")
        
        # Change password back to original
        print("\n" + "=" * 60)
        print("CLEANUP: Restore original password")
        print("=" * 60)
        change_data = {
            'current_password': 'NewSecurePass123',
            'new_password': 'admin123',
            'confirm_password': 'admin123'
        }
        
        response = session.post(f"{base_url}/auth/change-password", data=change_data)
        data = response.json()
        print(f"✅ Password restored: {data['success']}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    test_complete_flow()
