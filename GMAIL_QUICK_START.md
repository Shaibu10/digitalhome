# Gmail Setup Checklist - 5 Minutes

Quick checklist to enable real Gmail sending.

---

## Before You Start
- [ ] Google account ready
- [ ] GMAIL_SETUP_GUIDE.md read and understood
- [ ] 10-15 minutes available for setup

---

## Step 1: Create Google Cloud Project (3 min)

- [ ] Go to https://console.cloud.google.com/
- [ ] Create new project named `DigitalHome-Email`
- [ ] Go to "APIs & Services" > "Library"
- [ ] Search for and enable "Gmail API"

---

## Step 2: Create Service Account (2 min)

- [ ] Go to "APIs & Services" > "Credentials"
- [ ] Click "CREATE CREDENTIALS" > "Service Account"
- [ ] Name: `digitalhome-mailer`
- [ ] Click "CREATE AND CONTINUE" > "DONE"

---

## Step 3: Download JSON Key (2 min)

- [ ] Go to "APIs & Services" > "Credentials"
- [ ] Click on service account `digitalhome-mailer@...`
- [ ] Click "KEYS" tab
- [ ] Click "ADD KEY" > "Create new key"
- [ ] Choose "JSON" and click "CREATE"
- [ ] File downloads automatically

---

## Step 4: Save Credentials (1 min)

- [ ] Rename the file to `credentials.json`
- [ ] Move to: `e:\python_projects\digialhome\credentials.json`
- [ ] Keep this file secure - don't share or commit to Git

---

## Step 5: Set Environment Variables (2 min)

### Windows PowerShell (Run as Administrator):

```powershell
[Environment]::SetEnvironmentVariable("ENABLE_GMAIL", "true", "User")
[Environment]::SetEnvironmentVariable("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json", "User")
[Environment]::SetEnvironmentVariable("GMAIL_DELEGATED_USER", "your-email@gmail.com", "User")
```

Replace `your-email@gmail.com` with your actual Gmail address.

**Then restart your PowerShell or IDE.**

### Verify Variables Set:
```powershell
$env:ENABLE_GMAIL
$env:GOOGLE_SERVICE_ACCOUNT_FILE
$env:GMAIL_DELEGATED_USER
```

All three should show your values.

---

## Step 6: Test the Setup (1 min)

```powershell
cd e:\python_projects\digialhome
python app.py
```

**Look for this message:**
```
✅ Gmail service initialized successfully
```

If you see this, Gmail is configured! 🎉

---

## Step 7: Test Email Sending (1 min)

1. Keep the app running from Step 6
2. Go to http://localhost:5000/auth/register
3. Fill in registration form with any email
4. Submit the form
5. Check console for:
   ```
   ✅ Email sent successfully to xxx@example.com
   ```

---

## Troubleshooting

### Error: File not found
```
⚠️ Service account file 'credentials.json' not found
```
- Check credentials.json is in project root
- Restart your terminal/IDE

### Error: Invalid credentials  
```
❌ Failed to initialize Gmail service: invalid_grant
```
- Verify email is set correctly in GMAIL_DELEGATED_USER
- Check credentials.json is valid JSON
- Restart app

### Still showing console emails
```
📧 EMAIL WOULD BE SENT (Gmail API not configured)
```
- Check ENABLE_GMAIL is set to "true"
- Verify all environment variables are set
- Restart your IDE/terminal
- Run this to verify:
  ```powershell
  $env:ENABLE_GMAIL
  ```

---

## Success Indicators

✅ App shows: `✅ Gmail service initialized successfully`
✅ Registration sends real emails
✅ Emails appear in recipient inbox
✅ Console shows: `✅ Email sent successfully to xxx@example.com`

---

## Files Needed

```
e:\python_projects\digialhome\
├── credentials.json          ← Downloaded from Google
└── app.py                   ← Already configured
```

---

## Security Reminder

⚠️ **DO NOT**:
- Share credentials.json with anyone
- Commit credentials.json to Git
- Post it online or in chat

✅ **DO**:
- Add to .gitignore
- Keep in secure location
- Rotate credentials periodically

---

## Next Steps

After Gmail is working:
1. Update `run.py` to set ENABLE_GMAIL in code
2. Deploy to production with credentials
3. Monitor email logs
4. Set up backup email service

---

**Time to complete**: ~10-15 minutes
**Difficulty**: Easy
**Help needed?**: See GMAIL_SETUP_GUIDE.md for detailed instructions
