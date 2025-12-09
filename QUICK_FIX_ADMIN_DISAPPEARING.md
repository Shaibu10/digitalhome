# ⚡ Quick Fix: Admin User Disappearing on Render

## Why It's Happening

**Render's free tier uses ephemeral storage for SQLite.**

This means:
- Your database file is deleted every time Render restarts
- Admin user gets created, but then deleted on next restart
- Every restart = new database = no admin account

---

## Solution: Switch to PostgreSQL (5 minutes)

Render gives you a FREE PostgreSQL database. Your app already supports it!

### Step 1: Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **PostgreSQL**
3. Fill in:
   - **Name**: `digitalhome-db`
   - **Region**: Same as your web service
   - **Plan**: Free
4. Click **Create Database**
5. Wait for it to say "Available" (usually 1-2 minutes)

### Step 2: Get Connection String

1. Click your new PostgreSQL database in the dashboard
2. Copy the **Internal Database URL** from the connection details
3. It looks like: `postgresql://user:password@host/dbname`

### Step 3: Add to Your Web Service

1. Go back to your **digitalhome** web service
2. Click **Environment**
3. Add this variable:
   ```
   DATABASE_URL = [paste the connection string from Step 2]
   ```
4. Click **Save**

Your service will redeploy automatically (2-3 minutes).

### Step 4: Verify It Works

1. Wait for deployment to finish
2. Check Render logs for:
   ```
   ✅ Database initialization successful!
   ✅ Default admin user created: admin@example.com / admin123
   ```
3. Go to: `https://digitalhome.onrender.com/auth/login`
4. Login with:
   - Email: `admin@example.com`
   - Password: `admin123`

5. **Restart the service** (click Restart in Render dashboard)
6. **Try logging in again** - Admin account should still exist!

---

## Why PostgreSQL Works

- **SQLite**: File-based → stored in temp storage → deleted on restart ❌
- **PostgreSQL**: Managed database → stored permanently → persists forever ✅

---

## Total Time: ~10 minutes

1. Create PostgreSQL: 2 min (waiting)
2. Add DATABASE_URL: 2 min
3. Wait for redeploy: 3 min
4. Test: 3 min

**After this, your admin account will be permanent!** 🚀

---

## Need Help?

See `POSTGRES_MIGRATION.md` for detailed troubleshooting steps.
