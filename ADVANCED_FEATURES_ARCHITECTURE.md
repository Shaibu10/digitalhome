# Advanced Features - Visual Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMAIL VERIFICATION SYSTEM V2.0               │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                       RATE LIMITING (New)                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Request to Generate Token                                 │
│         ↓                                                        │
│  Check TokenRateLimit Table                                     │
│         ↓                                                        │
│   ┌─────────────────────────────┐                              │
│   │ is_locked() ?               │                              │
│   └──────────┬──────────────────┘                              │
│              │                                                  │
│         YES  │  NO                                             │
│         ↓    ↓                                                  │
│    BLOCK     increment_attempt()                               │
│    Show      ↓                                                  │
│    Wait      Generate Token                                    │
│    Time      ↓                                                  │
│             Send Email                                         │
│                                                                │
│  Wait Times: 60s → 120s → 240s → 480s → ...                  │
│  Reset: After successful email verification                   │
│                                                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                  ADMIN DASHBOARD (New)                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Route: /auth/admin/verification                               │
│  Access: Admin users only (is_admin=True)                      │
│                                                                │
│  ┌────────────────────────────────────────────┐              │
│  │        STATISTICS DASHBOARD                │              │
│  ├────────────────────────────────────────────┤              │
│  │ [Total: 150]  [Verified: 130]  [Pending: 20]              │
│  │ [Verification Rate: 86.7%]                 │              │
│  └────────────────────────────────────────────┘              │
│                                                                │
│  ┌────────────────────────────────────────────┐              │
│  │    UNVERIFIED USERS TABLE (Paginated)      │              │
│  ├────────────────────────────────────────────┤              │
│  │ Username | Email | Date Registered | Act. │              │
│  │ john_d   | j@ex  | 2025-11-20     | [V] [R] [View] │      │
│  │ jane_s   | j@ex  | 2025-11-21     | [V] [R] [View] │      │
│  │ ...      | ...   | ...            | ...           │      │
│  │                                    │              │
│  │ [V] = Verify (manual verification)          │              │
│  │ [R] = Resend (email, no rate limit)         │              │
│  │                                                │              │
│  │ Page: 1 2 3 4 5 [Next]                      │              │
│  └────────────────────────────────────────────┘              │
│                                                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│              USER PROFILE PAGE (New)                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Route: /auth/profile                                          │
│  Access: Logged-in users                                       │
│                                                                │
│  ┌────────────────────────────────────────────┐              │
│  │ [Avatar]  USERNAME                         │              │
│  │           Member since: Nov 15, 2025       │              │
│  │                                             │              │
│  │ ✅ EMAIL VERIFIED                          │              │
│  │    Verified on Nov 21, 2025 at 15:30      │              │
│  │                                             │              │
│  │ Status: ✅ Active | Verified               │              │
│  └────────────────────────────────────────────┘              │
│                                                                │
│  ┌──────────────────┬──────────────────┐                     │
│  │  ACCOUNT DETAILS │  STATISTICS      │                     │
│  ├──────────────────┼──────────────────┤                     │
│  │ Username: john_s │ Orders: 5        │                     │
│  │ Email: j@ex.com  │ Spent: $450.00   │                     │
│  │ Status: Active   │                  │                     │
│  │ Verified: ✅     │                  │                     │
│  │ Joined: Nov 2025 │                  │                     │
│  │ Last: Nov 21 2PM │                  │                     │
│  └──────────────────┴──────────────────┘                     │
│                                                                │
│  ┌──────────────────────────────────────────┐              │
│  │  RECENT ACTIVITY                         │              │
│  ├──────────────────────────────────────────┤              │
│  │ ✅ Logged in           Nov 21, 14:45     │              │
│  │ 🛒 Added to cart       Nov 21, 14:30     │              │
│  │ ✉️  Verified email     Nov 21, 10:15     │              │
│  │ 👤 Registered account  Nov 15, 09:30     │              │
│  │ ...                                      │              │
│  └──────────────────────────────────────────┘              │
│                                                                │
│  SIDEBAR:                                                      │
│  [Change Password]  [Change Email]                            │
│                                                                │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

### Registration with Rate Limiting

