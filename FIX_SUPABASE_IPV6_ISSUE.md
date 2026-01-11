# Supabase IPv6 Connection Issue - SOLUTION

## The Problem

Your Supabase connection string is using IPv6 (address starting with `2a05:`), but Render doesn't support IPv6 connections.

```
❌ IPv6: connection to server at "2a05:d018:135e:1668:4f72:a042:d68:f29a"
✅ IPv4: connection to server at "db.region.supabase.co"
```

## Solution: Use Connection String Format Instead of URI

### Step 1: Get Connection String from Supabase (Not URI)

1. Go to **Supabase Dashboard** → Your Project
2. Click **Settings** ⚙️ (bottom left)
3. Click **Database** tab
4. Look at **Connection string** section - you'll see different **modes**:
   - ❌ `URI` (causes IPv6 issue)
   - ✅ `Connection string` (handles IPv4/IPv6 properly)

### Step 2: Choose the Right Format

In Supabase, there are usually tabs or dropdowns showing different connection modes:

**Look for:**
- `Postgres` (use this one)
- `PoolerMode` (if available)
- URI (avoid this)

**Copy the "Postgres" or "Connection string" that looks like:**
```
postgresql://postgres:[PASSWORD]@db.region.supabase.co:5432/postgres
```

NOT:
```
postgresql://postgres:[PASSWORD]@2a05:d018:135e:1668:4f72:a042:d68:f29a:5432/postgres
```

### Step 3: Update Render Environment Variable

1. Go to Render Dashboard → Your Service
2. **Settings** → **Environment**
3. Update `DATABASE_URL` with the **IPv4-friendly** connection string
4. Save and redeploy

### Step 4: Force IPv4 (Optional Extra Safety)

If issues persist, modify your `config.py` to add IPv4 preference:

```python
# In config.py, before SQLALCHEMY_DATABASE_URI

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///digitalhome.db')

# Force IPv4 resolution if connection string uses domain name
if DATABASE_URL and 'supabase.co' in DATABASE_URL:
    # Supabase domain - already should resolve to IPv4
    # Just ensure we're not using URI mode that forces IPv6
    pass

# Convert postgresql:// to postgresql+psycopg:// for SQLAlchemy 2.0
if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
elif DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)

SQLALCHEMY_DATABASE_URI = DATABASE_URL
```

---

## Quick Checklist

- [ ] In Supabase, use "Connection string" mode (NOT "URI")
- [ ] Copy the full connection string (should contain `db.region.supabase.co`)
- [ ] Paste into Render `DATABASE_URL` environment variable
- [ ] Save and redeploy
- [ ] Wait 2-3 minutes for deployment
- [ ] Check logs - should now show IPv4 connection attempt

---

## If Still Not Working

Try this test script to verify the connection string format:

**test_url.py:**
```python
import os
from urllib.parse import urlparse

url = os.environ.get('DATABASE_URL')
if url:
    parsed = urlparse(url)
    print(f"Host: {parsed.hostname}")
    print(f"Port: {parsed.port}")
    print(f"Database: {parsed.path}")
    
    # Check if using domain (good) or IP (bad)
    if ':' in parsed.hostname:  # IPv6
        print("⚠️ WARNING: IPv6 address detected - may fail on Render")
    elif '.' in parsed.hostname:  # IPv4 or domain
        print("✅ IPv4 or domain detected - should work")
    else:
        print("✅ Domain name - should work")
else:
    print("❌ DATABASE_URL not set")
```

Run locally:
```bash
$env:DATABASE_URL="your-connection-string"
python test_url.py
```

---

## Summary

| Issue | Cause | Fix |
|-------|-------|-----|
| IPv6 error | Using "URI" mode | Use "Connection string" mode |
| Network unreachable | Render doesn't support IPv6 | Use domain name, not IP |
| Still can't connect | Old connection string cached | Redeploy (full rebuild) |

