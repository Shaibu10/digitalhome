# SMS MANAGEMENT SYSTEM - QUICK START GUIDE

## 🚀 Quick Setup (5 minutes)

### 1. Configure mNotify API Key
Add to your `.env` file or set as environment variable:
```
MNOTIFY_API_KEY=your_api_key_from_mnotify_dashboard
```

### 2. Start the Application
```bash
flask run
```
Server runs at: `http://127.0.0.1:5000`

### 3. Login to Admin Panel
- **URL**: http://127.0.0.1:5000/
- **Email**: admin@example.com
- **Password**: admin123

### 4. Access SMS Dashboard
- **URL**: http://127.0.0.1:5000/admin/sms/
- All SMS features available from here

---

## 📱 Common Tasks

### Send a Single SMS
1. Go to `/admin/sms/` (Dashboard)
2. Click "Send Single SMS" button
3. Select recipient user from dropdown
4. Type your message (character count updates in real-time)
5. Message shows SMS parts needed (160 chars = 1 SMS, or 70 for Unicode)
6. Click "Send SMS" button
7. View status in Activity Log

### Create SMS Template
1. Go to `/admin/sms/templates`
2. Click "Create New Template" button
3. Fill in:
   - **Template Name**: e.g., "Order Confirmation"
   - **Category**: e.g., "orders", "shipping", "verification"
   - **Description**: What this template is for
   - **Content**: Message text with {variables}
     - Example: `Your order #{order_id} confirmed. Delivery: {delivery_date}`
4. Variables automatically extracted from curly braces
5. Click "Save Template"

**Variable Examples:**
```
{order_id}        - Order number
{delivery_date}   - Expected delivery date
{tracking_number} - Shipment tracking
{user_name}       - Recipient name
{code}            - Verification or promo code
{discount}        - Discount percentage
```

### Send Bulk Campaign
1. Go to `/admin/sms/campaigns` → "Create Campaign"
2. Fill in:
   - **Campaign Name**: "May Promo SMS"
   - **Description**: Optional details
   - **Template Selection**: Pick existing template or custom message
   - **Recipient Filter**: 
     - "All Users" - send to everyone
     - "Active Users" - only active accounts
     - "Verified Only" - confirmed email only
   - **Batch Size**: 100 (default, adjust if needed)
   - **Enable Retry**: Check to retry failed messages
3. Click "Preview Campaign" to see sample recipients
4. Click "Create Campaign"
5. On campaign detail page, click "Send Campaign"
6. Confirm sending
7. Monitor progress in Activity Log

**Recipient Filters:**
- All Users: Everyone in database
- Active Users: Account status = active
- Verified Users: Email verified only
- By Status: Select specific status
- By Group: If you have user groups

### Manage Blacklist
1. Go to `/admin/sms/blacklist`
2. **Add Phone to Blacklist:**
   - Click "Add to Blacklist"
   - Enter phone number
   - Enter reason (optional)
   - Click "Add"
3. **Remove from Blacklist:**
   - Find phone in list
   - Click "Remove" button
   - Confirm

**Blacklist prevents:**
- Sending SMS to blocked numbers
- Campaign messages to blacklisted users
- Both single and bulk sends

### View Activity & History
1. **Dashboard** - See overall statistics
2. **Activity Log** (/admin/sms/activity) - All admin actions:
   - Who sent what
   - When it was sent
   - IP address & browser info
3. **Message History** (/admin/sms/messages) - Individual message tracking:
   - Delivery status
   - Error messages
   - Retry attempts
   - Cost per message

---

## 📊 Monitoring & Analytics

### Dashboard Statistics
- **Total SMS Sent**: Cumulative count
- **Delivered**: Successfully delivered
- **Failed**: Delivery failed
- **Pending**: Awaiting confirmation
- **Delivery Rate**: Success percentage

### Campaign Analytics
- **Recipients**: Number of users targeted
- **Sent**: Messages successfully sent
- **Delivered**: Confirmed received
- **Failed**: Delivery failed
- **Retry**: Messages being retried

### Message Costs
Each SMS shows:
- **SMS Parts**: How many SMS credits used (160 chars = 1 part)
- **Cost**: Price per SMS (varies by length)
- **Total**: Cost per message

---

## 🔄 Automatic Features

### Retry Logic
- Failed messages automatically retry
- Configurable retry count (default: 3)
- Retry delay: 5 minutes between attempts
- After max retries, marked as failed
- View failures in Activity Log

### Phone Validation
Supported formats (Ghana numbers):
- `+233123456789`
- `233123456789`
- `0123456789`
All converted to international format

### SMS Length Calculation
- **ASCII Text**: 160 characters per SMS
  - Example: "Hello world" = 1 SMS
  - Maximum 9 SMS per message
- **Unicode**: 70 characters per SMS
  - Example: "مرحبا" (Arabic) = 1 SMS
  - Maximum 3 SMS per message
- Character counter shows in real-time

### Character Counting
- Enter message → Counter updates instantly
- Shows SMS parts needed
- Warns if too long
- HTML entities not counted (only actual characters)

