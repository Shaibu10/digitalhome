# Dynamic Message System - Complete Implementation Guide

## Overview

The Dynamic Message System allows administrators to create, schedule, and manage messages that display on the homepage and across the site. Messages include built-in analytics (view counts, click-through rates) and rich customization options (colors, icons, CTAs).

## Architecture

### Components

1. **Database Model** (`models.py`)
   - `DynamicMessage` class with 18 fields
   - Scheduling support (start_date, end_date)
   - Analytics tracking (view_count, click_count)
   - User relationships (created_by, updated_by)

2. **Admin Routes** (`app.py`)
   - List messages with filtering (all/active/inactive/scheduled/expired)
   - Create new messages with validation
   - Edit existing messages
   - Delete messages
   - Toggle active status
   - View/click analytics endpoints

3. **User Interface**
   - Admin dashboard (`templates/admin/messages.html`)
   - Create message form (`templates/admin/add_message.html`)
   - Edit message form (`templates/admin/edit_message.html`)
   - Homepage display (`templates/index.html`)

4. **Tracking**
   - View tracking via Intersection Observer API
   - Click tracking on CTA buttons
   - Analytics displayed in admin dashboard

## Database Schema

```sql
CREATE TABLE dynamic_message (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'info',
    is_active BOOLEAN DEFAULT TRUE,
    start_date DATETIME,
    end_date DATETIME,
    display_location VARCHAR(100) DEFAULT 'homepage',
    background_color VARCHAR(10) DEFAULT '#007bff',
    text_color VARCHAR(10) DEFAULT '#ffffff',
    icon VARCHAR(50) DEFAULT 'info-circle',
    cta_text VARCHAR(100),
    cta_url VARCHAR(500),
    click_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    display_order INTEGER DEFAULT 0,
    created_by_id INTEGER,
    updated_by_id INTEGER,
    created_at DATETIME,
    updated_at DATETIME
);

-- Indexes for performance
CREATE INDEX idx_is_active ON dynamic_message(is_active);
CREATE INDEX idx_display_location ON dynamic_message(display_location);
CREATE INDEX idx_start_date ON dynamic_message(start_date);
```

## DynamicMessage Model Methods

### Helper Methods

```python
class DynamicMessage(db.Model):
    
    @staticmethod
    def get_active_messages():
        """Get all currently active and scheduled messages"""
        return DynamicMessage.query.filter(
            DynamicMessage.is_active == True,
            DynamicMessage.start_date <= now,
            (DynamicMessage.end_date == None) | (DynamicMessage.end_date >= now)
        ).order_by(DynamicMessage.display_order).all()
    
    @staticmethod
    def get_active_homepage_messages():
        """Get active messages for homepage display"""
        now = datetime.utcnow()
        return DynamicMessage.query.filter(
            DynamicMessage.is_active == True,
            DynamicMessage.display_location.in_(['homepage', 'all_pages']),
            (DynamicMessage.start_date == None) | (DynamicMessage.start_date <= now),
            (DynamicMessage.end_date == None) | (DynamicMessage.end_date >= now)
        ).order_by(DynamicMessage.display_order.asc()).all()
    
    def is_currently_active(self):
        """Check if message should currently be displayed"""
        now = datetime.utcnow()
        return (
            self.is_active and
            (self.start_date is None or self.start_date <= now) and
            (self.end_date is None or self.end_date >= now)
        )
    
    def is_scheduled(self):
        """Check if message is scheduled for future display"""
        return self.start_date and self.start_date > datetime.utcnow()
    
    def is_expired(self):
        """Check if message has passed its end date"""
        return self.end_date and self.end_date < datetime.utcnow()
    
    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
    
    def increment_clicks(self):
        """Increment click count"""
        self.click_count += 1
```

## Admin Routes

### List Messages
- **Route**: `GET /admin/messages`
- **Feature**: View all messages with filtering
- **Filters**: All, Active, Inactive, Scheduled, Expired
- **Display**: Title, type, location, status badges, analytics

