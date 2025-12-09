# Gmail OAuth 2.0 Fix - Precondition Check Failed

## Problem

Your Gmail API was failing with:
```
❌ Precondition check failed
```

This happened because the code was using **Service Account** credentials instead of **OAuth 2.0 User** credentials.

**Service Accounts** are meant for server-to-server communication and cannot send emails from a Gmail inbox.

---

## Solution: Use OAuth 2.0 User Credentials

We've updated your code to use the correct OAuth 2.0 flow for user accounts.

### Step 1: Get OAuth 2.0 Credentials from Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (name it "DigitalHome")
3. **Enable these APIs:**
   - Go to **APIs & Services** → **Library**
   - Search for "Gmail API" → Click → **Enable**
   - Search for "Google Drive API" → Click → **Enable** (needed for credentials)

4. **Create OAuth 2.0 Credentials:**
   - Go to **Credentials** (left sidebar)
   - Click **+ Create Credentials** → **OAuth client ID**
   - Choose **Desktop application**
   - Click **Create**
   - A dialog appears → Click **Download JSON** (or click your app name later to download)
   - Save this file as `credentials.json` in your project root

### Step 2: Verify credentials.json Format

Your `credentials.json` should look like:
```json
{
  "installed": {
    "client_id": "XXXX.apps.googleusercontent.com",
    "project_id": "digitalhome-XXXXX",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "XXXXX",
    "redirect_uris": ["http://localhost"]
  }
}
```

**NOT this format** (which is Service Account):
```json
{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  "private_key": "...",
  ...
}
```

If your credentials.json has `"type": "service_account"` at the top, you downloaded the wrong file. Download the OAuth credentials instead.

---

## Step 3: Add credentials.json to Your Project

### For Local Development:

1. Place `credentials.json` in your project root:
   ```
   e:\python_projects\digialhome\
   ├── app.py
   ├── credentials.json  ← Place it here
   ├── requirements.txt
   ...
   ```

2. Run your app locally:
   ```bash
   python app.py
   ```

3. **First time only:** A browser window will open asking you to authorize the app
   - Click "Allow" to grant Gmail API access
   - A token.json file is saved automatically
   - You won't need to authorize again (until token expires)

### For Render (Production):

**Option A: Upload via Web Terminal (Recommended)**
1. In Render Dashboard, go to your service
2. Click **Shell** (or **Console**)
3. Upload the file using SCP or paste contents:
   ```bash
   cat > credentials.json << 'EOF'
   {paste entire credentials.json contents here}
   EOF
   ```

**Option B: Set as Environment Variable**
1. Base64 encode your credentials.json:
   ```bash
   # Windows PowerShell
   [Convert]::ToBase64String([System.IO.File]::ReadAllBytes("credentials.json")) | clip
   ```
   Or on Mac/Linux:
   ```bash
   cat credentials.json | base64
   ```

2. In Render Environment Variables, add:
   ```
   GOOGLE_CREDENTIALS_JSON_BASE64 = [paste base64 string]
   ```

3. Update app.py startup to decode it:
   ```python
   import base64
   
   if os.environ.get('GOOGLE_CREDENTIALS_JSON_BASE64'):
       creds_json = base64.b64decode(os.environ.get('GOOGLE_CREDENTIALS_JSON_BASE64')).decode()
       with open('credentials.json', 'w') as f:
           f.write(creds_json)
   ```

---

## Step 4: Update Render Environment Variables

In Render Dashboard → Environment, make sure these are set:

```
ENABLE_GMAIL = true
GMAIL_ACCOUNT = your-email@gmail.com
MAIL_USERNAME = your-email@gmail.com
MAIL_PASSWORD = [not used for OAuth, but keep for compatibility]
FLASK_ENV = production
FLASK_DEBUG = 0
```

---

## Step 5: Troubleshooting

### Error: "credentials.json not found"
- **Cause:** File not uploaded to Render
- **Fix:** Use Step 3 to upload the file

### Error: "credentials.json is not an OAuth credentials file"
- **Cause:** You downloaded a Service Account file instead
- **Fix:** Re-download OAuth credentials from Google Cloud Console (choose "Desktop application")

### Error: "Unauthorized client: The OAuth client was not granted access"
- **Cause:** You haven't authorized the app yet
- **Fix:** 
  - Locally: Run the app and authorize in the browser popup
  - On Render: Use SSH to create the token.json file

### Email Still Not Sending
- Check Render logs: Look for `✅ Gmail service initialized successfully`
- Check that `ENABLE_GMAIL=true` in Render Environment
- Try testing locally first with the same credentials.json

---

## How OAuth Flow Works (Local)

1. **First run:**
   ```
   User runs: python app.py
   App checks: Does token.json exist? NO
   App opens: Browser window for Gmail login
   User clicks: "Allow"
   App saves: token.json (reusable access token)
   ```

2. **Subsequent runs:**
   ```
   User runs: python app.py
   App checks: Does token.json exist? YES
   App uses: Saved token.json (no browser needed)
   ```

3. **Token expires:**
   ```
   Render will auto-refresh using refresh_token
   No user interaction needed
   ```

---

## How OAuth Works on Render (Server)

Since Render runs headless (no browser), we handle it differently:

1. **Generate token.json locally:**
   ```bash
   python app.py
   # Authorize in browser → Creates token.json
   ```

2. **Upload token.json to Render:**
   ```bash
   # In Render Shell
   cat > token.json << 'EOF'
   {paste token.json contents}
   EOF
   ```

3. **Render uses saved token:**
   - App starts and finds token.json
   - Uses existing token (no browser needed)
   - Token auto-refreshes if expired

---

## Quick Checklist

- [ ] Downloaded OAuth 2.0 credentials (not Service Account)
- [ ] credentials.json is in project root
- [ ] credentials.json has `"installed"` at top (not `"type": "service_account"`)
- [ ] Ran locally once to generate token.json
- [ ] Uploaded both credentials.json and token.json to Render
- [ ] Set `ENABLE_GMAIL=true` in Render Environment
- [ ] Redeployed on Render
- [ ] Checked Render logs for `✅ Gmail service initialized successfully`

---

## After Fix

Once configured:

```
📧 Sending verification email to user@example.com
✅ Email sent successfully to user@example.com. Message ID: 1234567890
```

Instead of:

```
❌ Precondition check failed
```

---

## Need Help?

1. **Check Render logs** for specific error messages
2. **Test locally first** with same credentials.json
3. **Verify credentials.json format** (must have "installed" key)
4. **Check ENABLE_GMAIL=true** in environment variables
5. **Make sure token.json exists** (or run locally once to generate)
