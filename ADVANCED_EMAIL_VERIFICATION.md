# Advanced Email Verification Features

## Overview

Three powerful features have been added to the email verification system:

1. **Token Rate Limiting** - Prevent abuse and spam
2. **Admin Verification Dashboard** - Manage user verification status
3. **User Profile with Verification Status** - Show verification info to users

---

## 1. Token Rate Limiting

### What It Does

Prevents users from repeatedly generating verification tokens, protecting against:
- Brute force attacks
- Email spam/flooding
- Automated abuse attempts

### How It Works

The system tracks token generation attempts per email address with **exponential backoff**:

| Attempt # | Status | Wait Time |
|-----------|--------|-----------|
| 1-2 | ✅ Allowed | 0 seconds |
| 3 | ⏳ Locked | 60 seconds |
| 4 | ⏳ Locked | 120 seconds (2 min) |
| 5 | ⏳ Locked | 240 seconds (4 min) |
| 6+ | ⏳ Locked | Exponential (8+ min) |

**Reset**: After successful email verification, the counter resets to 0.

### Technical Implementation

#### TokenRateLimit Model

```python
class TokenRateLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    attempt_count = db.Column(db.Integer, default=1)
    last_attempt_at = db.Column(db.DateTime, default=datetime.utcnow)
    locked_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### TokenGenerator Methods

```python
# Check if email is rate limited
rate_limit_check = TokenGenerator.check_rate_limit(email)
# Returns: {'allowed': bool, 'message': str, 'wait_seconds': int}

# Generate token (with rate limit checking)
token_result = TokenGenerator.generate_email_token(user)
# Returns: {'success': bool, 'token': EmailToken, 'message': str}
```

### User Experience

When rate limited, users see:
```
Too many requests. Please wait 120 seconds before trying again.
```

### Admin Bypass

Admin users can resend verification emails without rate limiting restrictions.

---

## 2. Admin Verification Dashboard

### Access

**Route**: `/auth/admin/verification`
**Requirements**: User must be admin (`is_admin=True`)

### Features

#### Dashboard Statistics
- **Total Users**: Count of all registered users
- **Verified Users**: Users with `is_verified=True`
- **Unverified Users**: Users with `is_verified=False`
- **Verification Rate**: Percentage of users verified

#### Unverified Users Table
Shows all unverified users with:
- Username
- Email address
- Registration date
- Current status (Pending)
- Action buttons

#### Action Buttons

**1. Verify Button**
```
POST /auth/admin/verification/manual-verify/<user_id>
```
- Immediately marks user as verified
- Sets `verified_at` timestamp
- No email required
- Logs admin activity
- User can now login

**2. Resend Email Button**
```
POST /auth/admin/verification/resend/<user_id>
```
- Sends new verification email
- Bypasses rate limiting
- Reuses valid token if available
- Logs admin activity
- User can click link to verify

**3. View Button**
- Links to user detail page
- See full user information

### Security Features

- Only admins can access (`@login_required` + `is_admin` check)
- All actions logged to `user_activity` table
- Manual verification logged with user ID and email
- Cannot verify already-verified users

### Pagination

Table displays 20 unverified users per page with navigation controls.

### Example Usage

```python
# Check if user is admin
if current_user.is_admin:
    # Navigate to /auth/admin/verification
    # See all unverified users
    # Click "Verify" to manually verify user
    # Click "Resend Email" to send new link
```

---

## 3. User Profile with Verification Status

### Access

**Route**: `/auth/profile`
**Requirements**: User must be logged in (`@login_required`)

### Sections

#### Profile Header
- User avatar
- Username
- Member since date
- **Email Verification Status**
  - ✅ Verified badge (if verified)
  - ⏳ Pending badge (if not verified)
  - Verification date (if verified)
  - Resend button (if not verified)

#### Account Details
- **Username**: User's display name
- **Email Address**: Primary email
- **Account Status**: Active/Inactive
- **Email Verification**: Verified/Pending
- **Member Since**: Account creation date
- **Last Login**: Previous login timestamp

#### Account Statistics
- **Total Orders**: Lifetime order count
- **Total Spent**: Sum of all orders
- Only shown if user has orders

#### Recent Activity Timeline
Shows last 5 activities:
- Login/Logout events
- Email verification
- Account registration
- Cart additions
- Other tracked activities

#### Sidebar Widgets

**Security Box**
- Change Password button
- Change Email button

**Verification Status Box**
- Email verification status with date
- Account status indicator
- Visual icons (checkmark/warning)

**Quick Stats**
- Account age
- Order count
- Activity count

### Verification Status Display

**If Email NOT Verified:**
```
⚠️ Email Not Yet Verified
Please verify your email address to unlock all features
[Resend Verification Email]
```

**If Email IS Verified:**
```
✅ Email Verified
Verified on November 21, 2025 at 15:30
```

### Change Email/Password Modals

**Change Password Modal**
- Current password (required)
- New password (required)
- Confirm password (required)
- Submit button

**Change Email Modal**
- Current email (disabled, informational)
- New email (required)
- Info: "You'll need to verify your new email address"
- Submit button

> **Note**: Email and password change functionality needs to be implemented in routes

### User Experience

Users can:
1. View their email verification status
2. See when they verified their email
3. Request a resend if not verified
4. View account statistics
5. See recent activity
6. Access security settings

### Code Integration

In `auth/routes.py`:
```python
@auth_bp.route('/profile')
@login_required
def profile():
    return render_template(
        'auth/profile.html', 
        user=current_user, 
        now=datetime.utcnow()
    )
