# Email Verification Quick Reference

## For Developers

### How to Test Locally

1. **Start the Flask app:**
   ```bash
   python app.py
   ```

2. **Register a new user:**
   - Go to `http://localhost:5000/auth/register`
   - Enter username, email, password
   - Submit form

3. **Check console for verification email:**
   - The Flask console will print the verification URL
   - Copy the URL and open in browser
   - Or click the link if you set up a local email server

4. **Verify and login:**
   - Visit the verification URL
   - You should see success message
   - Now you can login with the registered email/password

### Key Classes and Functions

```python
# In auth/utils.py
from auth.utils import TokenGenerator

# Generate a verification token
token = TokenGenerator.generate_email_token(
    user=user_instance,
    token_type='email_verification',
    expires_in_hours=24
)

# Verify a token
email_token = TokenGenerator.verify_token(
    token='token_string',
    token_type='email_verification'
)

if email_token:
    print(f"Valid token for user: {email_token.user.username}")
    email_token.mark_as_used()
```

```python
# In emails/service.py
from emails.service import send_verification_email

# Send verification email
send_verification_email(
    user=user_instance,
    verification_url='http://localhost:5000/auth/verify-email/abc123'
)
```

### Database Queries

```python
# Check if user is verified
user = User.query.get(user_id)
if user.is_verified:
    print("User email verified")
else:
    print("User email pending verification")

# Get all unverified users
unverified = User.query.filter_by(is_verified=False).all()

# Get valid tokens for a user
from models import EmailToken
from datetime import datetime
valid_tokens = EmailToken.query.filter(
    EmailToken.user_id == user_id,
    EmailToken.expires_at > datetime.utcnow(),
    EmailToken.used_at == None
).all()

# Find token by string
token = EmailToken.query.filter_by(token='token_string').first()
```

### Integration Points

**If you have another registration process:**
```python
# After creating user
user = User(username='john', email='john@example.com')
user.set_password('password123')
user.is_verified = False  # Important!
db.session.add(user)
db.session.commit()

# Generate and send token
from auth.utils import TokenGenerator
from emails.service import send_verification_email
from flask import url_for

token = TokenGenerator.generate_email_token(user)
verification_url = url_for('auth.verify_email', token=token.token, _external=True)
send_verification_email(user, verification_url)
```

**If you need to allow unverified users (admin bypass):**
```python
# In your route
user = User.query.get(user_id)
if current_user.is_admin:
    # Allow access even if not verified
    pass
else:
    # Require verification
    if not user.is_verified:
        flash('Please verify your email')
        return redirect(url_for('auth.resend_verification', email=user.email))
```

### Customization

**Change token expiration time:**
```python
# In auth/routes.py register route
email_token = TokenGenerator.generate_email_token(
    user,
    token_type='email_verification',
    expires_in_hours=48  # Change from 24 to 48 hours
)
```

**Customize verification email template:**
- Edit `emails/templates/emails/verify_email.html`
- Add custom styling, company branding, etc.

**Customize pending verification page:**
- Edit `templates/auth/pending_verification.html`
- Change button text, styling, layout

### Debugging

**Check token validity:**
```python
from models import EmailToken
token = EmailToken.query.filter_by(token='abc123').first()
if token:
    print(f"Valid: {token.is_valid()}")
    print(f"Expires at: {token.expires_at}")
    print(f"Used at: {token.used_at}")
```

**Manually verify user (admin only):**
```python
from datetime import datetime
user = User.query.get(user_id)
user.is_verified = True
user.verified_at = datetime.utcnow()
db.session.commit()
```

**Resend verification email:**
```python
from auth.utils import TokenGenerator
from emails.service import send_verification_email
from flask import url_for

user = User.query.filter_by(email='user@example.com').first()
token = TokenGenerator.generate_email_token(user)
verification_url = url_for('auth.verify_email', token=token.token, _external=True)
send_verification_email(user, verification_url)
```

### Email Service Setup

Currently uses console logging. To enable Gmail:

1. Get service account credentials
2. Set `GOOGLE_SERVICE_ACCOUNT_FILE` environment variable
3. Uncomment Gmail setup in `emails/service.py`
4. Restart Flask app

For SMTP (alternative):
- Update `emails/service.py` to use Flask-Mail
- Configure SMTP settings in `config.py`

### Common Issues

**"Token is invalid or expired":**
- Token was already used
- Token has expired (>24 hours)
- Solution: Request new verification email

**Email not received:**
- Check spam/junk folder
- Gmail API not configured (check console)
- User email typo
- Solution: Use resend button on pending verification page

**User can't login after verification:**
- Check database: `is_verified` should be True
- Check migration applied: `flask db upgrade`
- Solution: Manually verify or resend token

### Testing Endpoints

```bash
# Test registration
curl -X POST http://localhost:5000/auth/register \
  -d "username=testuser&email=test@example.com&password=pass123"

# Test login (unverified - should fail)
curl -X POST http://localhost:5000/auth/login \
  -d "email=test@example.com&password=pass123"

# Test verification (use token from console)
curl http://localhost:5000/auth/verify-email/[TOKEN]

# Test resend
curl -X POST http://localhost:5000/auth/resend-verification/test@example.com
```

## Next Steps

1. **Apply database migration:**
   ```bash
   flask db upgrade
   ```

2. **Test user registration and verification**

3. **Configure Gmail API for production (optional)**

4. **Customize email templates with your branding**

5. **Add email verification status to user profile**

6. **Consider adding password reset via email**

---

For detailed implementation information, see `EMAIL_VERIFICATION_IMPLEMENTATION.md`
