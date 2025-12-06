# Dynamic Message System - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DIGITAL HOME PLATFORM                    │
└─────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │   Admin Browser  │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                     │
              /admin/messages                  /api/messages/*
             (Dashboard, CRUD)              (Analytics Tracking)
                    │                                     │
    ┌───────────────┴───────────────┐                    │
    │                               │                    │
┌───▼────────────────────────────────▼────┐              │
│         Flask Application (app.py)        │◄─────────────┘
│  ┌─────────────────────────────────────┐ │
│  │  Admin Routes (7 routes)            │ │
│  │  - List, Create, Edit, Delete       │ │
│  │  - Toggle, Analytics API            │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │  Index Route (/home)                │ │
│  │  - Retrieves active messages        │ │
│  │  - Passes to template               │ │
│  └─────────────────────────────────────┘ │
└───┬────────────────────────────────────┬──┘
    │                                    │
    │                          ┌─────────▼────────┐
    │                          │  Jinja2 Template │
    │                          │  - index.html    │
    │                          │  - Renders msgs  │
    │                          └─────────┬────────┘
    │                                    │
    │                          ┌─────────▼──────────┐
    │                          │  User Browser      │
    │                          │  - Views homepage  │
    │                          │  - Sees messages   │
    │                          │  - Clicks buttons  │
    │                          └─────────┬──────────┘
    │                                    │
    │                 ┌──────────────────┼──────────────────┐
    │                 │  JavaScript      │  AJAX Tracking   │
    │                 │  - View tracking  │  - /api/click    │
    │                 │  - Click tracking │  - /api/view     │
    │                 └──────────┬───────────────────────────┘
    │                            │
    └────────────────┬───────────┘
                     │
    ┌────────────────▼──────────────────────┐
    │    SQLAlchemy ORM (models.py)          │
    │  ┌─────────────────────────────────┐  │
    │  │  DynamicMessage Model           │  │
    │  │  - 18 fields                    │  │
    │  │  - Helper methods               │  │
    │  │  - Relationships (User)         │  │
    │  └─────────────────────────────────┘  │
    │  ┌─────────────────────────────────┐  │
    │  │  Active Message Queries         │  │
    │  │  - Filtering                    │  │
    │  │  - Scheduling logic             │  │
    │  │  - Analytics                    │  │
    │  └─────────────────────────────────┘  │
    └────────────────┬──────────────────────┘
                     │
    ┌────────────────▼──────────────────────┐
    │      SQLite Database                   │
    │  ┌─────────────────────────────────┐  │
    │  │  dynamic_message table          │  │
    │  │  - 20 columns                   │  │
    │  │  - 3 indexes                    │  │
    │  │  - Relationships (user table)   │  │
    │  └─────────────────────────────────┘  │
    │  ┌─────────────────────────────────┐  │
    │  │  Migration History              │  │
    │  │  - g8h9i0j1k2l3                │  │
    │  └─────────────────────────────────┘  │
    └────────────────────────────────────────┘
```

## Data Flow Diagram

```
1. ADMIN CREATES MESSAGE
   ┌─────────────────────────────────────────┐
   │ Admin fills form at /admin/messages/add │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Form validation in Flask route          │
   │ - Check title/content                   │
   │ - Parse dates                           │
   │ - Validate colors                       │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Create DynamicMessage instance          │
   │ - Set all fields                        │
   │ - Set created_by (current admin)        │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ db.session.add() & commit()             │
   │ Save to SQLite database                 │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Redirect to messages list               │
   │ Flash success message                   │
   └────────────────────────────────────────┘


2. USER VIEWS HOMEPAGE
   ┌─────────────────────────────────────────┐
   │ User requests / (homepage)              │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Flask index() route executes            │
   │ - Query DynamicMessage.                 │
   │   get_active_homepage_messages()        │
   │ - Filter: is_active=True                │
   │ - Filter: schedule within range         │
   │ - Order by display_order                │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Render template/index.html              │
   │ - Pass messages to template             │
   │ - Loop through messages                 │
   │ - Apply dynamic colors/icons            │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Return HTML to browser                  │
   │ - Page loads with messages              │
   │ - JavaScript initializes                │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Browser Intersection Observer           │
   │ - Detects message in viewport           │
   │ - Calls /api/messages/view/<id>         │
   │ - Server increments view_count          │
   └────────────────────────────────────────┘


3. USER CLICKS CTA BUTTON
   ┌─────────────────────────────────────────┐
   │ User clicks "Shop Now" button           │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ JavaScript trackMessageClick() called   │
   │ - Sends AJAX request                    │
   │ - Calls /api/messages/click/<id>        │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Flask endpoint processes request        │
   │ - Get DynamicMessage by ID              │
   │ - Increment click_count                 │
   │ - db.session.commit()                   │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Return JSON response                    │
   │ { "success": true }                     │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ User navigates to target URL            │
   │ (e.g., /products, /sale)                │
   └────────────────────────────────────────┘


4. ADMIN VIEWS ANALYTICS
   ┌─────────────────────────────────────────┐
   │ Admin navigates to /admin/messages      │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Flask admin_messages() route executes   │
   │ - Query all DynamicMessage records      │
   │ - Apply optional filters                │
   │ - Sort by display_order                 │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Render admin/messages.html              │
   │ - Display message list                  │
   │ - Show views/clicks for each            │
   │ - Calculate CTR (click_count/view_count)│
   │ - Show statistics cards                 │
   └────────────┬────────────────────────────┘
                │
   ┌────────────▼────────────────────────────┐
   │ Return dashboard to admin               │
   │ - View real-time analytics              │
   │ - Monitor performance                   │
   └────────────────────────────────────────┘
```

## Database Schema Diagram

```
dynamic_message table
┌──────────────────────────────────────────────────┐
│ Column              │ Type        │ Purpose      │
├──────────────────────────────────────────────────┤
│ id                  │ INTEGER PK  │ Primary key  │
├──────────────────────────────────────────────────┤
│ CONTENT FIELDS                                   │
│ title               │ VARCHAR     │ Headline     │
│ content             │ TEXT        │ Message body │
│ message_type        │ VARCHAR     │ Type/badge   │
├──────────────────────────────────────────────────┤
│ SCHEDULING FIELDS                                │
│ is_active           │ BOOLEAN     │ Show/hide    │
│ start_date          │ DATETIME    │ When to show │
│ end_date            │ DATETIME    │ When to hide │
├──────────────────────────────────────────────────┤
│ DISPLAY FIELDS                                   │
│ display_location    │ VARCHAR     │ Where to show│
│ background_color    │ VARCHAR(10) │ Hex color    │
│ text_color          │ VARCHAR(10) │ Hex color    │
│ icon                │ VARCHAR     │ FA icon      │
│ display_order       │ INTEGER     │ Priority     │
├──────────────────────────────────────────────────┤
│ CTA FIELDS                                       │
│ cta_text            │ VARCHAR     │ Button text  │
│ cta_url             │ VARCHAR     │ Button URL   │
├──────────────────────────────────────────────────┤
│ ANALYTICS FIELDS                                 │
│ view_count          │ INTEGER     │ Impressions  │
│ click_count         │ INTEGER     │ CTA clicks   │
├──────────────────────────────────────────────────┤
│ METADATA FIELDS                                  │
│ created_by_id       │ INTEGER FK  │ Creator      │
│ updated_by_id       │ INTEGER FK  │ Last editor  │
│ created_at          │ DATETIME    │ Created time │
│ updated_at          │ DATETIME    │ Updated time │
└──────────────────────────────────────────────────┘

INDEXES
┌──────────────────────────────────┐
│ idx_is_active                    │
│ idx_display_location             │
│ idx_start_date                   │
└──────────────────────────────────┘

FOREIGN KEYS
┌──────────────────────────────────┐
│ created_by → user.id             │
│ updated_by → user.id             │
└──────────────────────────────────┘
```

## Component Interaction Map

```
                    ┌──────────────┐
                    │   Frontend   │
                    │  (index.html)│
                    └───────┬──────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
         View Tracking            Click Tracking
         (Intersection Obs)        (onclick handler)
              │                           │
         /api/messages/          /api/messages/
         view/<id>               click/<id>
              │                           │
              └─────────────┬─────────────┘
                            │
                    ┌───────▼────────┐
                    │  Flask Routes  │
                    │  (app.py)      │
                    └───────┬────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
      Admin           Analytics          Homepage
      Routes          Endpoints           Route
         │                  │                  │
    /admin/         /api/messages/         /
    messages*           click/<id>
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                    ┌───────▼────────┐
                    │  SQLAlchemy    │
                    │  Models        │
                    └───────┬────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
      DynamicMessage            Database Session
      Model                      Operations
            │                               │
            └───────────────┬───────────────┘
                            │
                    ┌───────▼────────┐
                    │  SQLite DB     │
                    │  dynamic_      │
                    │  message       │
                    │  table         │
                    └────────────────┘
```

## Admin UI Flow

```
┌─────────────────────────────────────────────┐
│        Admin Dashboard                      │
│        /admin/messages                      │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ Filter Buttons                        │ │
│  │ [All] [Active] [Inactive] [Scheduled] │ │
│  │      [Expired]                        │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ Statistics Cards                      │ │
│  │ Total: 5  Active: 3  Views: 1,234     │ │
│  │ Clicks: 89  CTR: 7.2%                 │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ Messages Table                        │ │
│  │ Title | Type | Location | Status | .. │ │
│  │ ───────────────────────────────────── │ │
│  │ Sale  | Promo| Homepage | Active | ✓ │ │
│  │ Maint | Alert| All Pages| Inact  | ✓ │ │
│  │                                      │ │
│  │ [Edit] [Toggle] [Delete] [Stats]     │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │ [➕ Create Message]                 │  │
│  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
           │                    │
           ▼                    ▼
    ┌────────────────┐  ┌────────────────┐
    │ Create/Edit    │  │ View Stats     │
    │ Form Page      │  │ Details Page   │
    │                │  │                │
    │ • Title        │  │ • Views: 450   │
    │ • Content      │  │ • Clicks: 32   │
    │ • Colors       │  │ • CTR: 7.1%    │
    │ • Icon         │  │ • Creator: xxx │
    │ • CTA Button   │  │ • Created: xxx │
    │ • Schedule     │  │ • Updated: xxx │
    │ • Live Preview │  │                │
    │                │  │ [Edit] [Delete]│
    │ [Save] [Cancel]│  └────────────────┘
    └────────────────┘
```

## User Experience Flow

```
┌─────────────────────────────────────────┐
│        User Visits Homepage              │
│        GET /                             │
└──────────────────┬──────────────────────┘
                   │
         ┌─────────▼──────────┐
         │ Page Loads         │
         │ - Hero Section     │
         │ - Categories       │
         │ - Products         │
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────────────┐
         │ Dynamic Messages           │
         │ Rendered Below Hero        │
         │                            │
         │ ┌────────────────────────┐ │
         │ │ 🎁 Summer Sale        │ │
         │ │ Get 40% off items!    │ │
         │ │ [Shop Now] →          │ │
         │ └─────────┬──────────────┘ │
         │           │                │
         │       Intersection          │
         │       Observer fires        │
         │           │                │
         │       /api/messages/       │
         │       view/<id>            │
         │           │                │
         │       View count +1        │
         │                            │
         │ [If clicked]               │
         │       │                    │
         │       ▼                    │
         │   trackMessageClick()      │
         │       │                    │
         │   /api/messages/click/<id> │
         │       │                    │
         │   Click count +1           │
         │       │                    │
         │   Navigate to URL          │
         └────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Production Environment          │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Web Server (Gunicorn)            │  │
│  │ - 4-8 worker processes           │  │
│  │ - Load balanced                  │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
│  ┌──────────────▼───────────────────┐  │
│  │ Flask Application                │  │
│  │ - Dynamic message routes         │  │
│  │ - Admin CRUD operations          │  │
│  │ - Analytics tracking             │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
│  ┌──────────────▼───────────────────┐  │
│  │ SQLAlchemy ORM                   │  │
│  │ - Query caching (optional)       │  │
│  │ - Connection pooling             │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
│  ┌──────────────▼───────────────────┐  │
│  │ SQLite Database                  │  │
│  │ - dynamic_message table          │  │
│  │ - Optimized indexes              │  │
│  │ - Backup strategy                │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

## Security Architecture

```
┌──────────────────────────────────────────────┐
│      Security Layers                         │
│                                              │
│  Layer 1: Authentication                     │
│  ├─ @login_required decorator                │
│  ├─ Session management                       │
│  └─ User identity verification               │
│                                              │
│  Layer 2: Authorization                      │
│  ├─ Admin role verification                  │
│  ├─ Route access control                     │
│  └─ Feature-level permissions                │
│                                              │
│  Layer 3: Input Validation                   │
│  ├─ Form field validation                    │
│  ├─ URL parameter validation                 │
│  ├─ Color code validation                    │
│  └─ HTML sanitization (Jinja2 safe)          │
│                                              │
│  Layer 4: Data Protection                    │
│  ├─ Database transactions                    │
│  ├─ Error handling                           │
│  ├─ Audit logging                            │
│  └─ Activity tracking                        │
│                                              │
│  Layer 5: Frontend Security                  │
│  ├─ XSS prevention                           │
│  ├─ CSRF tokens (if enabled)                 │
│  ├─ Safe event binding                       │
│  └─ Input sanitization                       │
│                                              │
└──────────────────────────────────────────────┘
```

---

**This architecture ensures**:
✅ Scalable message management
✅ Robust analytics tracking
✅ Secure admin operations
✅ Responsive user experience
✅ Maintainable codebase