---

## 🛡️ Security Features

### Admin-Only Access
- All SMS routes require admin login
- Non-admin users redirected to login
- Session timeout after 30 minutes inactivity

### Activity Audit Trail
Every SMS action logged:
- Who sent it (admin name/email)
- What was sent (template, message)
- When it was sent (timestamp)
- Where from (IP address, browser)
- Result (success/failure)

**View Audit Log:**
Go to `/admin/sms/activity` to see complete history

### Rate Limiting
- Prevents spam/abuse
- Limits sends per user per hour
- Configurable thresholds
- Exceeded sends logged as security event

---

## 🔧 Troubleshooting

### "SMS service disabled" Warning
**Cause**: MNOTIFY_API_KEY not configured
**Solution**: 
1. Add API key to `.env` file
2. Restart Flask server
3. Warning disappears when key is set

### SMS Not Sending
**Check:**
1. Phone number format valid? (Must be Ghana format)
2. Phone not on blacklist?
3. mNotify API key configured?
4. Check Activity Log for error message

### "Table category already exists" Error
**Cause**: Old migration conflict
**Solution**: Already fixed! Database recreated fresh

### Campaign Shows 0 Recipients
**Cause**: No users matching filter criteria
**Solution**:
1. Check filter settings
2. Use "All Users" to test
3. Verify users exist in database

### Failed Messages Not Retrying
**Check:**
1. "Enable Retry" checkbox marked when creating campaign?
2. Retry count not exceeded?
3. Check error reason in message details

---

## 📧 Integration Examples

### Send SMS on Order Confirmation
```python
from sms.service import SMSManager

manager = SMSManager()
manager.send_single_sms(
    user_id=order.user_id,
    message=f"Your order #{order.id} confirmed"
)
```

### Send SMS on Account Verification
```python
from sms.service import send_verification_sms

send_verification_sms(user, verification_code="123456")
```

### Send SMS on Password Reset
```python
from sms.service import send_password_reset_sms

send_password_reset_sms(user, reset_code="abc123")
```

### Send SMS on Shipping
```python
from sms.service import send_promotional_sms

send_promotional_sms(
    user_id=order.user_id,
    message=f"Your order shipped! Track: {tracking_url}"
)
```

---

## 📋 API Reference

### GET /admin/sms/
SMS Dashboard - displays statistics and recent activity

### GET/POST /admin/sms/single
Send single SMS to one user
- POST data: `user_id`, `message`
- Returns: redirect to activity log on success

### GET /admin/sms/templates
List all SMS templates

### GET/POST /admin/sms/templates/create
Create new SMS template
- POST data: `name`, `category`, `content`, `description`

### GET /admin/sms/templates/{id}/edit
Edit existing template
- POST data: `name`, `category`, `content`, `description`

### GET /admin/sms/campaigns
List all SMS campaigns

### GET/POST /admin/sms/campaigns/create
Create new bulk campaign
- POST data: `name`, `template_id`, `recipient_filter`, `batch_size`

### POST /admin/sms/campaigns/{id}/send
Execute campaign send
- Marks campaign as sent
- Sends all messages in batches

### POST /admin/sms/campaigns/{id}/retry
Retry failed messages in campaign

### GET /admin/sms/activity
View activity audit log

### GET /admin/sms/blacklist
Manage phone blacklist

### POST /admin/sms/blacklist/add
Add phone to blacklist
- POST data: `phone_number`, `reason`

---

## 💡 Best Practices

1. **Use Templates**: Reuse templates for consistency
2. **Test First**: Send test message before bulk campaign
3. **Schedule Wisely**: Send during business hours (9am-6pm)
4. **Monitor Delivery**: Check Activity Log after sending
5. **Keep Records**: Audit log automatically tracks all sends
6. **Plan Content**: Character limits? Use template preview
7. **Check Blacklist**: Don't send to unwanted numbers
8. **Use Variables**: Personalize with {user_name}, {order_id}
9. **Review Costs**: High-length messages cost more SMS credits
10. **Batch Large Campaigns**: Split into smaller batches if >10k users

---

## 📞 Support

**Feature Issues?**
1. Check Activity Log for errors
2. Verify mNotify API key is set
3. Ensure phone numbers are valid Ghana format
4. Check user exists and is not blacklisted

**Database Issues?**
```bash
# Reset database (DANGER - deletes all data!)
flask db downgrade base
flask db upgrade
```

---

## ✅ Checklist for First SMS Send

- [ ] mNotify API key configured in .env
- [ ] Flask server running (flask run)
- [ ] Logged in as admin (admin@example.com / admin123)
- [ ] Visited /admin/sms/ dashboard
- [ ] Created at least 1 SMS template
- [ ] Have target user(s) in database
- [ ] Phone numbers in valid Ghana format
- [ ] Phone number not on blacklist
- [ ] Character count under SMS limits
- [ ] Hit "Send SMS" button
- [ ] Check Activity Log for confirmation
- [ ] Verify mNotify dashboard shows message sent

---

**SMS System Ready to Use! 🎉**
