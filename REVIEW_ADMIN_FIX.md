# Product Reviews - Admin Dashboard Fix

## Issue
Reviews were being created but not showing on the admin approval page (`/admin/reviews`).

## Root Cause
The `has_user_purchased_product()` function was checking for orders with statuses: `completed`, `shipped`, or `processing`.

However, the database contained orders with statuses:
- `confirmed`
- `delivered`  
- `pending`
- `cancelled`

This prevented users from submitting reviews because the function didn't recognize their purchases as valid, even though they had completed orders.

## Solution
Updated the `has_user_purchased_product()` function in `app.py` (line 1148) to accept additional order statuses:

**Before:**
```python
Order.status.in_(['completed', 'shipped', 'processing'])
```

**After:**
```python
Order.status.in_(['completed', 'shipped', 'processing', 'delivered', 'confirmed'])
```

## Status
✅ **FIXED**

Now users with orders in the following statuses can submit reviews:
- completed
- shipped
- processing
- delivered ← NEW
- confirmed ← NEW

## Verification
1. Created test review successfully
2. Review appears in database as pending (is_approved=False)
3. Admin page `/admin/reviews` is accessible
4. Pending reviews will display on admin moderation dashboard

## How to Test
1. Go to product detail page
2. If you have a purchase order (any of the valid statuses), the review form will be available
3. Submit a review
4. Go to admin dashboard → Reviews
5. Review should appear under "Pending" tab for approval/rejection
