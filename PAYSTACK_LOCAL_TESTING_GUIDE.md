# 🧪 PAYSTACK INTEGRATION - LOCAL TESTING GUIDE

## ✅ Integration Status: READY FOR TESTING

All components verified and functional. Use this guide to test the complete payment flow locally.

---

## Prerequisite: Start Flask Server

Open a new terminal and run:

```bash
python run.py
```

The server should start at `http://127.0.0.1:5000`

**Expected Output:**
```
 🚀 DigitalHome E-Commerce Platform - Development Server
 📍 Server running at: http://localhost:5000
 🔑 Admin login: admin@example.com / admin123
```

---

## TEST SCENARIO 1: User Registration & Login

**Objective:** Verify user authentication works before payment

**Steps:**
1. Navigate to `http://127.0.0.1:5000/auth/register`
2. Create test account:
   - Email: `testuser@digitalhome.test`
   - Password: `testpass123`
3. Click Register
4. Navigate to `http://127.0.0.1:5000/auth/login`
5. Log in with credentials above

**Expected Results:**
- ✓ Registration successful
- ✓ Login successful
- ✓ Redirected to homepage or products page
- ✓ User session created

**Database Check:**
```sql
SELECT * FROM user WHERE email = 'testuser@digitalhome.test';
```

---

## TEST SCENARIO 2: Add Products to Cart

**Objective:** Build a cart for payment testing

**Steps:**
1. Navigate to `http://127.0.0.1:5000/products`
2. Click on any product
3. Enter quantity: `1`
4. Click "Add to Cart"
5. Repeat for 2-3 products

**Expected Results:**
- ✓ Products added to cart
- ✓ Cart count updates in header
- ✓ Can navigate to different products
- ✓ No errors in console

**Database Check:**
```sql
SELECT * FROM cart_item WHERE user_id = <USER_ID>;
```

---

## TEST SCENARIO 3: Proceed to Checkout

**Objective:** Verify checkout page loads with correct payment options

**Steps:**
1. Click "Checkout" or navigate to `http://127.0.0.1:5000/checkout`
2. Verify page displays:
   - ✓ Cart items summary
   - ✓ Shipping address form
   - ✓ Payment method options:
     - Cash on Delivery (COD)
     - Paystack (PRIMARY - should be selected)
     - Manual Payment Methods (Bank Transfer, Mobile Money)

**Expected Results:**
- ✓ Checkout page loads without errors
- ✓ Cart items display correctly
- ✓ Paystack option appears and is selected by default
- ✓ Form validation works

**Browser Console Check:**
- Press `F12` to open Developer Tools
- Check Console tab for any errors
- Expected: No errors, only info messages

---

## TEST SCENARIO 4: Test Paystack Payment (Success Case)

**Objective:** Verify successful payment flow with test card

**Steps:**
1. On checkout page, confirm:
   - Paystack payment method is selected
   - Shipping details filled
2. Click "Complete Payment"
3. Paystack popup should appear with payment form
4. Use test card: **4084 0840 8408 4081**
   - Expiry: Any future date (e.g., 12/25)
   - CVV: Any 3 digits (e.g., 123)
5. Click "Pay"
6. After popup closes, you should be redirected to payment confirmation

**Expected Results:**
- ✓ Paystack popup opens
- ✓ Payment form accepts test card
- ✓ Popup closes after payment
- ✓ Redirected to `/payment-confirmed/<reference>`
- ✓ Confirmation page shows: "Payment Successful"

**Database Check - Payment Created:**
```sql
SELECT * FROM payment ORDER BY id DESC LIMIT 1;
```

Expected columns populated:
- `order_id`: Order number
- `customer_email`: User email
- `amount`: 100.00 (or cart total)
- `currency`: GHS
- `paystack_reference`: Unique reference
- `payment_method`: card
- `status`: pending (or success if webhook confirmed)
- `initiated_at`: Current timestamp

**Database Check - PaymentLog Created:**
```sql
SELECT * FROM payment_log ORDER BY id DESC LIMIT 1;
```

Expected:
- `action`: initiated
- `details`: Payment initiated message
- `timestamp`: Current timestamp

**Database Check - Order Updated:**
```sql
SELECT * FROM order ORDER BY id DESC LIMIT 1;
```

Expected:
- `payment_status`: pending (or paid if webhook confirmed)

---

## TEST SCENARIO 5: Test Paystack Payment (Failure Case)

**Objective:** Verify failed payment handling

**Steps:**
1. Repeat checkout process
2. Use failure test card: **4111 1111 1111 1111**
   - Expiry: Any future date
   - CVV: Any 3 digits
3. Complete payment flow
4. Should see failure message

**Expected Results:**
- ✓ Payment popup opens
- ✓ Test card is rejected
- ✓ Redirected to payment failure page or error message
- ✓ Order remains unpaid

**Database Check - Payment Failed:**
```sql
SELECT status, status_reason FROM payment 
WHERE paystack_reference LIKE '%failed%' 
ORDER BY id DESC LIMIT 1;
```

Expected:
- `status`: failed
- `status_reason`: Failure reason from Paystack

---

## TEST SCENARIO 6: Payment History Page

**Objective:** Verify user can view their payment history

**Steps:**
1. After successful payment, navigate to `http://127.0.0.1:5000/payment/payment-history`
2. Verify page displays:
   - List of all payments
   - Payment reference
   - Amount
   - Status
   - Date
   - "View" and "Details" buttons

**Expected Results:**
- ✓ Payment history page loads
- ✓ Recent payment appears in list
- ✓ All fields display correctly
- ✓ Can click "Details" button
- ✓ Details modal shows payment information

