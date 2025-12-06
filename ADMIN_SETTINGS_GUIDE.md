# Admin Settings Quick Reference

## Accessing Admin Settings

1. **Login as Admin**
   - Navigate to `/auth/login`
   - Enter admin credentials
   - Click "Admin Dashboard"

2. **Access Settings**
   - Click "System Settings" in the left sidebar (gear icon)
   - Or visit: `/admin/settings`

## Managing Shipping Costs

### Shipping Settings Tab

1. **Standard Shipping Cost**
   - Default: GH₵ 10.00
   - Delivery: 3-5 days
   - Enter amount in GH₵
   - Update shows in checkout immediately

2. **Express Shipping Cost**
   - Default: GH₵ 15.00
   - Delivery: 1-2 days
   - Enter amount in GH₵
   - Premium option for faster delivery

3. **Free Shipping Threshold**
   - Default: GH₵ 100.00
   - Orders at or above this amount get free shipping
   - Free option delivery: 5-7 days
   - Set to high value (e.g., 9999) to disable free shipping

### How It Works

**Example Scenario:**
- Threshold: GH₵ 100
- Customer cart: GH₵ 95
  - ✗ Free shipping not available (below threshold)
  - Options: Standard (GH₵ 10) or Express (GH₵ 15)

- Customer cart: GH₵ 105
  - ✓ Free shipping available (above threshold)
  - Options: Free (5-7 days), Standard, or Express

## Managing Tax Rate

### Tax Settings Tab

1. **Tax Rate Input**
   - Enter as percentage (0-100)
   - Default: 5%
   - Applied to all orders

2. **Live Preview**
   - Shows example calculation
   - For GH₵ 100 order:
     - At 5%: Tax = GH₵ 5.00, Total = GH₵ 105.00
     - At 10%: Tax = GH₵ 10.00, Total = GH₵ 110.00

3. **Common Rates**
   - 0% = No tax
   - 5% = Standard VAT
   - 10% = Higher VAT
   - 15% = Premium tax

## Real-Time Impact

### Checkout Page Updates

When admin saves new settings:

**Before:**
- Shipping: GH₵ 10.00 (standard)
- Tax: 5%
- Total: GH₵ 105.00

**After admin changes to:**
- Shipping: GH₵ 12.00 (standard)
- Tax: 7%
- Total: GH₵ 117.00

**Next customer checkout shows new prices immediately!**

## Audit Trail

Each settings page shows:
- **Last Updated:** Date and time of last change
- **By:** Username of admin who made change
- Allows tracking of who changed what and when

## Common Tasks

### Task 1: Run a Promotion
Increase free shipping threshold to make free shipping available for lower orders

**Steps:**
1. Go to Shipping Settings
2. Change "Free Shipping Threshold" from GH₵ 100 → GH₵ 50
3. Click "Save Shipping Settings"
4. Customers now get free shipping on orders ≥ GH₵ 50

### Task 2: Increase Revenue per Order
Add express shipping option and increase tax rate

**Steps:**
1. Go to Shipping Settings
2. Change "Express Shipping Cost" from GH₵ 15 → GH₵ 20
3. Go to Tax Settings
4. Change tax rate from 5% → 7%
5. Save both settings
6. Orders now have higher margins

### Task 3: Seasonal Adjustment
Reduce shipping to compete during holiday season

**Steps:**
1. Go to Shipping Settings
2. Change "Standard Shipping Cost" from GH₵ 10 → GH₵ 5
3. Change "Express Shipping Cost" from GH₵ 15 → GH₵ 8
4. Click "Save Shipping Settings"
5. Prices are competitive for holiday shopping

### Task 4: Check Settings History
See what's been changed recently

**Steps:**
1. Go to System Settings page
2. Look at "Last Updated" information at bottom of each section
3. See admin who made changes
4. Each change is logged in Activity Logs

## REST API (For Future Development)

Settings can be programmatically accessed (future feature):

```python
# Get current settings
settings = SystemSettings.get_settings()
print(settings.tax_rate)  # 0.05
print(settings.standard_shipping_cost)  # 10.00

# Update settings (only in admin route currently)
settings.update_shipping_settings(12, 18, 120, admin_user_id)
settings.update_tax_settings(0.07, admin_user_id)
```

## Troubleshooting

### Problem: Changes not showing in checkout
**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Try a new incognito/private window
3. Verify changes were saved (look for success message)

### Problem: Cannot access settings page
**Solution:**
1. Verify you're logged in as admin
2. Check that your user account has is_admin=True
3. Use admin account, not regular user account

### Problem: Negative or invalid values
**Solution:**
1. All costs must be positive numbers
2. Tax rate must be 0-100
3. System shows error message on invalid input
4. Correct the value and try again

## Data Backup

Before making large changes:
1. Take screenshot of current settings
2. Make note of values in Activity Logs
3. Can always be changed back if needed

## Support

For issues or questions:
1. Check Activity Logs to see change history
2. Review this quick reference guide
3. Contact system administrator
4. Check DYNAMIC_SETTINGS_IMPLEMENTATION.md for technical details
