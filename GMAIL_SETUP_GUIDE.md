# Gmail API Setup Guide - Step by Step

## Overview
This guide will help you configure real email sending via Gmail API instead of console logging.

---

## Prerequisites
- Google account
- Google Workspace or G Suite domain (recommended for production)
- Administrator access to Google Cloud Console
- Python knowledge (basic)

---

## Step 1: Create Google Cloud Project

### 1.1 Go to Google Cloud Console
1. Visit https://console.cloud.google.com/
2. Sign in with your Google account
3. Click the project dropdown at the top

### 1.2 Create New Project
1. Click "NEW PROJECT"
2. Project name: `DigitalHome-Email`
3. Click "CREATE"
4. Wait for project to be created (1-2 minutes)
5. Select the new project from dropdown

### 1.3 Enable Gmail API
1. In the left sidebar, click "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "ENABLE"
5. Wait a few seconds for it to enable

---

## Step 2: Create Service Account

### 2.1 Navigate to Service Accounts
1. Go to "APIs & Services" > "Credentials"
2. Click "CREATE CREDENTIALS" > "Service Account"

### 2.2 Create Service Account
1. **Service account name**: `digitalhome-mailer`
2. **Service account ID**: Auto-filled, keep as is
3. **Description**: `Email service for DigitalHome e-commerce platform`
4. Click "CREATE AND CONTINUE"

### 2.3 Grant Permissions (Optional)
1. Skip the optional steps - just click "CONTINUE"
2. Click "DONE"

---

## Step 3: Create and Download JSON Key

### 3.1 Navigate Back to Service Account
1. Go to "APIs & Services" > "Credentials"
2. Under "Service Accounts", click on `digitalhome-mailer@...`

### 3.2 Create JSON Key
1. Click the "KEYS" tab
2. Click "ADD KEY" > "Create new key"
3. Choose "JSON"
4. Click "CREATE"
5. A JSON file will download automatically
   - **Important**: Save this file securely
   - Don't share this file with anyone
   - Store in your project root as `credentials.json`

### 3.3 Copy the Client ID
1. In the service account details page
2. Look for "Client ID" (a long number)
3. Copy this value - you'll need it in Step 4

---

## Step 4: Enable Domain-wide Delegation

### 4.1 Get the Client ID from Service Account
1. Go to "APIs & Services" > "Credentials"
2. Click on your service account `digitalhome-mailer@...`
3. Look for the **Client ID** number and copy it

### 4.2 Configure Domain-wide Delegation
1. Still in the service account details:
2. Look for "Domain-wide delegation" section
3. Click "Show Domain-wide Delegation"
4. Click the "View Google Cloud Console" link (if shown)
5. Or go to "Admin console of the workspace" (if using Google Workspace)

### 4.3 Grant Scopes in Google Workspace
**Note**: If you don't have Google Workspace, you can skip this and use the delegated user email directly.

1. Go to https://admin.google.com (if you have Workspace)
2. Navigate to "Security" > "API Controls" > "Domain-wide Delegation"
3. Click "Add a new entry"
4. Paste your **Client ID** from Step 4.1
5. In "OAuth Scopes" field, paste:
   ```
   https://www.googleapis.com/auth/gmail.send
   ```
6. Click "AUTHORIZE"

---

## Step 5: Place Credentials in Project

### 5.1 Save credentials.json
1. Take the downloaded JSON file from Step 3
2. Place it in your project root:
   ```
   e:\python_projects\digialhome\credentials.json
   ```

### 5.2 Verify the File
1. Open `credentials.json` in a text editor
2. Verify it contains these fields:
   ```json
   {
     "type": "service_account",
     "project_id": "...",
     "private_key_id": "...",
     "private_key": "...",
     "client_email": "digitalhome-mailer@...",
     "client_id": "...",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "...",
     "client_x509_cert_url": "..."
   }
   ```

**Important**: Keep this file secure - don't commit to Git!

---

## Step 6: Configure Environment Variables

### 6.1 Set Variables Permanently (Windows)

#### Using PowerShell (Recommended):
```powershell
# Open PowerShell as Administrator and run:
[Environment]::SetEnvironmentVariable("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json", "User")
[Environment]::SetEnvironmentVariable("GMAIL_DELEGATED_USER", "your-email@gmail.com", "User")

# Restart PowerShell for changes to take effect
```

