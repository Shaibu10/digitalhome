# 📱 SMS SYSTEM - STEP BY STEP USER GUIDE

## Initial Setup

### Prerequisites
- ✅ Flask server running (`flask run`)
- ✅ Admin user created (admin@example.com / admin123)
- ✅ mNotify account with API key (optional for testing)

### Step 0: Configure mNotify (Optional but Recommended)

To send **real SMS messages**:

1. Get API key from https://mnotify.com/
2. Add to `.env` file:
   ```
   MNOTIFY_API_KEY=your_key_here
   ```
3. Restart Flask server
4. Warning "SMS service disabled" will disappear

**For testing without real SMS:**
- No configuration needed!
- Messages log to console
- Perfect for development

---

## 🔐 Part 1: Login to Admin Panel

### Step 1: Navigate to Login
- Open browser: http://localhost:5000/
- You'll see the DigitalHome homepage
- Click "Admin Panel" or go to http://localhost:5000/auth/login

### Step 2: Enter Credentials
- **Email**: admin@example.com
- **Password**: admin123
- Click "Login"

### Step 3: Verify Login Success
- You're now logged in as admin
- You can see admin menu with SMS option
- You should see "SMS Management" link

### Step 4: Access SMS Dashboard
- Click "SMS Management" from admin menu
- Or navigate directly: http://localhost:5000/admin/sms/
- You'll see the SMS Dashboard with statistics

---

## 📊 Part 2: SMS Dashboard Overview

### Dashboard Components

**Top Statistics Cards:**
- **Total SMS Sent** - All SMS ever sent
- **Delivered** - Successfully delivered
- **Failed** - Delivery failed  
- **Pending** - Currently in queue
- **Delivery Rate** - Success percentage

**Recent Campaigns Widget:**
- Shows last 5 campaigns
- Status (pending, sent, completed)
- Recipient count
- Action buttons

**Recent Activity Widget:**
- Last 10 admin actions
- Who did what
- When they did it

**Quick Action Buttons:**
- "Send Single SMS" - Send to one user
- "Create Campaign" - Send to many users
- "Manage Templates" - View/edit SMS templates
- "View Activity" - See audit log

---

## 💌 Part 3: Send a Single SMS

### Scenario: Send SMS to one customer

### Step 1: Open Send Single SMS
1. From dashboard, click "Send Single SMS" button
2. Or navigate: http://localhost:5000/admin/sms/single
3. You'll see a form with fields:
   - **Select Recipient** - Dropdown of users
   - **Message** - Text area for SMS
   - **Character Counter** - Shows current count

### Step 2: Select Recipient
1. Click the dropdown "Select a user"
2. See list of users with email and phone
3. Choose one (e.g., first user)
4. Their phone number auto-fills

### Step 3: Compose Message
1. Click in message text area
2. Type your message (e.g., "Hi! Your order is ready for pickup!")
3. Watch **Character Counter** update in real-time

**Character Counter Shows:**
- Current character count (e.g., "45 chars")
- Number of SMS needed (e.g., "1 SMS")
- SMS parts calculation:
  - 160 chars = 1 SMS (ASCII text)
  - 70 chars = 1 SMS (Unicode/emojis)

### Step 4: Preview
1. Message displays in preview panel
2. Shows exactly what recipient will see
3. Check for typos or issues

### Step 5: Send SMS
1. Click **"Send SMS"** button
2. Confirmation message appears
3. You're redirected to activity log
4. Message shown as "Sent" with timestamp

### Step 6: Verify Delivery
1. In Activity Log, find your message
2. Status column shows:
   - ✅ Sent (successfully sent)
   - ⏳ Pending (still processing)
   - ❌ Failed (delivery failed)
3. Click message for details

---

## 📧 Part 4: Create SMS Template

### Scenario: Create template for order notifications

### Step 1: Navigate to Templates
1. From dashboard, click "Manage Templates"
2. Or go to: http://localhost:5000/admin/sms/templates
3. You'll see list of existing templates (10 pre-loaded)

