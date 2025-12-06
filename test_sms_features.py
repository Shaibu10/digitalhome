#!/usr/bin/env python
"""
SMS Feature Test Script
Tests all SMS functionality without requiring a UI
"""
import requests
import json
from time import sleep

BASE_URL = "http://127.0.0.1:5000"

def test_sms_features():
    print("=" * 60)
    print("SMS FEATURE TEST SUITE")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. Login as admin
    print("\n1. Testing Admin Login...")
    login_response = session.post(
        f"{BASE_URL}/auth/login",
        data={
            'email': 'admin@example.com',
            'password': 'admin123'
        },
        allow_redirects=True
    )
    
    if login_response.status_code == 200:
        print("   ✅ Admin login successful")
    else:
        print(f"   ❌ Login failed: {login_response.status_code}")
        return
    
    # 2. Test SMS Dashboard
    print("\n2. Testing SMS Dashboard...")
    dashboard_response = session.get(f"{BASE_URL}/admin/sms/")
    if dashboard_response.status_code == 200:
        print("   ✅ SMS dashboard accessible")
    else:
        print(f"   ❌ Dashboard access failed: {dashboard_response.status_code}")
    
    # 3. Test Create SMS Template
    print("\n3. Testing SMS Template Creation...")
    template_data = {
        'name': 'Order Confirmation',
        'category': 'orders',
        'description': 'Sent when order is confirmed',
        'content': 'Your order #{order_id} has been confirmed. Delivery expected: {delivery_date}'
    }
    template_response = session.post(
        f"{BASE_URL}/admin/sms/templates/create",
        data=template_data
    )
    if template_response.status_code in [200, 302]:
        print("   ✅ Template creation endpoint accessible")
    else:
        print(f"   ⚠️  Template creation response: {template_response.status_code}")
    
    # 4. Test Templates List
    print("\n4. Testing SMS Templates List...")
    templates_response = session.get(f"{BASE_URL}/admin/sms/templates")
    if templates_response.status_code == 200:
        print("   ✅ Templates list accessible")
    else:
        print(f"   ❌ Templates list failed: {templates_response.status_code}")
    
    # 5. Test Campaign Creation Page
    print("\n5. Testing Campaign Creation Page...")
    campaign_page = session.get(f"{BASE_URL}/admin/sms/campaigns/create")
    if campaign_page.status_code == 200:
        print("   ✅ Campaign creation page accessible")
    else:
        print(f"   ❌ Campaign page failed: {campaign_page.status_code}")
    
    # 6. Test Campaigns List
    print("\n6. Testing Campaigns List...")
    campaigns_list = session.get(f"{BASE_URL}/admin/sms/campaigns")
    if campaigns_list.status_code == 200:
        print("   ✅ Campaigns list accessible")
    else:
        print(f"   ❌ Campaigns list failed: {campaigns_list.status_code}")
    
    # 7. Test Activity Logs
    print("\n7. Testing Activity Logs...")
    logs_response = session.get(f"{BASE_URL}/admin/sms/activity")
    if logs_response.status_code == 200:
        print("   ✅ Activity logs accessible")
    else:
        print(f"   ⚠️  Activity logs response: {logs_response.status_code}")
    
    # 8. Test Blacklist Management
    print("\n8. Testing Blacklist Management...")
    blacklist_response = session.get(f"{BASE_URL}/admin/sms/blacklist")
    if blacklist_response.status_code == 200:
        print("   ✅ Blacklist management accessible")
    else:
        print(f"   ⚠️  Blacklist response: {blacklist_response.status_code}")
    
    # 9. Test API Endpoints
    print("\n9. Testing API Endpoints...")
    api_users = session.get(f"{BASE_URL}/admin/sms/api/users?search=")
    if api_users.status_code == 200:
        print("   ✅ User search API accessible")
        try:
            users_data = api_users.json()
            print(f"   ℹ️  Found {len(users_data.get('users', []))} users")
        except:
            pass
    else:
        print(f"   ⚠️  API response: {api_users.status_code}")
    
    print("\n" + "=" * 60)
    print("SMS FEATURE TEST COMPLETE")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Set MNOTIFY_API_KEY environment variable for real SMS sending")
    print("2. Access SMS dashboard at: http://localhost:5000/admin/sms/")
    print("3. Create SMS templates")
    print("4. Send individual or bulk SMS messages")
    print("5. Monitor delivery in Activity Logs")

if __name__ == '__main__':
    test_sms_features()