### Create Message
- **Route**: `GET /admin/messages/add` (form) | `POST /admin/messages/add` (submit)
- **Form Fields**:
  - Title (required, max 200 chars)
  - Content (required, HTML-safe)
  - Message type (info/promotion/warning/alert/success)
  - Display location (homepage/all_pages)
  - Active status (checkbox)
  - Schedule (optional start/end dates)
  - Colors (background, text - color pickers)
  - Icon (Font Awesome class)
  - CTA (optional button text & URL)
  - Display order (priority)
- **Features**: Live preview, validation, audit logging

### Edit Message
- **Route**: `GET /admin/messages/edit/<id>` (form) | `POST /admin/messages/edit/<id>` (submit)
- **Features**: Pre-populated form, analytics display, metadata (creator, timestamps)

### Delete Message
- **Route**: `POST /admin/messages/delete/<id>`
- **Behavior**: Logs deletion to activity log

### Toggle Active Status
- **Route**: `GET /admin/messages/toggle/<id>`
- **Behavior**: Toggles `is_active` field without requiring edit form

### Click Tracking API
- **Route**: `GET /api/messages/click/<id>`
- **Behavior**: Increments `click_count` for CTA button clicks

### View Tracking API
- **Route**: `GET /api/messages/view/<id>`
- **Behavior**: Increments `view_count` when message enters viewport

## Frontend Integration

### Homepage Display

Messages are displayed in a dedicated section on the homepage:

```html
<!-- Dynamic Messages Section -->
{% if dynamic_messages %}
<section class="dynamic-messages-container">
    <div class="container">
        {% for message in dynamic_messages %}
        <div class="dynamic-message" 
             style="background-color: {{ message.background_color }}; 
                    color: {{ message.text_color }};">
            
            <div class="dynamic-message-icon">
                <i class="fas fa-{{ message.icon }}"></i>
            </div>
            
            <div class="dynamic-message-content">
                <h4 class="dynamic-message-title">{{ message.title }}</h4>
                <div class="dynamic-message-body">
                    {{ message.content | safe }}
                </div>
                
                {% if message.cta_text and message.cta_url %}
                <a href="{{ message.cta_url }}" class="dynamic-message-cta"
                   onclick="trackMessageClick({{ message.id }})">
                    {{ message.cta_text }}
                </a>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
</section>
{% endif %}
```

### JavaScript Tracking

```javascript
// Track view using Intersection Observer
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const messageId = entry.target.dataset.messageId;
            fetch(`/api/messages/view/${messageId}`);
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

// Track CTA button clicks
function trackMessageClick(messageId) {
    fetch(`/api/messages/click/${messageId}`);
}
```

## Message Types

| Type | Default Color | Use Case |
|------|---------------|----------|
| `info` | #007bff (blue) | General information |
| `promotion` | #28a745 (green) | Sales, special offers |
| `warning` | #ffc107 (yellow) | Important alerts |
| `alert` | #dc3545 (red) | Critical warnings |
| `success` | #28a745 (green) | Confirmation messages |

## Display Locations

- **homepage**: Only shown on homepage
- **all_pages**: Shown on all pages throughout the site

## Admin Features

### Filtering
- **All**: Show all messages
- **Active**: Currently displayed messages
- **Inactive**: Messages with `is_active=False`
- **Scheduled**: Messages with future `start_date`
- **Expired**: Messages past their `end_date`

### Analytics Dashboard
- View count per message
- Click count per message
- Click-through rate calculation
- Total site statistics

### Message Metadata
- Creator name and timestamp
- Last editor name and timestamp
- Audit trail of changes

## Testing

### Run Tests
```bash
python test_dynamic_messages.py
```

### Test Coverage
1. ✅ Database table exists
2. ✅ Create messages
3. ✅ Query active messages
4. ✅ Scheduling logic (future dates)
5. ✅ Analytics tracking (views/clicks)
6. ✅ Homepage message retrieval
7. ✅ Expiration logic (past dates)

## Example Use Cases