```
User Registers
    ↓
Create User (not verified)
    ↓
Check Rate Limit → Allowed?
    ├─ YES: Generate token, send email
    │        User added to TokenRateLimit table
    │        attempt_count = 1
    │
    └─ NO: Show error "Too many requests"
            Wait time shown to user


Resend Request
    ↓
Check Rate Limit → Allowed?
    ├─ YES: Increment attempt_count
    │        Check if locked_until has passed
    │        If not locked: generate token, send email
    │
    └─ NO: Show "Wait X seconds"


Verify Email Click
    ↓
Validate token
    ├─ VALID: Mark user verified
    │         Reset rate limit (attempt_count = 0)
    │         Redirect to login
    │
    └─ INVALID: Show error "Expired/invalid"
```

### Admin Actions

```
Admin Views Dashboard
    ↓
Query all users with is_verified=False
    ↓
Display in table (20 per page)
    ↓
Admin clicks action
    │
    ├─ [Verify]: 
    │   ├─ Set is_verified=True
    │   ├─ Set verified_at=now
    │   └─ Log activity
    │
    ├─ [Resend]:
    │   ├─ Generate/get token (ignore rate limit)
    │   ├─ Send email
    │   └─ Log activity
    │
    └─ [View]:
        └─ Link to user detail page
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│ TABLE: user                                                 │
├─────────────────────────────────────────────────────────────┤
│ id (INT)                                                    │
│ username (VARCHAR)                                          │
│ email (VARCHAR)                                             │
│ password_hash (VARCHAR)                                     │
│ is_verified (BOOLEAN) ← NEW FIELD                          │
│ verified_at (DATETIME) ← NEW FIELD                         │
│ is_admin (BOOLEAN)                                          │
│ is_active (BOOLEAN)                                         │
│ created_at (DATETIME)                                       │
│ last_login (DATETIME)                                       │
└─────────────────────────────────────────────────────────────┘
                         │
                         ├─→ 1:N to email_token
                         └─→ 1:N to user_activity

┌─────────────────────────────────────────────────────────────┐
│ TABLE: token_rate_limit ← NEW TABLE                         │
├─────────────────────────────────────────────────────────────┤
│ id (INT) - Primary Key                                      │
│ email (VARCHAR) ← INDEX                                     │
│ attempt_count (INT) - Tracks requests                       │
│ last_attempt_at (DATETIME)                                  │
│ locked_until (DATETIME) - When lock expires                │
│ created_at (DATETIME)                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TABLE: email_token (Previously added)                       │
├─────────────────────────────────────────────────────────────┤
│ id (INT)                                                    │
│ user_id (INT) ← FK to user                                 │
│ token (VARCHAR) UNIQUE                                      │
│ token_type (VARCHAR)                                        │
│ expires_at (DATETIME)                                       │
│ used_at (DATETIME)                                          │
│ created_at (DATETIME)                                       │
└─────────────────────────────────────────────────────────────┘
```

## State Diagram: User Verification

```
                    [Registration]
                          ↓
                    Create User
                     is_verified=False
                          ↓
                  ┌─────────────────┐
                  │   UNVERIFIED    │ ← Rate limited if requests > limit
                  │                 │
                  │ Can't Login      │
                  │ Resend Available │
                  └────────┬────────┘
                           │
                    Email verification link
                           │
                    Click link in email
                           │
                    ┌──────┴──────┐
                    ↓             ↓
              Valid Token    Invalid/Expired
                    ↓             ↓
                 Mark Verified  Show Error
                    │             │
                    ↓             ↓
            ┌──────────────┐  Resend Link
            │  VERIFIED    │
            │              │
            │ Can Login    │
            │ Full Access  │
            └──────────────┘
                    ↑
                    │
            [Manual Verification by Admin]
```

