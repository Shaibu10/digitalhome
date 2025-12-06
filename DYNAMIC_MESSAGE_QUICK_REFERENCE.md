# Dynamic Message System - Quick Reference for Admins

## Where to Access

**Admin Dashboard**: Navigate to `/admin/messages` in your browser

## Quick Tasks

### Create a New Message

1. Go to `/admin/messages` → Click **"Create First Message"** or **"Create Message"** button
2. Fill in message details:
   - **Title**: Short, catchy headline (max 200 characters)
   - **Content**: Your message text (supports HTML formatting)
   - **Type**: Choose from Info, Promotion, Warning, Alert, Success
   - **Location**: Homepage Only or All Pages
3. Configure appearance:
   - **Background Color**: Click color box to pick a color
   - **Text Color**: Click color box to pick a color
   - **Icon**: Enter Font Awesome icon name (e.g., `gift`, `star`, `check-circle`)
4. (Optional) Add a button:
   - **Button Text**: e.g., "Shop Now", "Learn More"
   - **Button URL**: e.g., `/products`, `/sale-page`
5. (Optional) Set schedule:
   - **Start Date**: When message should appear
   - **End Date**: When message should stop appearing
6. Live preview updates as you type
7. Click **"Create Message"** to save

### Edit a Message

1. Go to `/admin/messages`
2. Click **"Edit"** button on the message
3. Make your changes (same form as create)
4. Preview updates in real-time
5. Click **"Save Changes"**

### Delete a Message

1. Go to `/admin/messages`
2. Click **"Delete"** button on the message
3. Confirm deletion

### Temporarily Hide a Message

1. Go to `/admin/messages`
2. Click **"Toggle"** button to deactivate (or activate)
3. Message will immediately stop (or start) displaying

### View Message Statistics

1. Go to `/admin/messages`
2. Check the **Analytics** column for each message:
   - **Views**: How many people saw the message
   - **Clicks**: How many clicked the button

3. For detailed stats, click **"Edit"** to see:
   - Click-through rate (% of views that clicked)
   - Who created it and when
   - Who last edited it

### Filter Messages

Use the buttons at the top to filter by status:
- **All**: Show all messages
- **Active**: Currently displaying
- **Inactive**: Hidden messages
- **Scheduled**: Messages set for future display
- **Expired**: Messages past their end date

## Common Message Types & Colors

| Message Type | Use | Suggested Color |
|--------------|-----|-----------------|
| **Info** | General information | Blue (#007bff) |
| **Promotion** | Sales, offers, discounts | Green (#28a745) |
| **Warning** | Important reminders | Yellow (#ffc107) |
| **Alert** | Critical messages | Red (#dc3545) |
| **Success** | Confirmations, achievements | Green (#28a745) |

## Popular Icons

- `info-circle` - Information
- `gift` - Gifts, discounts
- `star` - Featured, special
- `check-circle` - Success, verified
- `exclamation-triangle` - Warning
- `alert` - Critical alert
- `shopping-bag` - Shopping, sale
- `tag` - Discount, sale
- `truck` - Shipping
- `bolt` - Limited time
- `calendar` - Events, dates

*Find more at: [Font Awesome Icons](https://fontawesome.com/search)*

## Example Messages

### Summer Sale Banner
```
Title: Summer Sale 2025
Content: Get up to 40% off all items this summer!
Type: Promotion
Location: Homepage Only
Colors: Green background, white text
Icon: gift
Button: "Shop Sale" → /sale
Schedule: June 1 - August 31
```

### New Feature Alert
```
Title: New Payment Method
Content: We now accept Orange Money payments online!
Type: Success
Location: Homepage Only
Colors: Blue background, white text
Icon: credit-card
Button: "Learn More" → /help/payment
```

### Maintenance Warning
```
Title: Scheduled Maintenance
Content: Site maintenance tonight 11 PM - 2 AM. Service will be unavailable.
Type: Alert
Location: All Pages
Colors: Yellow background, dark text
Icon: wrench
No Button
Schedule: Tonight 11:00 PM - 2:00 AM
```

### Flash Sale (Limited Time)
```
Title: Flash Sale - 24 Hours Only!
Content: Limited stock available. <strong>Today only!</strong>
Type: Warning
Location: Homepage Only
Colors: Red background, white text
Icon: bolt
Button: "Grab Yours" → /flash-sale
Schedule: Today only
```

## Tips & Best Practices

### Content Tips
- **Keep titles short** (under 50 characters) for mobile devices
- **Use bold or italics** in content for emphasis: `<strong>text</strong>`
- **Always provide context** - say what the message is about
- **Test on mobile** - preview how it looks on phones

### Design Tips
- **High contrast** - Make sure text is readable on background color
- **One message at a time** - Limit to 1-2 active messages
- **Order matters** - Messages with lower order numbers appear first
- **Seasonal colors** - Use colors relevant to your message

### Timing Tips
- **Schedule ahead** - Create messages days in advance
- **Test before going live** - Try scheduling for 1 minute from now first
- **Monitor CTR** - Check click-through rate to measure effectiveness
- **Rotate messages** - Change messages weekly to keep content fresh

### Button Tips
- **Keep button text short** - 2-3 words max
- **Use action words** - "Shop Now", "Learn More", "Explore"
- **Ensure URLs work** - Test that button links go to correct page
- **Link to related content** - Button should match message context

## Keyboard Shortcuts

- **Tab** - Move between form fields
- **Shift+Tab** - Move back to previous field
- **Enter** - Submit form (if focused on button)

## Common Issues

### Message Not Showing
- ✅ Check if it's **Active** (toggle on if needed)
- ✅ Check if current date is within **Start/End dates**
- ✅ Check if location includes **Homepage**
- ✅ Try **refreshing your browser**

### Text Color Not Readable
- ✅ Increase **contrast** between background and text colors
- ✅ Example: Light text on dark background or vice versa
- ✅ Use online tool to check: [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### Button Not Showing
- ✅ Make sure both **Button Text** AND **Button URL** are filled in
- ✅ Leave BOTH blank if you don't want a button

### Analytics Showing 0
- ✅ Views are tracked when users see the message
- ✅ Clicks are tracked when users click the button
- ✅ May take a few hours to accumulate data

## Admin Dashboard Quick Stats

Look at the top of `/admin/messages` for quick statistics:
- **Total Messages**: All messages in system
- **Active Now**: Currently displaying
- **Total Views**: All-time impressions
- **Total Clicks**: All-time button clicks

## Help & Support

For technical issues:
1. Check the [DYNAMIC_MESSAGE_SYSTEM.md](./DYNAMIC_MESSAGE_SYSTEM.md) documentation
2. Review the test results: `python test_dynamic_messages.py`
3. Check Flask application logs for errors

## Checklists

### Before Publishing a Message
- [ ] Title is clear and under 50 characters
- [ ] Content is proofread and error-free
- [ ] Message type matches your content
- [ ] Colors have good contrast and are readable
- [ ] If including a button, both text and URL are filled in
- [ ] Button URL works and goes to correct page
- [ ] Schedule dates are correct (if using scheduling)
- [ ] Location is set correctly (Homepage vs All Pages)
- [ ] Icon is chosen and relevant to content
- [ ] Tested on mobile browser

### Weekly Maintenance
- [ ] Check analytics for low-performing messages
- [ ] Archive or update expired messages
- [ ] Plan and schedule messages for next week
- [ ] Rotate content to keep site fresh
- [ ] Monitor click-through rates

---

**Last Updated**: 2025
**System Version**: 1.0
**Admin Interface**: `/admin/messages`