```

---

## Database Changes

### New Table: TokenRateLimit

```sql
CREATE TABLE token_rate_limit (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    attempt_count INTEGER DEFAULT 1,
    last_attempt_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    locked_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email_rate_limit ON token_rate_limit(email);
```

### Migration

Run after pulling changes:

```bash
# Generate migration
flask db migrate -m "Add token rate limiting"

# Or apply provided migration
flask db upgrade
```

The migration file is: `b3c4d5e6f7g8_add_token_rate_limiting_table.py`

---

## Security Considerations

### Rate Limiting
- ✅ Exponential backoff prevents brute force
- ✅ Per-email tracking (not per IP)
- ✅ Resets after successful verification
- ✅ Configurable limits in `TokenGenerator.MAX_ATTEMPTS`

### Admin Verification
- ✅ Only accessible to admin users
- ✅ All actions logged with admin user ID
- ✅ Cannot be used to modify other admin accounts
- ✅ Audit trail for compliance

### User Profile
- ✅ Only logged-in users can access
- ✅ Can only see own profile
- ✅ Sensitive info protected (password modals don't process yet)
- ✅ Activity logged for security events

---

## Future Enhancements

### Rate Limiting
- [ ] IP-based rate limiting
- [ ] Per-user device tracking
- [ ] Email provider detection (catch-alls)
- [ ] API rate limiting

### Admin Dashboard
- [ ] Bulk verification operations
- [ ] Filter/search unverified users
- [ ] Email templates editor
- [ ] Rate limit management

### User Profile
- [ ] Two-factor authentication (2FA)
- [ ] Email change with re-verification
- [ ] Connected accounts (social logins)
- [ ] Export user data (GDPR)
- [ ] Account deletion

---

## Code Examples

### Check Rate Limit

```python
from auth.utils import TokenGenerator

email = 'user@example.com'
check = TokenGenerator.check_rate_limit(email)

if not check['allowed']:
    flash(check['message'], 'error')
    # User is rate limited
else:
    # Proceed with token generation
```

### Generate Token with Rate Limiting

```python
user = User.query.get(user_id)
result = TokenGenerator.generate_email_token(user)

if result['success']:
    token = result['token']
    # Send verification email
else:
    # Handle rate limit error
    message = result['message']
```

### Get Unverified Users (Admin)

```python
unverified = User.query.filter_by(is_verified=False).all()

for user in unverified:
    print(f"{user.username} - {user.email}")
```

### Manual Verification (Admin)

```python
user = User.query.get(user_id)
user.is_verified = True
user.verified_at = datetime.utcnow()
db.session.commit()

# Activity logged automatically in route
```

---

## Testing Checklist

- [ ] Register new user → receives verification email
- [ ] Verify email → redirects to login
- [ ] Try to login unverified → see pending page
- [ ] Click resend → get new email
- [ ] Verify email → can now login
- [ ] Request multiple resends → hit rate limit
- [ ] Wait for rate limit → can request again
- [ ] Admin: see unverified users on dashboard
- [ ] Admin: click verify → user verified immediately
- [ ] Admin: click resend → receives email
- [ ] User: visit profile → see verification status
- [ ] Verified user: profile shows verified badge
- [ ] Unverified user: profile shows pending + resend button

---

## Troubleshooting

### Rate Limit Not Working
**Issue**: Users can generate unlimited tokens
**Solution**: Ensure migration has been run (`flask db upgrade`)

### Admin Dashboard Not Accessible
**Issue**: 403 Forbidden error
**Solution**: User must have `is_admin=True`

### Profile Page Not Found
**Issue**: 404 error on `/auth/profile`
**Solution**: Ensure template exists at `templates/auth/profile.html`

### Verification Status Not Updating
**Issue**: `is_verified` still False after clicking link
**Solution**: 
1. Check migration was applied
2. Verify token is in database
3. Check token expiration time

---

## Configuration

### Rate Limiting Limits

Edit `auth/utils.py` to adjust:

```python
class TokenGenerator:
    MAX_ATTEMPTS = 5  # Lock after this many attempts
```

### Token Expiration

Edit `auth/utils.py` to adjust:

```python
TokenGenerator.generate_email_token(
    user,
    expires_in_hours=24  # Change this value
)
```

### Backoff Formula

The exponential backoff uses: `60 * 2^(attempts-3)`

Adjust in `models.py` TokenRateLimit.increment_attempt():

```python
seconds_to_lock = 60 * (2 ** (self.attempt_count - 3))
```

---

## Related Documentation

- [EMAIL_VERIFICATION_IMPLEMENTATION.md](EMAIL_VERIFICATION_IMPLEMENTATION.md) - Core implementation details
- [README_EMAIL_VERIFICATION.md](README_EMAIL_VERIFICATION.md) - User guide
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Deployment instructions

---

**Status**: ✅ Complete
**Last Updated**: November 21, 2025
**Version**: 2.0 (Advanced Features)
