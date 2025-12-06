# Render.com Deployment Guide

## Quick Start - Deploy in 5 Minutes

### Step 1: Push Latest Code to GitHub
```powershell
git add requirements.txt render.yaml .env.example
git commit -m "Add Render.com deployment configuration"
git push origin main
```

### Step 2: Create Render.com Account
1. Go to https://render.com
2. Sign up with GitHub account
3. Authorize Render to access your repositories

### Step 3: Create Web Service
1. Dashboard → **New +** → **Web Service**
2. Connect your `digitalhome` repository
3. Settings:
   - **Name**: digitalhome
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### Step 4: Configure Environment Variables
In Render dashboard → Environment:

```
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=generate-a-random-secret-key
PAYSTACK_PUBLIC_KEY=your-key
PAYSTACK_SECRET_KEY=your-key
GMAIL_ACCOUNT=your-email@gmail.com
MNNOTIFY_API_KEY=your-api-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Step 5: Deploy
Click **Create Web Service** → Render auto-deploys from GitHub

**Your app will be live at**: `https://digitalhome.onrender.com` (or similar)

---

## Environment Variables Explained

### Required for Production
- `FLASK_ENV=production` - Disables debug mode
- `FLASK_DEBUG=0` - Disables interactive debugger
- `SECRET_KEY` - Generate strong key: `python -c "import secrets; print(secrets.token_hex(32))"`

### Payment (Paystack)
- Get keys from: https://dashboard.paystack.com/settings/api-keys
- Make sure **Public Key** goes in `PAYSTACK_PUBLIC_KEY`
- Make sure **Secret Key** goes in `PAYSTACK_SECRET_KEY`

### SMS (mNotify)
- Get API Key from: https://www.mnnotify.com/dashboard
- Sender ID should be pre-configured

### Email (Gmail)
- Use **Gmail App Password** (not main password)
- Generate at: https://myaccount.google.com/apppasswords
- Enable 2FA first if not already enabled

### Database
- SQLite database will be stored in Render's ephemeral storage
- **⚠️ Note**: Files don't persist on free tier after redeploy
- **Solution**: Backup regularly using `/admin/backups` feature

---

## Important Notes

### Free Tier Limitations
✅ What works:
- 750 free hours/month (covers always-on)
- 512MB RAM
- Outbound internet (API calls work)
- Auto-deployment from GitHub
- Custom domain (paid upgrade)

⚠️ Know before you deploy:
- Service spins down after 15 min inactivity
- First request will be slow (~30 seconds)
- No persistent file storage (database survives, uploaded files need CDN)
- For production use, consider paid tier

### Database Persistence
Your SQLite database (`digitalhome.db`) will persist because:
1. It's small (~180KB)
2. Render keeps it even after spin-down
3. Backup regularly via admin panel

### Static Files & Uploads
For production, consider:
1. Use CloudFront/Cloudflare for static assets
2. Store uploads on AWS S3/Cloudinary for images
3. Or upgrade to Render's paid tier for persistent storage

---

## Auto-Deployment Setup

Your repository is now configured for **auto-deployment**:

1. ✅ `render.yaml` - Tells Render how to build and run
2. ✅ `requirements.txt` - All dependencies listed
3. ✅ GitHub push → Render auto-deploys

**To deploy after changes:**
```powershell
git add .
git commit -m "Your changes"
git push origin main
```
→ Render automatically rebuilds and deploys!

---

## Monitoring & Logs

In Render Dashboard:
- **Logs** → See real-time application output
- **Metrics** → CPU, RAM, requests
- **Deploys** → Deployment history

---

## Troubleshooting

### App won't start
1. Check **Logs** for error messages
2. Verify all environment variables are set
3. Ensure `requirements.txt` has all packages

### 500 Error on requests
1. Check app logs for exceptions
2. Verify database path (should be relative)
3. Check API keys (Paystack, Gmail, mNotify)

### Database errors
1. First deploy creates fresh database
2. Use backup feature to migrate data
3. Check file permissions

### API calls failing
1. Free tier has outbound access - should work
2. Check if API keys are correct
3. Verify firewall/CORS settings

---

## Next Steps

1. **Push code**: `git push origin main`
2. **Create account**: https://render.com
3. **Connect repository** and deploy
4. **Set environment variables**
5. **Monitor logs** during first deployment
6. **Test payment flow** (use Paystack test keys first)

Your Digital Home e-commerce platform will be live in minutes! 🚀
