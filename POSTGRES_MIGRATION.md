# 🗄️ Migrate to PostgreSQL on Render - Fix Admin User Disappearing

## Problem

Your admin account and all data disappear after Render restarts because **SQLite on Render is ephemeral** (temporary storage).

Every time Render redeploys or restarts your service, the SQLite database file is deleted.

---

## Solution: Use PostgreSQL (Persistent Database)

Render provides a free PostgreSQL database. Your app already supports it!

---

## Step-by-Step Migration

### Step 1: Create PostgreSQL Database on Render (2 minutes)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **PostgreSQL**
3. Fill in:
   - **Name**: `digitalhome-db`
   - **Database**: `digitalhome`
   - **User**: ` `
   - **Region**: Same as your web service
   - **Plan**: Free

4. Click **Create Database**
5. Wait 2-3 minutes for creation (you'll see a green "Available" status)

### Step 2: Get PostgreSQL Connection String

1. Your new PostgreSQL service appears in the dashboard
2. Click on it
3. Copy the **Internal Database URL** (looks like):
   ```
   postgresql://digitalhome_user:PASSWORD@dpg-abc123def456.internal/digitalhome
   ```
   Or the **External Database URL** if internal doesn't work

### Step 3: Add to Your Web Service Environment

1. Go to your **digitalhome** web service (not the DB service)
2. Click **Environment**
3. Add/Update this variable:
   ```
   DATABASE_URL = postgresql://digitalhome_user:PASSWORD@dpg-abc123def456.internal/digitalhome
   ```
   (Replace with your actual connection string from Step 2)

4. Click **Save**
5. Your service will automatically redeploy

### Step 4: Install PostgreSQL Driver

Update `requirements.txt` to include PostgreSQL support:

Add this line (already in most setups, but verify):
```
psycopg2-binary==2.9.9
```

Or run locally:
```bash
pip install psycopg2-binary
```

Commit and push:
```bash
git add requirements.txt
git commit -m "Add PostgreSQL driver for Render database"
git push origin main
```

### Step 5: Verify Migration

1. Wait for Render to redeploy (check **Deploys** tab)
2. Once deployed, check logs for:
   ```
   ✅ Database initialization successful!
   ✅ Tables created: 22
   ✅ Default admin user created: admin@example.com / admin123
   ```

3. Try logging in:
   ```
   https://digitalhome.onrender.com/auth/login
   Email: admin@example.com
   Password: admin123
   ```

---

## Why This Works

- **SQLite**: Files stored in ephemeral storage → **deleted on restart**
- **PostgreSQL**: Data stored on Render's managed database → **persists forever**
- **Your app**: Already configured to auto-create admin user on startup
- **Result**: Admin user created once, persists across all restarts ✅

---

## Optional: Migrate Existing SQLite Data

If you have data in your local SQLite that you want to keep:

```bash
# Export from SQLite locally
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    # Your SQLite data is here
    # It will be used to populate PostgreSQL if you run migrations
    pass
"

# Then let Render handle the migration automatically
# The app.py create_app() function will:
# 1. Connect to PostgreSQL
# 2. Create all tables
# 3. Create default admin user
```

---

## Troubleshooting

**Q: "database connection refused"**
- A: Wait a few minutes for PostgreSQL to fully initialize
- A: Check DATABASE_URL is correct (copy from Render dashboard)
- A: Make sure it's the Internal URL (ends with `.internal`)

**Q: "psycopg2 not found"**
- A: Run: `pip install psycopg2-binary`
- A: Commit requirements.txt to Git
- A: Render will auto-install on redeploy

**Q: "password authentication failed"**
- A: Double-check the connection string
- A: Copy the entire thing from Render dashboard (includes password)

**Q: Data from SQLite not showing**
- A: SQLite data stays on your local machine
- A: PostgreSQL on Render starts fresh (but admin user auto-created)
- A: This is normal and safe - previous data wasn't production anyway

---

## After Migration

Your app now has:
- ✅ **Persistent database** - Data survives restarts
- ✅ **Admin user always exists** - Auto-created on startup
- ✅ **Professional setup** - Ready for production
- ✅ **Free tier** - PostgreSQL free tier on Render

---

## Next Steps

1. Create PostgreSQL database on Render
2. Get connection string
3. Add `DATABASE_URL` to web service environment
4. Verify tables created and admin user exists
5. Test login: `admin@example.com` / `admin123`

**Estimated time: 10 minutes total**

Good luck! Your app will be much more stable now! 🚀
