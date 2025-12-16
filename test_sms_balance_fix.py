#!/usr/bin/env python
"""Test SMS Balance display fix"""

import os
import sys

# Suppress email warnings
os.environ['SHOW_EMAIL_WARNINGS'] = 'false'
os.environ['SHOW_SMS_WARNINGS'] = 'true'

from app import app
from sms.service import mNotifyService

def test_balance_fetch():
    """Test the balance fetching logic"""
    
    print("\n" + "="*70)
    print("SMS BALANCE FETCH TEST")
    print("="*70)
    
    service = mNotifyService()
    
    print("\n1. Testing mNotifyService initialization...")
    print(f"   - Enabled: {service.enabled}")
    print(f"   - API Key configured: {'Yes' if service.enabled else 'No (using demo mode)'}")
    print(f"   - Sender ID: {service.sender_id}")
    
    print("\n2. Fetching account balance...")
    with app.app_context():
        balance_info = service.get_account_balance()
    
    print(f"\n3. Response structure:")
    print(f"   - Status: {balance_info.get('status')}")
    print(f"   - Balance: {balance_info.get('balance', 'N/A')}")
    print(f"   - Message: {balance_info.get('message', 'N/A')}")
    print(f"   - Demo Mode: {balance_info.get('demo_mode', False)}")
    print(f"   - Code: {balance_info.get('code', 'N/A')}")
    
    print("\n4. Template rendering test:")
    if balance_info['status'] == 'success':
        print("   ✅ Card will show: GREEN (success)")
        if balance_info.get('demo_mode'):
            print("   ✅ With yellow warning styling (DEMO MODE)")
        else:
            print("   ✅ With blue info styling (PRODUCTION)")
    else:
        print("   ❌ Card will show: RED (error)")
        print(f"   - Error message displayed: {balance_info.get('message')}")
        print(f"   - Error code: {balance_info.get('code')}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")
    
    return balance_info['status'] == 'success'

if __name__ == '__main__':
    success = test_balance_fetch()
    sys.exit(0 if success else 1)
