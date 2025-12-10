# 🚀 QUICK SMS SETUP - 3 STEPS ONLY

## Step 1️⃣ Get mNotify API Key (2 min)

```
https://mnotify.com → Sign Up → Verify Email → Get API Key
```

**Where to find API Key:**
- Dashboard → Settings → API Key (copy this exact value)

---

## Step 2️⃣ Add to Render (3 min)

1. Open: https://dashboard.render.com
2. Click your **digitalhome** service
3. Click **Environment** tab (left side)
4. Click **Add Environment Variable**

5. **First Variable:**
   ```
   Key:   MNOTIFY_API_KEY
   Value: (paste your mNotify API key)
   ```

6. **Second Variable:**
   ```
   Key:   MNOTIFY_SENDER_ID
   Value: DigitalHome
   ```

7. Click **Save Changes**

---

## Step 3️⃣ Wait & Verify (2 min)

1. Render auto-redeploys (wait 2-3 minutes)
2. Go to Render **Logs** tab
3. Look for: `✅ mNotify SMS service initialized`
4. If you see it → **SMS is WORKING!** ✅

---

## Test It

Go to: `https://digitalhome.onrender.com/admin/sms/`

Click **"Send Single SMS"** and send a test message to your phone.

---

## That's It! 🎉

Your SMS is now active and ready to use!

**Questions?** Check `RENDER_SMS_SETUP.md` for detailed troubleshooting.
