# Render Email & SMS Configuration Guide

## Overview

Your Digital Home project requires two external services:
1. **Gmail API** - For email verification and notifications
2. **mNotify** - For SMS verification and notifications

This guide walks you through configuring both on Render.

## Part 1: Gmail Configuration

### Step 1: Get Gmail Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (name it "DigitalHome")
3. Enable these APIs:
   - Gmail API
   - Google Drive API (for credentials)

4. Create OAuth 2.0 credentials:
   - Go to **Credentials** → **Create Credentials** → **OAuth client ID**
   - Choose **Desktop application**
   - Download the JSON file (save as `credentials.json`)

### Step 2: Get Service Account Email

Your `credentials.json` contains a `client_email`. Copy it.

### Step 3: Set Up Gmail App Password

1. Enable 2-Factor Authentication on your Gmail account
2. Go to [Google Account Security](https://myaccount.google.com/security)
3. Find **App passwords** (near bottom)
4. Select **Mail** and **Windows Computer**
5. Google generates a 16-character password - **copy this**

### Step 4: Configure on Render

1. Go to your Render service dashboard
2. Click **Environment**
3. Add these variables:

```
ENABLE_GMAIL = true
GMAIL_ACCOUNT = your-email@gmail.com
MAIL_USERNAME = your-email@gmail.com
MAIL_PASSWORD = [16-char app password from Step 3]
```

### Step 5: Upload credentials.json

⚠️ **Important**: The `credentials.json` file is in your `.gitignore` for security.

Since you can't commit it to Git, you need to add it to Render:

**Option A: Upload via Render Dashboard (Recommended)**
1. In Render dashboard, go to **Files** (if available)
2. Upload `credentials.json` to the app root

**Option B: Set as Environment Variable (Alternative)**
1. Copy contents of `credentials.json`
2. In Render Environment, add:
```
GOOGLE_CREDENTIALS_JSON = {paste entire JSON contents}
```
3. Update `emails/service.py` to read from this variable

**Option C: Manually Add to Render (SSH)**
1. SSH into your Render service
2. Create the file manually:
   ```bash
   cat > credentials.json << 'EOF'
   {paste credentials.json contents}
   EOF
   ```

---

## Part 2: mNotify SMS Configuration

### Step 1: Get mNotify Credentials

1. Sign up at [mNotify.com](https://www.mnnotify.com/)
2. Go to your Dashboard
3. Find your **API Key** (usually in Settings)
4. Choose a **Sender ID** (appears as SMS sender name, e.g., "DigitalHome")

### Step 2: Configure on Render

1. Go to your Render service dashboard
2. Click **Environment**
3. Add these variables:

```
MNNOTIFY_API_KEY = [your mNotify API Key]
MNNOTIFY_SENDER_ID = DigitalHome
```

### Step 3: Test SMS

Once configured, SMS should automatically send on:
- User registration (verification code)
- Password reset
- Order notifications

---

## Part 3: Verify Configuration

### Check Email Works

1. After deploying, register a new user on your app
2. Check Render logs for:
   ```
   ✅ Verification email sent to user@example.com
   ```
3. Check your email inbox for verification link

### Check SMS Works

1. Register with a phone number
2. Check Render logs for:
   ```
   ✅ Verification SMS sent to 0544765278
   ```
3. Check SMS on your phone

### View Render Logs

```bash
# In Render Dashboard → Logs
tail -f <service-name>-log
```

Or locally via Render CLI:
```bash
render logs <service-id>
```

---

## Troubleshooting

### Gmail Not Sending

**Error**: "Gmail API not configured"

**Solution**:
- [ ] Check `ENABLE_GMAIL=true` is set in Render Environment
- [ ] Verify `credentials.json` exists in app root
- [ ] Verify `MAIL_USERNAME` and `MAIL_PASSWORD` are set
- [ ] Check 2FA is enabled on Gmail account
- [ ] Verify 16-character app password is correct (not regular password)

### SMS Not Sending

**Error**: "mNotify not configured"

**Solution**:
- [ ] Check `MNNOTIFY_API_KEY` is set in Render Environment
- [ ] Verify API key is correct (copy from mNotify dashboard)
- [ ] Check `MNNOTIFY_SENDER_ID` is set
- [ ] Verify mNotify account has credit/balance

### Testing Locally

Before deploying, test locally:

```bash
# Set environment variables
$env:ENABLE_GMAIL = "true"
$env:MNNOTIFY_API_KEY = "your-api-key"

# Run Flask app
python app.py

# Register a user - should see email/SMS attempts in console
```

---

## Environment Variables Checklist

### Gmail/Email (Required for Verification)
- ✅ `ENABLE_GMAIL` = "true"
- ✅ `GMAIL_ACCOUNT` = your Gmail address
- ✅ `MAIL_USERNAME` = your Gmail address
- ✅ `MAIL_PASSWORD` = 16-char app password
- ✅ `credentials.json` file in app root

### SMS (Required for SMS Verification)
- ✅ `MNNOTIFY_API_KEY` = your mNotify API key
- ✅ `MNNOTIFY_SENDER_ID` = "DigitalHome" (or your sender ID)

### Flask
- ✅ `FLASK_ENV` = "production"
- ✅ `FLASK_DEBUG` = "0"

---

## Security Notes

⚠️ **Never commit sensitive files!**
- `credentials.json` ← Keep in `.gitignore`
- `.env` files ← Keep in `.gitignore`
- API keys ← Use Render Environment variables

✅ **Best Practices**:
- Use app-specific passwords, not main Gmail password
- Rotate API keys periodically
- Enable 2FA on all email/SMS accounts
- Monitor Render logs for failed send attempts

---

## Next Steps

1. **Gather credentials** (Gmail + mNotify)
2. **Set environment variables** in Render
3. **Upload credentials.json** to Render
4. **Deploy** to Render
5. **Test** by registering a new user
6. **Verify** email/SMS received

Once configured, verification emails and SMS will send automatically!

---

## Support

If issues persist:

1. Check Render logs: `render logs <service-id>`
2. Verify all environment variables are set
3. Test credentials locally first
4. Check mNotify/Gmail account limits/quotas
5. Review email/SMS service logs for bounced messages
