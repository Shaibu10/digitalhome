# Advanced Features - Quick Reference

## Rate Limiting

### Check if Email is Rate Limited
```python
from auth.utils import TokenGenerator

check = TokenGenerator.check_rate_limit('user@example.com')
# Returns: {'allowed': True/False, 'message': str, 'wait_seconds': int}

if not check['allowed']:
    print(f"Rate limited for {check['wait_seconds']} seconds")
```

### Generate Token (with Rate Limiting)
```python
user = User.query.get(user_id)
result = TokenGenerator.generate_email_token(user)

if result['success']:
    token = result['token']
    # Send email
else:
    # Handle error: result['message']
    print(result['message'])
```

### Verify Token (Resets Rate Limit)
```python
token = TokenGenerator.verify_token(token_string)
if token and token.is_valid():
    # Token is valid and rate limit has been reset
    token.mark_as_used()
```

---

## Admin Dashboard

### Access Dashboard
```
GET /auth/admin/verification
```
Requires: `current_user.is_admin == True`

### Manually Verify User
```python
user = User.query.get(user_id)
user.is_verified = True
user.verified_at = datetime.utcnow()
db.session.commit()
```

Form POST:
```
POST /auth/admin/verification/manual-verify/<user_id>
```

### Resend Verification Email
Form POST:
```
POST /auth/admin/verification/resend/<user_id>
```

---

## User Profile

### Access User Profile
```
GET /auth/profile
```
Requires: User logged in

### Check Verification Status
```python
user = current_user
if user.is_verified:
    print(f"Verified on {user.verified_at}")
else:
    print("Awaiting verification")
```

### Get Verification Badge
```jinja2
{% if current_user.is_verified %}
    <span class="badge badge-success">✅ Verified</span>
{% else %}
    <span class="badge badge-warning">⏳ Pending</span>
{% endif %}
```

---

## Database Queries

### Get Unverified Users
```python
unverified = User.query.filter_by(is_verified=False).all()
```

### Get Rate Limit Record
```python
from models import TokenRateLimit
rate_limit = TokenRateLimit.get_or_create('user@example.com')
```

### Check if User is Rate Limited
```python
from models import TokenRateLimit
rate_limit = TokenRateLimit.get_or_create('user@example.com')
if rate_limit.is_locked():
    print("User is rate limited")
```

### Reset Rate Limit
```python
from models import TokenRateLimit
rate_limit = TokenRateLimit.get_or_create('user@example.com')
rate_limit.reset()
```

---

## API Endpoints

### User Routes
| Method | Route | Auth | Purpose |
|--------|-------|------|---------|
| GET | `/auth/profile` | ✅ Required | View user profile |

### Admin Routes
| Method | Route | Auth | Purpose |
|--------|-------|------|---------|
| GET | `/auth/admin/verification` | ✅ Admin | View dashboard |
| POST | `/auth/admin/verification/manual-verify/<user_id>` | ✅ Admin | Verify user |
| POST | `/auth/admin/verification/resend/<user_id>` | ✅ Admin | Resend email |

---

## Configuration

### Max Rate Limit Attempts
File: `auth/utils.py`
```python
class TokenGenerator:
    MAX_ATTEMPTS = 5  # Change this
```

### Token Expiration Time
File: `auth/utils.py`
```python
TokenGenerator.generate_email_token(
    user,
    expires_in_hours=24  # Change this
)
```

### Backoff Formula
File: `models.py` in TokenRateLimit.increment_attempt()
```python
# Current: 60 * 2^(attempts-3)
# Adjust multiplier or exponent as needed
seconds_to_lock = 60 * (2 ** (self.attempt_count - 3))
```

---

## Error Handling

### Rate Limit Error
```python
token_result = TokenGenerator.generate_email_token(user)
if not token_result['success']:
    message = token_result['message']
    # "Too many requests. Please wait 120 seconds..."
    flash(message, 'error')
```

### Invalid Token
```python
token = TokenGenerator.verify_token(token_string)
if token is None:
    flash('Invalid or expired token', 'error')
```

### Admin Access Denied
```python
if not current_user.is_admin:
    abort(403)  # Forbidden
```

---

## User Messages

### Rate Limit Message
```
Too many requests. Please wait 120 seconds before trying again.
```

### Verification Pending
```
Please verify your email address before logging in.
Check your inbox for the verification link.
```

### Verification Successful
```
Email verified successfully! You can now login.
```

### Already Verified
```
Your email is already verified. You can login now.
```

---

## Testing

### Test Rate Limiting
```python
# Register with email1
# Request resend 6 times
# 6th request should be rate limited
```

### Test Admin Dashboard
```python
# Create admin user: user.is_admin = True
# Navigate to /auth/admin/verification
# Should see unverified users
# Click verify/resend buttons
```

### Test User Profile
```python
# Login as any user
# Navigate to /auth/profile
# Should see verification status
# If unverified, resend button available
```

---

## Debugging

### Check Rate Limit Status
```python
from models import TokenRateLimit
rate_limit = TokenRateLimit.query.filter_by(email='user@example.com').first()
print(f"Attempts: {rate_limit.attempt_count}")
print(f"Locked: {rate_limit.is_locked()}")
print(f"Locked until: {rate_limit.locked_until}")
```

### Check Token Status
```python
from models import EmailToken
token = EmailToken.query.filter_by(token='xyz...').first()
print(f"Valid: {token.is_valid()}")
print(f"Expires at: {token.expires_at}")
print(f"Used at: {token.used_at}")
```

### Check User Verification
```python
user = User.query.get(user_id)
print(f"Verified: {user.is_verified}")
print(f"Verified at: {user.verified_at}")
```

---

## Common Tasks

### Manually Verify a User (Code)
```python
user = User.query.filter_by(email='user@example.com').first()
user.is_verified = True
user.verified_at = datetime.utcnow()
db.session.commit()
```

### Manually Verify a User (Web UI)
```
1. Login as admin
2. Go to /auth/admin/verification
3. Find user in table
4. Click [Verify] button
```

### Send Verification Email
```python
from emails.service import send_verification_email
from flask import url_for

user = User.query.get(user_id)
token = TokenGenerator.generate_email_token(user)
url = url_for('auth.verify_email', token=token.token, _external=True)
send_verification_email(user, url)
```

### Check Admin Status
```python
if current_user.is_admin:
    # User is admin
else:
    # Not admin, deny access
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `models.py` | TokenRateLimit class |
| `auth/utils.py` | TokenGenerator methods |
| `auth/routes.py` | Admin routes |
| `templates/admin/verification_dashboard.html` | Admin UI |
| `templates/auth/profile.html` | User profile UI |
| `migrations/versions/b3c4d5e6f7g8_*.py` | Database migration |
| `ADVANCED_EMAIL_VERIFICATION.md` | Full documentation |
| `ADVANCED_FEATURES_COMPLETE.md` | Implementation summary |

---

## Production Checklist

- [ ] Run `flask db upgrade`
- [ ] Test rate limiting
- [ ] Test admin dashboard
- [ ] Test user profile
- [ ] Verify Gmail API (if needed)
- [ ] Create admin test user
- [ ] Test end-to-end flow
- [ ] Monitor for errors

---

**Last Updated**: November 21, 2025
**Status**: ✅ Ready for Production