## Features Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                     FEATURE COMPARISON                          │
├─────────────────────┬──────────────┬──────────────┬─────────────┤
│ Feature             │ Users        │ Admins       │ Status      │
├─────────────────────┼──────────────┼──────────────┼─────────────┤
│ View Profile        │ ✅ Own only  │ ✅ All       │ Complete    │
│ Rate Limiting       │ ✅ Yes       │ ✅ Bypassed  │ Complete    │
│ Resend Email        │ ✅ Limited   │ ✅ Unlimited │ Complete    │
│ See Verification    │ ✅ Own       │ ✅ All       │ Complete    │
│ Activity Timeline   │ ✅ Own       │ ✅ View All  │ Complete    │
│ Admin Dashboard     │ ❌ No        │ ✅ Yes       │ Complete    │
│ Manual Verify       │ ❌ No        │ ✅ Yes       │ Complete    │
│ Statistics          │ ✅ Personal  │ ✅ Global    │ Complete    │
│ Change Email        │ ⏳ Modal*    │ N/A          │ Planned     │
│ Change Password     │ ⏳ Modal*    │ N/A          │ Planned     │
│ 2FA Setup           │ ❌ No        │ N/A          │ Future      │
│ Email Change Verify │ ❌ No        │ N/A          │ Future      │
└─────────────────────┴──────────────┴──────────────┴─────────────┘
* Modal created but form processing not yet implemented
```

## Rate Limiting Timeline

```
Attempt #  Status      Wait Time    Example
─────────────────────────────────────────────────
1          ✅ OK      0 seconds    User generates first token
2          ✅ OK      0 seconds    User generates second token
3          ⏳ WAIT    60 seconds   User must wait 1 minute
4          ⏳ WAIT    120 seconds  User must wait 2 minutes
5          ⏳ WAIT    240 seconds  User must wait 4 minutes
6          ⏳ WAIT    480 seconds  User must wait 8 minutes
7          ⏳ WAIT    960 seconds  User must wait 16 minutes
...
            
Reset      ✅ OK      0 seconds    After user verifies email

Formula: seconds = 60 × 2^(attempts - 3)
```

## New File Structure

```
e:\python_projects\digialhome\
│
├── models.py (MODIFIED)
│   └── + TokenRateLimit class (60 lines)
│
├── auth/
│   ├── utils.py (MODIFIED)
│   │   └── + TokenGenerator.check_rate_limit()
│   │
│   └── routes.py (MODIFIED)
│       ├── + /auth/profile route
│       ├── + /auth/admin/verification route
│       ├── + /auth/admin/verification/manual-verify/<user_id>
│       ├── + /auth/admin/verification/resend/<user_id>
│       └── [Updated register, resend routes for rate limiting]
│
├── templates/
│   ├── auth/
│   │   └── profile.html (NEW - 380 lines)
│   │
│   └── admin/
│       └── verification_dashboard.html (NEW - 200 lines)
│
├── migrations/versions/
│   └── b3c4d5e6f7g8_add_token_rate_limiting_table.py (NEW)
│
└── Documentation/
    ├── ADVANCED_EMAIL_VERIFICATION.md (NEW - 400 lines)
    ├── ADVANCED_FEATURES_COMPLETE.md (NEW - 300 lines)
    ├── ADVANCED_FEATURES_QUICK_REFERENCE.md (NEW - 300 lines)
    └── ADVANCED_FEATURES_OVERVIEW.md (NEW - 400 lines)
```

## Integration Points

```
User → Browser → Flask App
                    ↓
            ┌───────┴────────┐
            ↓                ↓
     [Registration]  [Email Verification]
            ↓                ↓
        TokenRateLimit   EmailToken
            ↓                ↓
        Models DB        Models DB
            ↓                ↓
            └────────┬────────┘
                     ↓
         [User Records Updated]
         - is_verified = True
         - verified_at = timestamp
         - Rate limit reset

Admin → Browser → Flask App
                    ↓
            [Admin Dashboard]
                    ↓
        Check is_admin = True
                    ↓
        ┌───────────┬──────────────┐
        ↓           ↓              ↓
     View      Verify       Resend Email
     Users     (no rate)    (no rate)
        ↓           ↓              ↓
     Query      Update User    Send Email
     Users      Log Activity   Log Activity
```

---

**Legend**:
- ✅ = Implemented
- ⏳ = Partial/Planned
- ❌ = Not implemented

---

**Version**: 2.0 Advanced Features
**Date**: November 21, 2025
**Status**: ✅ Production Ready
