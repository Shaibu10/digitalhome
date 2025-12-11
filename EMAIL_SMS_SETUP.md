# Email & SMS Configuration for Render.com Deployment

## Current Status
- ✅ Email & SMS services are implemented and working locally
- ❌ Not sending on Render (Gmail API and mNotify not configured)
- ✅ Fallback to console logging is working (development mode)

## To Enable Email Verification (Gmail API)

### Step 1: Get Google Service Account Credentials

1. Go to: https://console.cloud.google.com/
2. Create a new project (name it "DigitalHome")
3. Enable the **Gmail API**:
   - Search for "Gmail API"
   - Click "Enable"
4. Create a Service Account:
   - Go to "Service Accounts" in left menu
   - Click "Create Service Account"
   - Name: "digitalhome-email"
   - Click "Create and Continue"
   - Skip optional steps
   - Click "Create Key" → JSON
   - Save the JSON file as `credentials.json`

### Step 2: Allow Service Account to Send Email

The service account email (from credentials.json) must be allowed to send emails:

**Option A: Gmail Account (Simple - for testing)**
1. Forward emails from the Gmail account to service account email
2. Or: Use the service account email directly (requires domain setup)

**Option B: Google Workspace (Production)**
1. Use domain-wide delegation
2. Set up OAuth consent
3. More secure for production

### Step 3: Upload credentials.json to Render

1. In Render dashboard, go to your web service
2. Go to **Settings** → **Environment Variables**
3. Add new variable:
   - Key: `GOOGLE_SERVICE_ACCOUNT_FILE`
   - Value: `credentials.json`
4. Upload the credentials.json file to your project root

### Step 4: Enable Gmail in Environment

1. In Render dashboard → Environment Variables
2. Add:
   - Key: `ENABLE_GMAIL`
   - Value: `true`

3. Also add:
   - Key: `SHOW_EMAIL_WARNINGS`
   - Value: `false`

## To Enable SMS Verification (mNotify)

### Step 1: Get mNotify API Key

1. Go to: https://www.mnnotify.com/dashboard
2. Sign up or log in
3. Get your API Key from the dashboard
4. Get your Sender ID (usually your business name, max 11 chars)

### Step 2: Configure on Render

In Render dashboard → Environment Variables, add:

```
MNNOTIFY_API_KEY=your-api-key-here
MNNOTIFY_SENDER_ID=DigitalHome
```

## Configuration in render.yaml

Update your `render.yaml`:

```yaml
services:
  - type: web
    ...
    envVars:
      - key: FLASK_ENV
        value: production
      - key: FLASK_DEBUG
        value: "0"
      - key: ENABLE_GMAIL
        value: "true"
      - key: SHOW_EMAIL_WARNINGS
        value: "false"
      - key: GOOGLE_SERVICE_ACCOUNT_FILE
        value: credentials.json
      - key: MNNOTIFY_API_KEY
        value: ${MNNOTIFY_API_KEY}  # Use Render secrets
      - key: MNNOTIFY_SENDER_ID
        value: DigitalHome
```

## Using Render Secrets (More Secure)

Instead of hardcoding API keys:

1. Create a `.env.production` file (don't commit to git):
```
MNNOTIFY_API_KEY=your-key-here
GOOGLE_SERVICE_ACCOUNT_FILE=credentials.json
```

2. In Render: Click "Sync with .env" when adding environment variables
3. Or manually add them as secrets in the dashboard

## Testing After Configuration

1. Deploy to Render
2. Register a new account
3. Check Render logs for:
   - `✅ Gmail service initialized successfully` (if Gmail enabled)
   - `✅ Email sent successfully` (when verification email sent)
   - `✅ SMS sent successfully` (when verification SMS sent)

4. Check your email/SMS for verification codes

## Troubleshooting

### Gmail Not Sending
- [ ] Verify credentials.json is in project root
- [ ] Check `ENABLE_GMAIL=true` is set
- [ ] Check service account email is allowed to send
- [ ] Review Render logs for error messages
- [ ] Verify credentials.json has all required fields

### SMS Not Sending
- [ ] Verify `MNNOTIFY_API_KEY` is set correctly
- [ ] Check phone number format (should start with country code)
- [ ] Verify mNotify account has credits
- [ ] Check Render logs for API errors

### Development Mode (Local Testing)
- Set `ENABLE_GMAIL=false` to use console logging
- This is useful for testing without sending real emails
- All emails/SMS will be logged to console

## Next Steps

1. Set up Google Cloud Service Account
2. Get mNotify API key
3. Add environment variables to Render
4. Deploy and test verification flow
5. Monitor logs to confirm emails/SMS are sending
