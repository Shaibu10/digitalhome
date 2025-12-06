# Gmail Setup - Final Step (2 Minutes)

Your credentials.json is correct! 
Service Account: digitalhome-mailer@digitalhome-email.iam.gserviceaccount.com

---

## Set Environment Variables Permanently

### Option 1: Using PowerShell (Recommended)

**Run PowerShell as Administrator:**

1. Press `Windows Key`
2. Type `PowerShell`
3. Right-click "Windows PowerShell"
4. Click "Run as Administrator"
5. Copy and paste these THREE commands:

```powershell
[Environment]::SetEnvironmentVariable("ENABLE_GMAIL", "true", "User")
[Environment]::SetEnvironmentVariable("GOOGLE_SERVICE_ACCOUNT_FILE","credentials.json", "User") 
[Environment]::SetEnvironmentVariable("GMAIL_DELEGATED_USER", "digitalhome-mailer@digitalhome-email.iam.gserviceaccount.com", "User")
```

6. Press Enter after each command
7. You should see no output (that's good!)

### Option 2: Using Command Prompt (Alternative)

**Run Command Prompt as Administrator:**

1. Press `Windows Key`
2. Type `cmd`
3. Right-click "Command Prompt"
4. Click "Run as Administrator"
5. Copy and paste these THREE commands:

```cmd
setx ENABLE_GMAIL true
setx GOOGLE_SERVICE_ACCOUNT_FILE credentials.json
setx GMAIL_DELEGATED_USER digitalhome-mailer@digitalhome-email.iam.gserviceaccount.com
```

6. Press Enter after each command
7. Wait for "SUCCESS: specified value was saved."

---

## IMPORTANT: Restart PowerShell/Terminal

After setting the variables, you MUST:
1. **Close PowerShell/CMD completely** (Exit or Alt+F4)
2. **Open a NEW PowerShell/CMD window**
3. Do NOT just open a new tab - close the entire window!

---

## Verify Setup

After restarting, run:

```powershell
python check_gmail_status.py
```

You should see:
```
Gmail API: ✅ ENABLED and initialized
```

---

## Test Email Sending

```powershell
python app.py
```

1. Go to: http://localhost:5000/auth/register
2. Fill in: Username, Email, Password
3. Click: Register
4. Check console for:
   ```
   ✅ Email sent successfully to [email]
   ```

---

## Troubleshooting

**Still shows "Gmail API: ⚠️ Disabled"?**
- Make sure you closed AND reopened PowerShell
- Verify environment variables were set: 
  ```powershell
  $env:ENABLE_GMAIL
  $env:GMAIL_DELEGATED_USER
  ```
  Both should return values, not blank

**Still shows "Email WOULD BE SENT"?**
- Same as above - restart PowerShell
- Check credentials.json is in project root

**Getting "Invalid credentials" error?**
- Verify credentials.json contains a service account (check it has "client_email")
- Current email: digitalhome-mailer@digitalhome-email.iam.gserviceaccount.com
- Check Gmail API is enabled in Google Cloud Console

---

## Summary

✅ You have the correct credentials.json (service account)
✅ You have the correct email address
⏳ Just need to set 3 environment variables
⏳ Then restart PowerShell
✅ Then test!

**Total time: ~2 minutes**

---

**Ready? Follow Option 1 (PowerShell) above!**