### Step 2: Create New Template
1. Click **"Create New Template"** button
2. Form opens with fields:
   - **Template Name** - e.g., "Special Offer"
   - **Category** - Choose category
   - **Description** - Purpose of template
   - **Content** - Message text

### Step 3: Fill Template Details

**Template Name:**
- Type: "Birthday Discount"
- Keep it descriptive

**Category:**
- Click dropdown, choose "marketing" or "orders"
- Or create custom category

**Description:**
- Type: "Send birthday discount offer to customers"
- This helps remember what template does

### Step 4: Add Message with Variables

**Template Content:**
- Type: "Happy Birthday {user_name}! Enjoy {discount}% off your entire order. Use code {promo_code}"

**Variables in Content:**
- Use {variable_name} format
- Variables auto-extracted on save
- System recognizes: {user_name}, {discount}, {promo_code}

**Available Variables:**
- {user_name} - Recipient's name
- {order_id} - Order number
- {delivery_date} - Expected delivery
- {tracking_number} - Shipment tracking
- {code} - Verification/promo code
- {discount} - Discount percentage
- {amount} - Currency amount
- {balance} - Account balance
- Any custom variable you create

### Step 5: Preview
1. Character counter shows: "125 chars = 1 SMS"
2. Preview shows how variables will look
3. Variables highlighted in blue

### Step 6: Save Template
1. Click **"Save Template"** button
2. Template saved to database
3. Redirected to templates list
4. New template appears in list

### Step 7: Use Template Later
1. When creating campaign, choose this template
2. System auto-fills template content
3. Just provide variable values
4. Send to recipients

---

## 🚀 Part 5: Create Bulk Campaign

### Scenario: Send bulk SMS to all customers for flash sale

### Step 1: Navigate to Campaigns
1. From dashboard, click "Create Campaign"
2. Or go to: http://localhost:5000/admin/sms/campaigns/create
3. Campaign creation form appears

### Step 2: Fill Campaign Details

**Campaign Name:**
- Type: "Flash Sale June 2024"
- Keep it descriptive

**Description:**
- Type: "Limited time offer - 50% off selected items"
- Optional but helpful for records

### Step 3: Choose Message Source

**Option A: Use Template**
- Click dropdown "Select Template"
- Choose "Flash Sale Alert" (pre-loaded template)
- Template content auto-fills
- Variables shown for filling

**Option B: Custom Message**
- Leave template empty
- Type custom message directly
- Add variables if needed

### Step 4: Set Recipients

**Recipient Filter:**
- Click dropdown "Who should receive?"
- Options:
  - "All Users" - Every registered user
  - "Active Users" - Account status = active
  - "Verified Users" - Email verified only
  - "By Status" - Choose specific status
  - "By Group" - If you have groups

**For this example:**
- Choose "All Users"
- System shows estimated count (e.g., "125 users")

### Step 5: Configure Sending

**Batch Size:**
- Default: 100
- Batch size = messages sent per cycle
- Larger batch = faster send but more API calls
- Keep 100-500 for stability

**Schedule Sending:**
- "Now" - Send immediately
- "Scheduled" - Pick date/time
- Click calendar to pick future time

**Retry Settings:**
- Check "Automatically retry failed"
- Max retries: 3 (default)
- Retry delay: 5 minutes

### Step 6: Preview Campaign
1. Click **"Preview Campaign"** button
2. Shows sample recipients
3. Shows sample message
4. Verify everything looks correct

### Step 7: Create Campaign
1. Click **"Create Campaign"** button
2. Campaign saved to database
3. Shows campaign details page
4. Status: "Draft" (not sent yet)

### Step 8: Send Campaign
1. On campaign details page, click **"Send Campaign"** button
2. Confirmation dialog appears
3. Confirm by clicking "Yes, Send Campaign"
4. Sending begins!

### Step 9: Monitor Progress
1. Page refreshes showing:
   - **Status**: Changed to "Sending"
   - **Messages Sent**: Count updates
   - **Messages Failed**: Count updates
   - **Progress Bar**: Shows % complete
2. Can watch in real-time as messages send
3. Each batch processes, then next batch

