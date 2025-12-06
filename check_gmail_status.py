#!/usr/bin/env python
"""Test Gmail configuration status."""

import os

print("\n" + "=" * 60)
print("Gmail Configuration Status")
print("=" * 60)

# Check environment variables
enable_gmail = os.environ.get('ENABLE_GMAIL', 'false').lower() == 'true'
service_file = os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE', 'credentials.json')
delegated_user = os.environ.get('GMAIL_DELEGATED_USER', 'not set')

print(f"\n📋 Environment Variables:")
print(f"  ENABLE_GMAIL: {os.environ.get('ENABLE_GMAIL', 'not set')}")
print(f"  GOOGLE_SERVICE_ACCOUNT_FILE: {service_file}")
print(f"  GMAIL_DELEGATED_USER: {delegated_user}")

# Check if credentials file exists
import os.path
creds_exists = os.path.exists(service_file)
print(f"\n📁 File Check:")
print(f"  Credentials file exists: {'✅ Yes' if creds_exists else '❌ No'}")

# Try to load the Gmail service
print(f"\n🔧 Gmail Service Check:")
try:
    from emails.service import gmail_service
    if gmail_service.service:
        print(f"  Gmail API: ✅ ENABLED and initialized")
    else:
        print(f"  Gmail API: ⚠️ Disabled (using console logging)")
except Exception as e:
    print(f"  Gmail API: ❌ Error loading service: {e}")

print("\n" + "=" * 60)
print("To enable Gmail:")
print("  1. Set: $env:ENABLE_GMAIL = 'true'")
print("  2. Set: $env:GOOGLE_SERVICE_ACCOUNT_FILE = 'credentials.json'")
print("  3. Set: $env:GMAIL_DELEGATED_USER = 'your-email@gmail.com'")
print("  4. Place credentials.json in project root")
print("  5. Restart your terminal and app")
print("=" * 60 + "\n")
