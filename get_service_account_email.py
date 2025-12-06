#!/usr/bin/env python
"""Extract service account email from credentials.json"""

import json
import os

credentials_file = 'credentials.json'

if not os.path.exists(credentials_file):
    print(f"❌ {credentials_file} not found in project root")
    print("Please create it first following Option B in GMAIL_SETUP_HELP.py")
    exit(1)

try:
    with open(credentials_file, 'r') as f:
        creds = json.load(f)
    
    # Check if it's a service account (for email sending)
    if 'type' in creds and creds['type'] == 'service_account':
        client_email = creds.get('client_email', 'NOT FOUND')
        project_id = creds.get('project_id', 'NOT FOUND')
        
        print("\n" + "=" * 60)
        print("✅ Service Account Found!")
        print("=" * 60)
        print(f"\nProject ID: {project_id}")
        print(f"Service Account Email: {client_email}")
        print("\n" + "=" * 60)
        print("NEXT STEPS - Set These Environment Variables:")
        print("=" * 60)
        print("\nCopy and paste in PowerShell (as Administrator):\n")
        
        print(f'[Environment]::SetEnvironmentVariable("ENABLE_GMAIL", "true", "User")')
        print(f'[Environment]::SetEnvironmentVariable("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json", "User")')
        print(f'[Environment]::SetEnvironmentVariable("GMAIL_DELEGATED_USER", "{client_email}", "User")')
        
        print("\n" + "=" * 60)
        print("Then:")
        print("  1. Close PowerShell completely")
        print("  2. Open PowerShell again (as regular user)")
        print("  3. Run: python check_gmail_status.py")
        print("=" * 60 + "\n")
        
    else:
        # It's the OAuth credentials file
        print("\n⚠️ This is a Google OAuth credentials file (for login)")
        print("You need a Service Account credentials file (for email sending)")
        print("\nFollow Option B in GMAIL_SETUP_HELP.py to create the correct file")
        exit(1)
        
except json.JSONDecodeError:
    print(f"❌ {credentials_file} is not valid JSON")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