### Step 10: Campaign Complete
1. Status changes to "Completed"
2. Shows final statistics:
   - Total recipients: 125
   - Messages sent: 123
   - Messages failed: 2
   - Delivery rate: 98.4%
3. Failed messages shown for review

### Step 11: Retry Failed Messages
1. If any failed, click **"Retry Failed"** button
2. System retries only failed messages
3. Sends up to max_retries times
4. Check Activity Log for details

---

## 🚫 Part 6: Manage Blacklist

### Scenario: Block customer from SMS

### Step 1: Navigate to Blacklist
1. From dashboard, click "View Blacklist"
2. Or go to: http://localhost:5000/admin/sms/blacklist
3. You see current blacklisted numbers

### Step 2: Add to Blacklist

**Option A: From Blacklist Page**
1. Click **"Add to Blacklist"** button
2. Form appears with fields:
   - Phone Number (required)
   - Reason (optional)
3. Type phone number: "+233123456789" or "0123456789"
4. Type reason: "Unsubscribed" or "Do Not Call"
5. Click "Add to Blacklist"
6. Phone added, appears in list

**Option B: Automatic**
- When system detects "STOP" reply from user
- Automatically adds to blacklist
- Reason recorded in system

### Step 3: View Blacklist
1. Blacklist table shows:
   - Phone number (formatted)
   - Reason for blocking
   - Date added
   - Admin who added it
   - Remove button

### Step 4: Remove from Blacklist
1. Find phone in list
2. Click **"Remove"** button
3. Confirm removal
4. Phone removed from blacklist
5. Can send to this number again

### Impact
- ✅ When sending single SMS, blocked numbers skipped
- ✅ When sending campaign, blocked numbers excluded
- ✅ Activity log shows "Skipped (blacklisted)"
- ✅ Respects customer preferences

---

## 📊 Part 7: View Activity Log

### Navigate to Activity Log
1. From dashboard, click "View Activity"
2. Or go to: http://localhost:5000/admin/sms/activity
3. See complete audit trail

### Activity Log Shows
**For each SMS action:**
- **Action** - What happened (e.g., "SMS Sent")
- **Type** - Action category (e.g., "send")
- **Admin** - Who did it
- **Status** - Success/failure
- **Time** - When it happened
- **IP Address** - Where from
- **Browser** - What browser used
- **Message** - Details

### Filter Activity
- Filter by action type
- Filter by date range
- Filter by admin user
- Search for specific message

### Use Cases
- Verify who sent what
- Audit trail for compliance
- Troubleshoot issues
- Track all SMS operations

---

## 🔍 Part 8: Monitor Messages

### Navigate to Messages
1. From dashboard, click "View Messages"
2. Or go to: http://localhost:5000/admin/sms/messages
3. See complete message history

### Message List Shows
**For each message:**
- **Recipient** - Phone number
- **Content** - Message text (truncated)
- **Status** - Sent/Delivered/Failed
- **Campaign** - Which campaign (if any)
- **Cost** - SMS credits used
- **Time** - When sent
- **View** - Details link

### Message Details
Click on message to see:
- Full message content
- Recipient name & email
- mNotify status code
- Delivery confirmation time
- Error reason (if failed)
- Retry count
- Cost breakdown

### Filtering
- By recipient phone
- By status (sent/delivered/failed)
- By date range
- By cost
- By campaign

---

## 📈 Part 9: Check Statistics

### Dashboard Statistics
**Updated in real-time:**
- **Total Sent** - Cumulative SMS count
- **Delivered** - Confirmed successful
- **Failed** - Delivery errors
- **Pending** - In queue
- **Delivery Rate** - % successful

### Campaign Statistics
**Per campaign:**
- Recipients targeted
- Messages sent
- Messages delivered
- Messages failed
- Delivery rate
- Estimated cost

### Message Analytics
- Messages by category
- Success rate by template
- Average delivery time
- Cost per message
- Peak sending times

---

## 🔧 Part 10: Troubleshooting