### 1. Homepage Banner Promotion
```
Title: "Summer Sale 2025"
Content: "Get 30% off all electronics this summer!"
Type: promotion
Location: homepage
Background: #28a745 (green)
Icon: gift
CTA: "Shop Now" → /products?category=electronics
Schedule: 2025-06-01 to 2025-08-31
```

### 2. Alert for System Maintenance
```
Title: "System Maintenance"
Content: "We'll be performing system updates tonight (11 PM - 2 AM GMT)"
Type: alert
Location: all_pages
Background: #ffc107 (yellow)
Icon: wrench
Schedule: 2025-03-15 21:00 to 2025-03-16 02:00
```

### 3. New Feature Announcement
```
Title: "New Payment Method Available"
Content: "We now accept <strong>Orange Money</strong> payments!"
Type: success
Location: homepage
Background: #007bff (blue)
Icon: credit-card
CTA: "Learn More" → /payment-methods
```

## Performance Considerations

### Database Indexes
- `is_active`: For filtering active messages
- `display_location`: For homepage-specific queries
- `start_date`: For scheduling queries

### Query Optimization
- Use `get_active_homepage_messages()` for homepage display
- Messages are ordered by `display_order` to control appearance sequence
- View/click tracking is non-blocking (AJAX calls)

### Caching Strategy
- Consider caching homepage messages (5-minute TTL) in production
- Cache invalidates on message update

## Security

### Input Validation
- Title: Max 200 characters, required
- Content: HTML-safe (uses Jinja2 `| safe` filter)
- URLs: Validated for correct format
- Colors: Validated as hex codes

### Authorization
- All admin routes require `@login_required` decorator
- `@is_admin` check ensures only admins can manage messages
- Activity logging for audit trail

### XSS Protection
- User content sanitized through Jinja2
- Icon classes validated from whitelist
- CTA URLs checked before linking

## Future Enhancements

1. **Rich Text Editor**: Integrate TinyMCE or similar for better HTML editing
2. **Message Templates**: Pre-designed templates for common message types
3. **A/B Testing**: Compare different message versions
4. **Targeting**: Show messages based on user segments
5. **Bulk Actions**: Edit multiple messages at once
6. **Analytics Export**: Export view/click data as CSV
7. **Message Scheduling UI**: Calendar view for scheduling
8. **Mobile Push**: Send critical messages as push notifications

## Files Modified/Created

### Created
- `migrations/versions/add_dynamic_message_model.py` - Database migration
- `templates/admin/messages.html` - Admin list view
- `templates/admin/add_message.html` - Create form
- `templates/admin/edit_message.html` - Edit form
- `test_dynamic_messages.py` - Test suite

### Modified
- `models.py` - Added `DynamicMessage` class
- `app.py` - Added 8 routes (7 admin + 1 API)
- `templates/index.html` - Added message display section

## Configuration

### Default Values
```python
DynamicMessage(
    message_type='info',
    is_active=True,
    display_location='homepage',
    background_color='#007bff',
    text_color='#ffffff',
    icon='info-circle',
    display_order=0,
    click_count=0,
    view_count=0
)
```

## Troubleshooting

### Messages Not Displaying
1. Check `is_active` is `True`
2. Verify current date is within `start_date` and `end_date`
3. Confirm `display_location` includes 'homepage' or 'all_pages'
4. Clear browser cache and refresh

### Analytics Not Tracking
1. Verify JavaScript console has no errors
2. Check `/api/messages/view/` and `/api/messages/click/` endpoints respond
3. Confirm database writes are succeeding (check Flask logs)

### Database Migration Failed
1. Run: `flask db upgrade`
2. Verify migration file exists in `migrations/versions/`
3. Check database compatibility and permissions

## Support

For issues or questions, refer to the implementation files:
- Model logic: `models.py` (lines ~369-452)
- Routes: `app.py` (lines ~2402-2683 and tracking endpoints)
- Templates: `templates/admin/` and `templates/index.html`
- Tests: `test_dynamic_messages.py`