**Database Check:**
```sql
SELECT * FROM payment WHERE customer_email = 'testuser@digitalhome.test';
```

---

## TEST SCENARIO 7: Webhook Verification

**Objective:** Verify webhook endpoint works (simulated locally)

**Steps:**
1. In a new terminal, send simulated webhook:

```bash
$payload = @{
    event = 'charge.success'
    data = @{
        reference = '<PAYMENT_REFERENCE>'
        status = 'success'
        amount = 100000
        authorization = @{
            authorization_code = 'AUTH_CODE123'
            card = @{
                type = 'visa'
                last4 = '4081'
            }
        }
    }
} | ConvertTo-Json

$hmacSecret = $env:PAYSTACK_SECRET_KEY
$hmac = [System.Security.Cryptography.HMACSHA512]::new([System.Text.Encoding]::UTF8.GetBytes($hmacSecret))
$hash = $hmac.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($payload))
$signature = [System.Convert]::ToBase64String($hash)

Invoke-WebRequest -Uri "http://127.0.0.1:5000/payment/webhook" `
    -Method POST `
    -Body $payload `
    -ContentType "application/json" `
    -Headers @{ "x-paystack-signature" = $signature }
```

**Expected Results:**
- ✓ Webhook accepted (HTTP 200)
- ✓ Payment status updated to 'success'
- ✓ Order payment_status updated to 'paid'
- ✓ PaymentLog entry created with 'webhook_confirmed'

---

## TEST SCENARIO 8: Mobile Money Payment (If Supported)

**Objective:** Verify mobile money payment method selection

**Steps:**
1. Return to checkout
2. Note that while Paystack popup appears, the selected payment method in database would be based on what user selected in Paystack popup
3. Complete a payment
4. Check database for payment_method field

**Expected Results:**
- ✓ Payment processes through Paystack
- ✓ Payment method recorded in database
- ✓ Could be 'card', 'mobile_money', 'bank_transfer', or 'ussd'

---

## Troubleshooting

### Issue: Paystack popup doesn't appear

**Check:**
1. Browser console for JavaScript errors
2. Verify Paystack SDK loaded: `https://js.paystack.co/v1/inline.js`
3. Verify `PAYSTACK_PUBLIC_KEY` in .env starts with `pk_test_`

**Solution:**
- Clear browser cache
- Check .env file has correct credentials
- Restart Flask server

### Issue: Payment created but not marked as success

**Check:**
1. Webhook might not be firing from Paystack in test environment
2. `payment.status` is still 'pending' instead of 'success'

**Solution:**
- Manually update payment status in database:
```sql
UPDATE payment SET status = 'success', completed_at = datetime('now')
WHERE status = 'pending'
LIMIT 1;
```

### Issue: 404 errors on routes

**Check:**
1. Flask server is running: `http://127.0.0.1:5000/`
2. Routes registered in Flask: Check terminal output for "Running on"

**Solution:**
- Kill Flask server (Ctrl+C)
- Restart: `python run.py`
- Wait 5 seconds for full startup

### Issue: Database errors

**Check:**
- Database file exists: `instance/digitalhome.db`
- Database is not locked by another process

**Solution:**
```bash
# Reinitialize database
python init_database.py
```

---

## Database Verification Commands

### Check all payments
```sql
SELECT id, paystack_reference, amount, status, initiated_at FROM payment;
```

### Check specific payment with logs
```sql
SELECT p.id, p.paystack_reference, p.status, p.amount,
       pl.action, pl.details, pl.timestamp
FROM payment p
LEFT JOIN payment_log pl ON p.id = pl.payment_id
ORDER BY p.id DESC, pl.timestamp DESC;
```

### Check order payment status
```sql
SELECT id, order_number, payment_status, total_amount FROM order;
```

### Check user with payments
```sql
SELECT u.id, u.email, u.username,
       COUNT(p.id) as payment_count,
       SUM(p.amount) as total_paid
FROM user u
LEFT JOIN payment p ON u.id = (
    SELECT user_id FROM order WHERE id = p.order_id
)
GROUP BY u.id;
```

---

## Test Results Template

After running all tests, record results:

```
TEST RESULTS - Paystack Integration Local Testing
Date: _______________
Tester: _______________

✓/✗ TEST 1: User Registration & Login
✓/✗ TEST 2: Add Products to Cart
✓/✗ TEST 3: Proceed to Checkout
✓/✗ TEST 4: Successful Payment
✓/✗ TEST 5: Failed Payment
✓/✗ TEST 6: Payment History
✓/✗ TEST 7: Webhook Verification
✓/✗ TEST 8: Mobile Money (If applicable)

Issues Found:
- [Issue 1]
- [Issue 2]

Notes:
- [Note 1]
- [Note 2]

Recommendation: ✓ Ready for Staging / ✗ Additional Testing Needed
```

---

## Next Steps

Once all local tests pass:

1. **Staging Environment Testing**
   - Deploy to staging server
   - Test with real Paystack test environment credentials
   - Test with team members

2. **Production Preparation**
   - Obtain production Paystack credentials
   - Configure production database
   - Set up email notifications
   - Configure webhook endpoints

3. **Go Live**
   - Switch to production Paystack keys
   - Enable email notifications
   - Monitor webhook logs
   - Document payment processes for support team

---

## Contact & Support

For Paystack integration issues:
- Paystack Dashboard: https://dashboard.paystack.co
- Paystack API Docs: https://paystack.com/docs/api
- Test Environment: Always use `pk_test_*` and `sk_test_*` keys during development

