# 🔧 Gmail API Fix - Quick Action Guide

## What Was Fixed

Your Gmail API was failing with:
```
❌ Precondition check failed
```

**Root Cause:** The code was using **Service Account** credentials, which cannot send emails from a Gmail inbox.

**Solution:** Updated to use **OAuth 2.0 User** credentials (the correct approach).

---

## What You Need to Do NOW

### 1. Download Correct Credentials (5 minutes)

You need **OAuth 2.0 credentials**, NOT Service Account credentials.

**Go to Google Cloud Console:**
1. [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project → Name it "DigitalHome"
3. Enable APIs:
   - Search "Gmail API" → Enable
   - Search "Google Drive API" → Enable

4. **Create OAuth Credentials:**
   - Go to **Credentials**
   - Click **+ Create Credentials** → **OAuth client ID**
   - Choose **Desktop application**
   - Click **Create**
   - Click **Download JSON** (or download from app list)
   - Save as `credentials.json` in your project root

5. **Verify format:**
   - Open `credentials.json`
   - Should start with `"installed": {` NOT `"type": "service_account"`

### 2. Generate Token Locally (2 minutes)

Run your app locally once to authorize:

```bash
cd e:\python_projects\digialhome
python app.py
```

A browser window will open asking to authorize. Click "Allow".

This creates `token.json` automatically.

### 3. Upload to Render (5 minutes)

You now have two files:
- `credentials.json` (just downloaded)
- `token.json` (just generated)

**Upload to Render:**

In Render Dashboard → Your service → **Shell**, paste:

```bash
# Step 1: Create credentials.json
cat > credentials.json << 'EOF'
{paste entire credentials.json contents here}
EOF

# Step 2: Create token.json
cat > token.json << 'EOF'
{paste entire token.json contents here}
EOF

# Verify files exist
ls -la *.json
```

### 4. Deploy (1 minute)

Just push to GitHub (Render auto-deploys):

```bash
git push origin main
```

Render will redeploy automatically. Wait 2-3 minutes.

### 5. Verify (2 minutes)

Check Render logs for:
```
✅ Gmail service initialized successfully (sending as: your-email@gmail.com)
```

Then test by registering a new user at:
```
https://digitalhome.onrender.com/auth/register
```

You should receive a verification email.

---

## Files Updated

- ✅ `emails/service.py` - Now uses OAuth 2.0 instead of Service Account
- ✅ `render.yaml` - Cleaned up duplicate environment variables
- ✅ `GMAIL_OAUTH_FIX.md` - Detailed technical guide (read if issues occur)

---

## Common Issues

**Q: "credentials.json not found"**
- A: You didn't upload it to Render. Use Step 3 above.

**Q: "credentials.json is not an OAuth credentials file"**
- A: You downloaded the wrong file type. Get "OAuth 2.0" not "Service Account".

**Q: Email still not sending after following steps**
- A: 
  1. Check Render logs for specific error
  2. Verify both `credentials.json` and `token.json` exist in Render
  3. Try the same files locally first to test

---

## Timeline

- **Session 12 (Previous):** Added automatic admin user creation ✅
- **Today (Session 13):** Fixed Gmail API OAuth issue ✅
- **Next:** Add mNotify SMS configuration (already documented in RENDER_EMAIL_SMS_SETUP.md)

---

## After Everything Works

Your app will have:
- ✅ User registration with email verification
- ✅ Password reset via email
- ✅ SMS notifications (after mNotify setup)
- ✅ Admin account: `admin@example.com` / `admin123`
- ✅ Production-ready email system

Good luck! You're almost there! 🚀
