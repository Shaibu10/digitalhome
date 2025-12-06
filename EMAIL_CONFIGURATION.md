# Email Configuration Guide

## Current Status
- ✅ Email system is working with **console logging** (emails are printed to console)
- ⚠️ Gmail API is disabled (no actual emails are sent)

---

## Option 1: Suppress Development Warnings

To hide the Gmail warnings during development, set the environment variable:

```bash
# Windows PowerShell
$env:SHOW_EMAIL_WARNINGS = "false"
python app.py

# Or set it permanently for the session
$env:SHOW_EMAIL_WARNINGS = "false"
# All Python scripts will now run silently

# Windows Command Prompt
set SHOW_EMAIL_WARNINGS=false
python app.py

# Linux/Mac
export SHOW_EMAIL_WARNINGS=false
python app.py
```

---

## Option 2: Enable Real Gmail Email Sending

### Prerequisites
1. Google Cloud Project with Gmail API enabled
2. Service Account with Domain-wide Delegation
3. G Suite/Google Workspace account

### Step 1: Create Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the **Gmail API**
4. Create a **Service Account**:
   - Service account name: `digitalhome-mailer`
   - Grant role: `Editor`
5. Create a **JSON key** and download it

### Step 2: Configure Domain-wide Delegation

1. In Google Cloud Console, go to Service Accounts
2. Edit your service account
3. Go to **Show Domain-wide Delegation**
4. Copy the **Client ID**
5. In Google Workspace Admin Console:
   - Go to **Security** → **API Controls** → **Domain-wide Delegation**
   - Add a new entry with your Client ID
   - Grant scopes: `https://www.googleapis.com/auth/gmail.send`

### Step 3: Set Up Credentials in DigitalHome

1. Place your downloaded `credentials.json` in the project root:
   ```
   e:\python_projects\digialhome\credentials.json
   ```

2. Set environment variables:
   ```bash
   # Windows PowerShell
   $env:GOOGLE_SERVICE_ACCOUNT_FILE = "credentials.json"
   $env:GMAIL_DELEGATED_USER = "your-workspace-email@yourdomain.com"
   
   # Or set permanently
   [Environment]::SetEnvironmentVariable("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json", "User")
   [Environment]::SetEnvironmentVariable("GMAIL_DELEGATED_USER", "your-workspace-email@yourdomain.com", "User")
   ```

### Step 4: Enable Gmail Service in Code

Edit `emails/service.py` and uncomment the Gmail API setup section (lines 20-48).

### Step 5: Test

Run the app:
```bash
python app.py
```

You should see:
```
✅ Gmail service initialized successfully
```

Instead of:
```
⚠️ Gmail API disabled - using console logging for emails
```

---

## Current Console Email Output

When a user registers, you'll see in the console:

```
==================================================
📧 EMAIL WOULD BE SENT (Gmail API not configured)
To: newuser@example.com
Subject: Verify Your Email - DigitalHome
Content Preview: <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
...
==================================================
```

This is **perfect for development and testing**. The email content is fully rendered and displayed.

---

## Configuration File

You can also create a `.env` file in the project root:

```
SHOW_EMAIL_WARNINGS=false
GOOGLE_SERVICE_ACCOUNT_FILE=credentials.json
GMAIL_DELEGATED_USER=mailer@yourdomain.com
```

Then load it in `config.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Troubleshooting

**Q: I see "Gmail API disabled" even after setting up credentials**

A: Make sure:
- `credentials.json` is in the project root
- The JSON file has all required fields
- Environment variables are set correctly
- You've uncommented the Gmail setup code in `emails/service.py`

**Q: Emails are being logged but not sent**

A: This is expected in development. To enable real Gmail sending:
1. Ensure Gmail API is enabled in Google Cloud
2. Service account has proper scopes
3. Delegated user email is correct

**Q: I'm getting "Invalid credentials" error**

A: Check:
- Service account JSON file is valid
- Domain-wide delegation is enabled
- Scopes include `https://www.googleapis.com/auth/gmail.send`

---

## Email Testing

To test email without Gmail:

```python
# In console, emails are printed showing full HTML content
# This allows you to:
# 1. Verify email is being triggered
# 2. See the complete HTML rendered
# 3. Check links and content
# 4. Test without sending real emails
```

---

**Current Status**: ✅ System operational with console logging
**Production Ready**: Yes (with or without real emails)
