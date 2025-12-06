# How to Apply Email Verification Migration

## Quick Start

### Step 1: Apply the Migration

```bash
# Navigate to project directory
cd e:\python_projects\digialhome

# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Apply migration
flask db upgrade
```

### Step 2: Verify Migration Applied

```bash
# Check migration history
flask db history

# You should see: a1b2c3d4e5f6 -> Add email verification fields and EmailToken model
```

### Step 3: Test the Feature

```bash
# Start Flask server
python app.py

# Go to http://localhost:5000/auth/register
# Register a new account
# Check console for verification email link
# Click link to verify
# Login with verified email
```

---

## Migration Details

### What Gets Created

1. **Two new columns on `user` table:**
   - `is_verified` (Boolean, default: False)
   - `verified_at` (DateTime, nullable)

2. **New `email_token` table with:**
   - `id` (Primary Key)
   - `user_id` (Foreign Key to user)
   - `token` (String 255, Unique)
   - `token_type` (String 50)
   - `expires_at` (DateTime)
   - `used_at` (DateTime)
   - `created_at` (DateTime)

### SQL Changes

```sql
-- Add columns to user table
ALTER TABLE user ADD COLUMN is_verified BOOLEAN DEFAULT 0;
ALTER TABLE user ADD COLUMN verified_at DATETIME;

-- Create email_token table
CREATE TABLE email_token (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    token_type VARCHAR(50),
    expires_at DATETIME NOT NULL,
    used_at DATETIME,
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES user (id)
);
```

---

## Troubleshooting

### Migration Already Applied?

If you get an error about migration already being applied:

```bash
# Check current database state
flask db current

# If it shows a1b2c3d4e5f6, migration is already applied
# You can proceed with testing
```

### Need to Rollback?

If you need to undo the migration:

```bash
flask db downgrade
```

This will:
- Remove the `email_token` table
- Remove `is_verified` and `verified_at` columns from `user`

Then you can apply it again:

```bash
flask db upgrade
```

### Database File Location

The SQLite database is typically at:
```
e:\python_projects\digialhome\instance\database.db
```

To manually inspect:
```bash
# Using sqlite3 (if installed)
sqlite3 instance/database.db

# Then in sqlite3 shell:
.tables
.schema user
.schema email_token
```

---

## Verification Checklist

After applying migration, verify:

- [ ] Migration applied without errors
- [ ] `flask db current` shows `a1b2c3d4e5f6`
- [ ] App starts without errors
- [ ] Can register new account
- [ ] Verification email appears in console
- [ ] Can click verification link
- [ ] Can login after verification
- [ ] Cannot login before verification

---

## If You Already Have Data

### Existing Users

If you already have users in the database:

```bash
# Apply migration
flask db upgrade

# All existing users will have:
# - is_verified = 0 (False)
# - verified_at = NULL
```

**To mark existing users as verified:**

```bash
# Start Python shell
flask shell

# In the shell:
from models import User
from datetime import datetime

# Mark all users as verified (if you want)
users = User.query.all()
for user in users:
    user.is_verified = True
    user.verified_at = datetime.utcnow()

# Commit changes
db.session.commit()
print(f"Verified {len(users)} users")
exit()
```

Or manually update in database:

```sql
UPDATE user SET is_verified = 1, verified_at = CURRENT_TIMESTAMP;
```

---

## Production Deployment

### Before Deploying to Production

1. **Test locally first**
   ```bash
   flask db upgrade
   # Test all verification features
   flask db downgrade
   flask db upgrade  # Test again
   ```

2. **Backup database**
   ```bash
   # Copy your database file
   copy instance/database.db instance/database.db.backup
   ```

3. **Apply migration**
   ```bash
   flask db upgrade
   ```

4. **Verify**
   ```bash
   flask db current
   # Should show: a1b2c3d4e5f6 -> Add email verification fields and EmailToken model
   ```

5. **Test feature in production**
   - Register test account
   - Verify email
   - Login

---

## Monitoring

### Check Verification Stats

```bash
# Start Flask shell
flask shell

# In shell:
from models import User, EmailToken
from datetime import datetime

# Count verified users
verified = User.query.filter_by(is_verified=True).count()
unverified = User.query.filter_by(is_verified=False).count()
print(f"Verified: {verified}, Unverified: {unverified}")

# Check old tokens
old_tokens = EmailToken.query.filter(
    EmailToken.expires_at < datetime.utcnow()
).count()
print(f"Expired tokens: {old_tokens}")

# Get active tokens
active_tokens = EmailToken.query.filter(
    EmailToken.expires_at > datetime.utcnow(),
    EmailToken.used_at == None
).count()
print(f"Active tokens: {active_tokens}")
```

---

## Reverting Migration (If Needed)

If you need to completely remove email verification:

```bash
# Downgrade database
flask db downgrade

# Remove email verification code from:
# - auth/routes.py (verify_email, resend_verification functions)
# - Update login() function
# - Update register() function

# Delete template files:
# - emails/templates/emails/verify_email.html
# - templates/auth/pending_verification.html

# Delete migration file:
# - migrations/versions/a1b2c3d4e5f6_add_email_verification.py

# Restart Flask app
```

---

## Support

If you encounter issues:

1. **Check migration file syntax**
   - `migrations/versions/a1b2c3d4e5f6_add_email_verification.py`

2. **Verify database is accessible**
   - Check file permissions
   - Ensure database not locked

3. **Check Flask-Migrate installation**
   ```bash
   pip list | grep -i alembic
   pip list | grep -i migrate
   ```

4. **Check database engine**
   - Look in `config.py` for `SQLALCHEMY_DATABASE_URI`
   - Ensure database URL is correct

5. **Review logs**
   ```bash
   flask db upgrade -v  # Verbose output
   ```

---

## Timeline

```
Before Migration:
- User registration: Immediate login allowed
- No email verification
- Email data not validated

After Migration:
- User registration: Email verification required
- Verification email sent
- User must click link to activate
- Login blocked until verified
```

---

## Success Criteria

Migration is successful if:

✅ `flask db upgrade` completes without errors
✅ `flask db current` shows `a1b2c3d4e5f6`
✅ New users must verify email before login
✅ Verification email sends
✅ Clicking link verifies account
✅ Verified users can login
✅ App still works for all other features

---

**Remember**: Always backup your database before running migrations!