### Issue: "No users in dropdown"
**Solution:**
1. Add test users to database first
2. Or click "View Users" to check
3. Must have at least 1 user
4. User must have valid phone number

### Issue: "Campaign shows 0 recipients"
**Solution:**
1. Check recipient filter
2. Try "All Users" filter
3. Verify users exist in database
4. Check user phone number format

### Issue: "SMS not sending"
**Solution:**
1. Check error in Activity Log
2. Verify phone number valid (Ghana format)
3. Verify phone not on blacklist
4. Check mNotify API key (if sending real SMS)
5. Check network connectivity

### Issue: "Character counter says 1 SMS but message is short"
**Solution:**
- This is normal!
- Unicode characters count differently
- Emoji = 1 char (counts as 1 Unicode SMS)
- Mix of emoji + text = Unicode mode (70 chars/SMS)

### Issue: "Previous campaign showed as duplicate"
**Solution:**
1. Go to Campaigns list
2. Check status (Sent vs Draft)
3. Click to view details
4. Verify before deleting

---

## 💡 Pro Tips

### Tip 1: Use Templates
- Save time with pre-made templates
- Ensure consistent messaging
- Easy to customize with variables

### Tip 2: Test First
- Send single SMS before bulk campaign
- Test with your own phone first
- Verify message looks correct

### Tip 3: Monitor Delivery
- Check Activity Log after sending
- Review failed messages
- Use Retry for failures

### Tip 4: Schedule Wisely
- Send during business hours (9am-6pm)
- Avoid late night sending
- Plan campaigns in advance

### Tip 5: Use Variables
- Personalize with {user_name}
- Add urgency with {promo_code}
- Include tracking with {tracking_url}

### Tip 6: Check Blacklist
- Before bulk sending, review blacklist
- Remove incorrect entries
- Add customers who unsubscribe

### Tip 7: Archive Old Campaigns
- Keep database clean
- Delete old campaigns after 6 months
- Export data for records

---

## ✅ Quick Checklist for First SMS

- [ ] Flask server running
- [ ] Logged in as admin
- [ ] Viewed SMS dashboard
- [ ] Verified 10 templates loaded
- [ ] Sent single SMS to test user
- [ ] Verified send in Activity Log
- [ ] Created test template
- [ ] Created test campaign
- [ ] Sent bulk campaign to small group
- [ ] Monitored in Activity Log
- [ ] Added phone to blacklist
- [ ] Tested blacklist exclusion
- [ ] Checked statistics update

---

## 🎯 Common Workflows

### Workflow 1: Daily Promotional SMS
1. Create template with promo details
2. Set campaign to "All Users"
3. Schedule for 10 AM daily
4. Monitor delivery rate
5. Use statistics to optimize

### Workflow 2: Order Confirmation SMS
1. Use "Order Confirmation" template
2. Automatically trigger on order
3. Include {order_id} in message
4. Monitor delivery in Activity Log

### Workflow 3: Verification Code SMS
1. Use "Verification Code" template
2. Include {code} parameter
3. Send during registration
4. Check Activity Log for delivery

### Workflow 4: Marketing Campaign
1. Create custom template with offer
2. Use "Flash Sale Alert" template
3. Target "Active Users" only
4. Schedule for specific time
5. Monitor engagement via delivery rate

---

## 📞 Need Help?

### Check Documentation
- README_SMS_SYSTEM.md - Overview
- SMS_QUICK_START.md - Quick reference
- SMS_IMPLEMENTATION_COMPLETE.md - Technical details
- CODE_SUMMARY.md - Implementation details

### Debug Issues
1. Check Activity Log for error messages
2. Verify user phone number format
3. Check blacklist for phone number
4. Review mNotify dashboard (if real SMS)
5. Check Flask console for Python errors

### Common Errors
- "Invalid phone format" - Use +233 or 0 prefix
- "User not found" - Create users first
- "API error" - Check mNotify API key
- "Campaign failed" - Check Activity Log for details

---

**You're ready to send SMS! Start with single messages, then try bulk campaigns. Monitor delivery rates and optimize based on statistics.**

Happy SMS sending! 📱✅
