#!/usr/bin/env python
"""
Set up Gmail environment variables permanently in Windows

This script will set the required environment variables so Gmail API works.
Run this ONCE and you're done!
"""

import subprocess
import os
import sys

# Service account email from your credentials.json
SERVICE_ACCOUNT_EMAIL = "digitalhome-mailer@digitalhome-email.iam.gserviceaccount.com"

print("\n" + "=" * 70)
print("🔧 Setting up Gmail API Environment Variables")
print("=" * 70)

print(f"\n📧 Service Account: {SERVICE_ACCOUNT_EMAIL}")
print("📁 Credentials File: credentials.json")
print("✅ Gmail API: Will be enabled")

# Check if running as administrator
is_admin = False
try:
    import ctypes
    is_admin = ctypes.windll.shell.IsUserAnAdmin()
except:
    pass

if not is_admin:
    print("\n⚠️ WARNING: This script needs to run as Administrator!")
    print("   Please run PowerShell as Administrator and try again.")
    print("\nTo do this:")
    print("  1. Press Windows key")
    print("  2. Type 'PowerShell'")
    print("  3. Right-click 'Windows PowerShell'")
    print("  4. Click 'Run as Administrator'")
    print("  5. Run this script again")
    sys.exit(1)

print("\n" + "=" * 70)
print("Setting environment variables...")
print("=" * 70)

try:
    # Set environment variables
    os.system(f'setx ENABLE_GMAIL true')
    os.system(f'setx GOOGLE_SERVICE_ACCOUNT_FILE credentials.json')
    os.system(f'setx GMAIL_DELEGATED_USER {SERVICE_ACCOUNT_EMAIL}')
    
    print("\n✅ Environment variables set successfully!")
    
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS:")
    print("=" * 70)
    print("""
1. ⚠️  CLOSE PowerShell completely (not just the window, use Alt+F4 or type 'exit')
2. 🔄 Open a NEW PowerShell window (as regular user, not admin)
3. 🚀 Run: python check_gmail_status.py
4. ✅ Should see: Gmail API: ✅ ENABLED and initialized
5. 🧪 Test: Go to http://localhost:5000/auth/register and create an account
""")
    
    print("=" * 70)
    print("Variables set:")
    print("=" * 70)
    print(f"  ENABLE_GMAIL = true")
    print(f"  GOOGLE_SERVICE_ACCOUNT_FILE = credentials.json")
    print(f"  GMAIL_DELEGATED_USER = {SERVICE_ACCOUNT_EMAIL}")
    print("=" * 70 + "\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