#### Using Command Prompt:
```cmd
setx GOOGLE_SERVICE_ACCOUNT_FILE "credentials.json"
setx GMAIL_DELEGATED_USER "your-email@gmail.com"

# Restart Command Prompt for changes to take effect
```

### 6.2 What Email to Use?
- **For Personal Gmail**: Use your Gmail address (e.g., `yourname@gmail.com`)
- **For Google Workspace**: Use a workspace email (e.g., `noreply@yourdomain.com`)

### 6.3 Test Variables Were Set
```powershell
$env:GOOGLE_SERVICE_ACCOUNT_FILE
$env:GMAIL_DELEGATED_USER
# Both should print your values
```

---

## Step 7: Enable Gmail in Code

### 7.1 Open emails/service.py
Edit the file: `e:\python_projects\digialhome\emails\service.py`

### 7.2 Find the Setup Section
Look for line 13 onwards in `setup_service()` method.

### 7.3 Comment Out the Disable Section
Change this:
```python
# For now, we'll disable Gmail API until credentials are properly set up
print("⚠️ Gmail API disabled - using console logging for emails")
self.service = None
```

To this:
```python
# Gmail API is now enabled - this will be set by the code below
# self.service = None
```

### 7.4 Uncomment the Gmail Setup
Find this section:
```python
# Uncomment and configure when you have proper service account credentials
"""
from google.oauth2 import service_account
...
```

Replace the entire `"""..."""` block with the uncommented code. You can delete the triple quotes and uncomment all the code inside.

---

## Step 8: Test Gmail Setup

### 8.1 Run with Warnings Enabled
```powershell
cd e:\python_projects\digialhome
$env:SHOW_EMAIL_WARNINGS = "true"
python app.py
```

### 8.2 Look for Success Message
You should see:
```
✅ Gmail service initialized successfully
```

Instead of:
```
⚠️ Gmail API disabled - using console logging for emails
```

### 8.3 Test Email Sending
1. Go to http://localhost:5000/auth/register
2. Register a new user with any email
3. Check the email was sent (in Gmail, or the delegated email address)
4. Check console output for confirmation

---

## Troubleshooting

### Error: "Service account file not found"
- Ensure `credentials.json` is in project root
- Check `GOOGLE_SERVICE_ACCOUNT_FILE` environment variable is set
- Verify file path is correct

### Error: "Service account file missing required fields"
- Download credentials file again from Google Cloud
- Ensure it's the JSON version, not PKCS12
- Check file hasn't been edited or corrupted

### Error: "Invalid credentials"
- Verify service account has Gmail API access
- Check domain-wide delegation is enabled
- Ensure delegated user email is correct
- Restart the app after setting environment variables

### Emails still going to console
- Check `SHOW_EMAIL_WARNINGS` is not set to `true`
- Verify `gmail_service.service` is not None
- Add debug print to confirm service initialized

### Can't see "Gmail service initialized" message
- Check console output carefully
- Verify `SHOW_EMAIL_WARNINGS` environment variable setting
- Temporarily set it to `true` to see initialization details

---

## Summary of Files

After setup, you should have:
```
e:\python_projects\digialhome\
├── credentials.json          ← Downloaded from Google Cloud (KEEP SECRET!)
├── emails/
│   └── service.py           ← Gmail code uncommented
├── run.py                   ← Launch script
└── app.py                   ← Main application
```

---

## Next Steps

1. ✅ Create Google Cloud Project
2. ✅ Create Service Account
3. ✅ Download credentials.json
4. ✅ Configure environment variables
5. ✅ Uncomment Gmail code
6. ✅ Test email sending
7. ✅ Monitor emails

---

## Security Notes

⚠️ **Important**:
- Never commit `credentials.json` to version control
- Add to `.gitignore`:
  ```
  credentials.json
  .env
  *.key
  ```
- Keep the JSON key secure
- Don't share environment variables
- Rotate credentials regularly in production

---

## Support

For issues with Google Cloud:
- Visit https://cloud.google.com/docs/authentication/client-libraries
- Check Gmail API docs: https://developers.google.com/gmail/api
- Enable debug logging in Python

For issues with DigitalHome:
- Check console output for error messages
- Verify all environment variables are set
- Test credentials with a simple script
