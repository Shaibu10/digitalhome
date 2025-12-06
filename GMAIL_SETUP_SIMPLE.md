# Gmail Setup - Simple Steps

## What You'll Do
1. Create a Google Cloud project (5 min)
2. Download credentials file (2 min)
3. Place file in your project folder (1 min)
4. Set 3 environment variables (2 min)
5. Run app and test (2 min)

**Total time: ~12 minutes**

---

## Step 1: Create Google Cloud Project

### Open Google Cloud
Go to: https://console.cloud.google.com/

Sign in with your Google account.

### Create New Project
1. Click the **project dropdown** at top left
2. Click **"NEW PROJECT"**
3. Name: `DigitalHome-Email`
4. Click **"CREATE"**
5. Wait 1-2 minutes for project to create
6. Select the new project from dropdown

### Enable Gmail API
1. In left sidebar, click **"APIs & Services"** > **"Library"**
2. Search for: `Gmail API`
3. Click on **Gmail API**
4. Click **"ENABLE"**

**Status**: ✅ Project created

---

## Step 2: Create Service Account

### Go to Credentials
In the left sidebar: **"APIs & Services"** > **"Credentials"**

### Create Service Account
1. Click **"CREATE CREDENTIALS"** (top button)
2. Select **"Service Account"**
3. Fill in:
   - **Service account name**: `digitalhome-mailer`
   - Description: `Email service for DigitalHome`
4. Click **"CREATE AND CONTINUE"**
5. Skip the optional steps, click **"DONE"**

**Status**: ✅ Service account created

---

## Step 3: Download JSON Credentials

### Navigate to Your Service Account
1. Go to **"APIs & Services"** > **"Credentials"** again
2. Under **"Service Accounts"**, click on: `digitalhome-mailer@...`

### Create JSON Key
1. Click the **"KEYS"** tab
2. Click **"ADD KEY"** > **"Create new key"**
3. Choose **"JSON"**
4. Click **"CREATE"**
5. **File downloads automatically** (save somewhere safe)

**Status**: ✅ JSON file downloaded

---

## Step 4: Place Credentials File

### Copy to Project
1. Take the downloaded JSON file
2. Rename it to: `credentials.json`
3. Move it to your project folder:
   ```
   e:\python_projects\digialhome\credentials.json
   ```

**Verify**: Open the file with Notepad to confirm it contains:
```json
{
  "type": "service_account",
  "project_id": "...",
  ...
}
```

**Status**: ✅ File placed in correct location

---

## Step 5: Set Environment Variables

### Open PowerShell as Administrator
1. Right-click PowerShell
2. Select "Run as Administrator"

### Copy and Paste These Commands

```powershell
[Environment]::SetEnvironmentVariable("ENABLE_GMAIL", "true", "User")
[Environment]::SetEnvironmentVariable("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json", "User")
[Environment]::SetEnvironmentVariable("GMAIL_DELEGATED_USER", "your-email@gmail.com", "User")
```

**IMPORTANT**: Replace `your-email@gmail.com` with your actual Gmail address.

### Verify It Worked
After running those commands, close PowerShell completely (very important!).

Open a NEW PowerShell window and type:
```powershell
$env:ENABLE_GMAIL
```

Should show: `true`

**Status**: ✅ Environment variables set

---

## Step 6: Test Gmail

### Start the App
Open PowerShell in your project folder and run:
```powershell
cd e:\python_projects\digialhome
python app.py
```

### Look for Success Message
You should see in the console:
```
✅ Gmail service initialized successfully (delegated to: your-email@gmail.com)
```

**If you see this**: Gmail is working! 🎉

**If you see this**: Something went wrong, see troubleshooting below
```
⚠️ Gmail API disabled - using console logging for emails
```

---

## Step 7: Test Email Sending

### Register a Test User
1. Keep the app running
2. Open browser: http://localhost:5000/auth/register
3. Fill in the form:
   - Username: `testuser`
   - Email: `yourname@gmail.com` (use your Gmail)
   - Password: anything
4. Click "Register"
5. Check console for:
   ```
   ✅ Email sent successfully to yourname@gmail.com
   ```

### Check Your Gmail Inbox
The verification email should appear in your Gmail inbox within 10 seconds.

**Status**: ✅ Emails sending successfully

---

## Troubleshooting

### Problem: "Gmail API disabled" message
```
⚠️ Gmail API disabled - using console logging for emails
```

**Solutions**:
1. Check environment variables are set:
   ```powershell
   $env:ENABLE_GMAIL
   $env:GOOGLE_SERVICE_ACCOUNT_FILE
   $env:GMAIL_DELEGATED_USER
   ```
   All three should show values

2. Close and reopen PowerShell completely

3. Verify `credentials.json` exists in project folder

4. Check JSON file is valid (open with Notepad, should start with `{`)

---

### Problem: "Service account file not found"
```
⚠️ Service account file 'credentials.json' not found
```

**Solutions**:
1. Download JSON again from Google Cloud
2. Rename to exactly: `credentials.json`
3. Place in: `e:\python_projects\digialhome\credentials.json`
4. Restart app

---

### Problem: "Failed to initialize Gmail service"
```
❌ Failed to initialize Gmail service: ...
```

**Solutions**:
1. Download fresh JSON from Google Cloud
2. Verify email in GMAIL_DELEGATED_USER is correct
3. Check credentials.json is valid JSON (open in Notepad)
4. Ensure Gmail API is enabled in Google Cloud Console

---

### Problem: Email goes to console instead of Gmail
```
📧 EMAIL WOULD BE SENT (Gmail API not configured)
```

**Solutions**:
1. Check `ENABLE_GMAIL` is set to `true`:
   ```powershell
   $env:ENABLE_GMAIL
   ```
2. Close and reopen PowerShell
3. Restart the app
4. See Step 5 again to verify variables

---

## Files You'll Have

After completing all steps:
```
e:\python_projects\digialhome\
├── credentials.json          ← Downloaded from Google (KEEP SECRET!)
├── app.py                   ← Already configured
├── emails/
│   └── service.py           ← Already updated
└── run.py                   ← Launch script
```

---

## Success Checklist

When everything is working, you'll see:

✅ App shows: `✅ Gmail service initialized successfully`
✅ Registration page works
✅ Email appears in inbox within 10 seconds
✅ Console shows: `✅ Email sent successfully to xxx@gmail.com`

---

## Need Help?

- **Detailed steps**: See `GMAIL_SETUP_GUIDE.md`
- **Quick reference**: See `GMAIL_QUICK_REFERENCE.md`
- **Email configuration**: See `EMAIL_CONFIGURATION.md`

---

## Important Security Notes

⚠️ **DO NOT**:
- Share credentials.json with anyone
- Post it in chat or email
- Commit it to Git

✅ **DO**:
- Keep it secure on your computer
- Add to .gitignore: `credentials.json`
- Consider rotating credentials every 90 days

---

## Next Steps After Setup

1. Email sending is now working ✅
2. Users can register and receive verification emails ✅
3. Admin dashboard can resend verification emails ✅
4. Ready for production (if using proper domain)

---

**Estimated time: 12 minutes**
**Difficulty: Easy**
**Help: All documentation provided**
