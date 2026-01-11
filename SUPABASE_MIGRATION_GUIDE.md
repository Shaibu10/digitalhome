# Supabase Migration Guide

Complete step-by-step guide to migrate your DigitalHome project from Render to Supabase.

## Table of Contents
1. [Create Supabase Project](#create-supabase-project)
2. [Get Connection String](#get-connection-string)
3. [Update Environment Variables](#update-environment-variables)
4. [Test Connection](#test-connection)
5. [Run Migrations](#run-migrations)
6. [Verify Migration](#verify-migration)

---

## Create Supabase Project

### Step 1: Sign Up / Log In
1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project" or sign in with GitHub
3. Create a free account (or use existing)

### Step 2: Create New Project
1. Click "New Project" button
2. Fill in the form:
   - **Project name**: `digitalhome` (or any name)
   - **Database Password**: Create a strong password and **save it securely** (you'll need it)
   - **Region**: Choose closest to your users (e.g., `us-east-1` for US, `eu-west-1` for Europe)
3. Click "Create new project"
4. Wait for project to be created (2-3 minutes)

### Step 3: Project Setup Complete
- You'll see a success message
- Project is now live with PostgreSQL database ready

---

## Get Connection String

### Step 1: Access Connection String
1. In Supabase dashboard, click on your project
2. Go to **Settings** (bottom left icon ⚙️)
3. Click **Database** tab
4. Look for **Connection string** section

### Step 2: Copy PostgreSQL Connection String
You'll see different connection options. Copy the **"Connection string"** that looks like:

```
postgresql://postgres:[YOUR-PASSWORD]@db.[REGION].supabase.co:5432/postgres
```

**Example:**
```
postgresql://postgres:MySecurePassword123@db.useast1.supabase.co:5432/postgres
```

**Keep this safe!** This is your database URL.

---

## Update Environment Variables

### Option A: Local Development (.env file)

1. Open `.env` file in your project root (or create one)
2. Replace or add:

```bash
# Old Render config (remove this)
# DATABASE_URL=postgresql+psycopg://user:pass@dpg-xxxxx.render.com/digitalhome

# New Supabase config
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[REGION].supabase.co:5432/postgres
```

**Important:** The connection string will be automatically converted to use `postgresql+psycopg://` by your config.py

### Option B: Render Deployment (Environment Variables)

If deploying on Render:

1. Go to your Render project dashboard
2. Click on your service
3. Go to **Settings** → **Environment**
4. Update `DATABASE_URL`:
   - **Old value**: `postgresql://user:pass@dpg-xxxxx.render.com/digitalhome`
   - **New value**: `postgresql://postgres:[YOUR-PASSWORD]@db.[REGION].supabase.co:5432/postgres`
5. Click "Save"
6. Service will redeploy automatically

### Option C: If Using Supabase + Render

You can deploy the Flask app on Render and database on Supabase:
- **Frontend/Backend**: Render (same as before)
- **Database**: Supabase PostgreSQL
- Just update the DATABASE_URL environment variable

---

## Test Connection

### Step 1: Test Locally

Create a test script `test_supabase_connection.py`:

```python
import os
from sqlalchemy import create_engine, text

# Get the database URL from your config
DATABASE_URL = os.environ.get('DATABASE_URL', 'your-supabase-url-here')

try:
    print("Testing Supabase connection...")
    print(f"URL: {DATABASE_URL[:50]}...")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ Connection successful!")
        print(f"   Server response: {result.fetchone()}")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Step 2: Run Test

```bash
# Set environment variable
$env:DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[REGION].supabase.co:5432/postgres"

# Run test
python test_supabase_connection.py
```

Expected output:
```
Testing Supabase connection...
✅ Connection successful!
   Server response: (1,)
```

---

## Run Migrations

### Step 1: Verify Migrations Directory

Your project should have a `migrations/` folder created by Flask-Migrate. Check it exists:

```bash
ls migrations/
```

You should see: `alembic.ini`, `versions/`, `env.py`, `script.py.mako`

### Step 2: Set Database URL and Run Upgrade

```bash
# PowerShell
$env:DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[REGION].supabase.co:5432/postgres"
$env:FLASK_APP="app.py"

# Run migration
python -m flask db upgrade
```

OR

```bash
# PowerShell with direct connection
$env:DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[REGION].supabase.co:5432/postgres"
python -m flask db upgrade
```

### Expected Output:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl().
INFO  [alembic.runtime.migration] Will assume transactional DDL is supported by the database
INFO  [alembic.runtime.migration] Running upgrade ... (multiple migrations)
INFO  [alembic.runtime.migration] Done!
```

---

## Verify Migration

### Step 1: Check Tables in Supabase

1. Go to Supabase dashboard
2. Click on your project
3. Go to **SQL Editor** (or **Database** → **Tables**)
4. You should see all your tables:
   - `user` (or `users`)
   - `product`
   - `category`
   - `order`
   - `order_item`
   - `cart_item`
   - And others...

### Step 2: Verify Data Integrity

Create verification script `verify_supabase.py`:

```python
import os
from config import Config
from extensions import db
from models import User, Product, Category, Order
from app import create_app

app = create_app()

with app.app_context():
    try:
        # Count records
        users = User.query.count()
        products = Product.query.count()
        categories = Category.query.count()
        orders = Order.query.count()
        
        print("✅ Database Verification")
        print(f"   Users: {users}")
        print(f"   Products: {products}")
        print(f"   Categories: {categories}")
        print(f"   Orders: {orders}")
        
        # Test admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print(f"✅ Admin user exists: {admin.username}")
        else:
            print("⚠️  Admin user not found")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
```

Run it:
```bash
python verify_supabase.py
```

### Step 3: Start Your App

```bash
python app.py
```

Visit: `http://localhost:5000`

Everything should work exactly as before!

---

## Troubleshooting

### Connection String Format Issues

If you get `ModuleNotFoundError: No module named 'psycopg'`:

```bash
pip install psycopg[binary]
```

### Connection Timeout

- Check Supabase region is accessible
- Verify password is correct (no special characters issues)
- Check firewall isn't blocking connections
- In Supabase, go to **Database** → **Network** and add your IP if needed

### Migration Fails

1. Check Supabase is running (check dashboard)
2. Verify DATABASE_URL is set correctly
3. Try connecting with DBeaver or another client first to confirm access
4. Check migration files are not corrupted

### Admin User Not Created

If migrations run but admin user doesn't exist:

```python
# Run in Python shell
from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        is_admin=True,
        is_verified=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print("Admin created!")
```

---

## Post-Migration Checklist

- [ ] Supabase project created
- [ ] Connection string copied
- [ ] DATABASE_URL environment variable updated
- [ ] Connection test passed
- [ ] Migrations ran successfully
- [ ] All tables visible in Supabase dashboard
- [ ] Admin user verified
- [ ] Application starts without errors
- [ ] Can log in with test user
- [ ] Can browse products
- [ ] Orders functionality works

---

## Summary: What Changed

| Aspect | Before (Render) | After (Supabase) |
|--------|-----------------|------------------|
| Database | Render PostgreSQL | Supabase PostgreSQL |
| CODE CHANGES | ❌ None needed | ✅ |
| Models | Same | Same |
| Migrations | Same | Same |
| ORM (SQLAlchemy) | Same | Same |
| Config | Changed DATABASE_URL only | - |
| Flask app logic | No changes | No changes |

---

## Next Steps

**Optional Enhancements** (not required):

1. **Enable Row Level Security (RLS)** in Supabase for security
2. **Set up Supabase Auth** to replace custom auth (optional)
3. **Use Supabase Storage** instead of Cloudinary (optional)
4. **Enable real-time subscriptions** for live updates

For now, just switch the database URL and everything works!

---

## Support

Need help?
- Supabase Docs: https://supabase.com/docs
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
- PostgreSQL Dialect: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html

