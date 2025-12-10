# 📱 SMS Setup Guide for Render Deployment

## Step 1: Get mNotify API Key (5 minutes)

### Option A: Create Free mNotify Account
1. Go to: https://mnotify.com/
2. Click **"Sign Up"** or **"Get Started"**
3. Fill in your details:
   - Email address
   - Password
   - Business name: "DigitalHome"
4. Click **Create Account**
5. Check your email and verify

### Option B: Use Existing mNotify Account
- Just log in to https://mnotify.com/

---

## Step 2: Get Your API Key

1. After login, go to **Dashboard**
2. Look for **"API Settings"** or **"Integrations"** menu
3. Find your **API Key** (looks like: `xxxxxxxxxxxxx`)
4. **Copy and save it** somewhere safe (you'll need it next)

---

## Step 3: Add to Render Environment Variables

### Method 1: Via Render Dashboard (Recommended)

1. Go to: https://dashboard.render.com/
2. Click on your **digitalhome** service
3. Go to the **"Environment"** tab (left sidebar)
4. Click **"Add Environment Variable"**

5. Add these two variables:

   **Variable 1:**
   ```
   Key:   MNOTIFY_API_KEY
   Value: (paste your API key from mNotify)
   ```
   
   **Variable 2:**
   ```
   Key:   MNOTIFY_SENDER_ID
   Value: DigitalHome
   ```

6. Click **"Save Changes"** button

### Method 2: Via .env file (Local Testing)

If you want to test SMS locally first:

1. Open `.env` in your project root
2. Add these lines:
   ```
   MNOTIFY_API_KEY=your_api_key_here
   MNOTIFY_SENDER_ID=DigitalHome
   ```
3. Save and restart Flask

---

## Step 4: Verify SMS is Working

### On Render:
1. After adding environment variables, Render will **auto-redeploy**
2. Wait 2-3 minutes for deployment
3. Check the **Logs** tab
4. Look for this message:
   ```
   ✅ mNotify SMS service initialized (sender: DigitalHome)
   ```
5. If you see this, SMS is **ACTIVE!** ✅

### Via Console Message:
If you still see:
```
⚠️ SMS service disabled - using console logging for SMS
```
Then:
- API key was not set correctly
- Go back to Render Environment tab
- Verify `MNOTIFY_API_KEY` is exactly as copied from mNotify
- Save and wait for redeploy

---

## Step 5: Test SMS Sending

### Test 1: Via Admin Dashboard
1. Go to: `https://digitalhome.onrender.com/admin/sms/`
2. Click **"Send Single SMS"**
3. Select a user or enter your phone number
4. Type a test message
5. Click **Send**
6. Check Render Logs for confirmation:
   ```
   ✅ SMS sent to 0241234567. Message ID: xxx, Credits left: 99
   ```

### Test 2: During User Registration
1. Go to: `https://digitalhome.onrender.com/auth/register`
2. Register a new account with your phone number
3. Check if SMS was sent:
   - Render logs should show SMS being sent
   - mNotify dashboard should show the message

---

## Step 6: Monitor SMS Activity

### Check in Render Logs:
```
✅ SMS sent to {phone_number}. Message ID: xxx, Credits left: 99
```

### Check mNotify Dashboard:
1. Go to https://mnotify.com/dashboard
2. Look for **Messages** or **Activity** section
3. Verify your SMS appears in the list

---

## Troubleshooting

### Problem: "SMS service disabled" still showing

**Solution:**
1. Verify API key is copied **exactly** (no spaces before/after)
2. In Render, go to **Environment** tab
3. Check that `MNOTIFY_API_KEY` variable exists
4. Click **Force Deploy** to redeploy
5. Wait 2-3 minutes and check logs again

### Problem: "Invalid phone number format"

**Solution:**
Phone must be in one of these formats:
- `0241234567` (Ghana local)
- `+233241234567` (International with +)
- `233241234567` (International without +)

### Problem: "No credits left"

**Solution:**
1. Check your mNotify account balance
2. mNotify offers free credits - check if you need to add payment method
3. Go to https://mnotify.com and check your account

### Problem: SMS not being received

**Solution:**
- Check that phone number is valid and formatted correctly
- Check mNotify logs to confirm it was sent
- Some carriers may block SMS - try different number
- Check if number is on SMS blacklist in admin panel

---

## SMS Features Now Available

Once SMS is working, you can use:

1. **Verification SMS** - Send codes to users during registration
2. **Password Reset SMS** - Send reset codes via SMS
3. **Order Status SMS** - Notify customers of order updates
4. **Admin Notifications** - Account activity alerts
5. **Bulk Campaigns** - Send to multiple users at once
6. **SMS Templates** - Create reusable message templates

---

## Quick Reference

| Item | Value |
|------|-------|
| API Provider | mNotify |
| Website | https://mnotify.com |
| Rate Limit | ~100 SMS per minute |
| Free Credits | Usually 10-20 to start |
| Character Limit | 160 (ASCII) / 70 (Unicode) |
| Supported Countries | Ghana, others |

---

## Need Help?

If SMS still doesn't work after these steps:

1. **Check mNotify Status:**
   - Log in to mNotify dashboard
   - Verify you have remaining credits
   - Check API settings match what you entered

2. **Check Render Logs:**
   - Go to Logs tab in Render
   - Look for error messages with "SMS" or "mNotify"
   - Copy any error and search online

3. **Test Locally First:**
   - Add MNOTIFY_API_KEY to .env
   - Run `python app.py`
   - Check console output

---

**✅ Setup Complete!**

Your DigitalHome app now has full SMS capabilities! 🎉
