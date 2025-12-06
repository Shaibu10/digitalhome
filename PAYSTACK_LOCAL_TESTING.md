# Paystack Integration - Local Testing Guide

## ✅ Implementation Complete!

All Paystack integration code has been implemented. Time to test!

---

## 🧪 Testing Overview

### What We're Testing
1. Order creation with different payment methods
2. Paystack payment initialization
3. Payment record creation in database
4. Payment verification flow
5. Order confirmation page

### Test Environment
- **App URL:** http://localhost:5000
- **Environment:** Sandbox (Test Mode)
- **Paystack Keys:** Using test credentials from .env
- **Database:** SQLite (digitalhome.db)

---

## 🚀 Test Steps

### Test 1: User Registration & Login (5 min)
1. Go to http://localhost:5000
2. Create a new account or login
3. **Verify:** User can access checkout page

### Test 2: Add Products to Cart (5 min)
1. Browse products
2. Add 2-3 items to cart
3. Go to cart page
4. **Verify:** Cart displays items and totals

### Test 3: Cash on Delivery Payment (10 min)
1. Go to checkout
2. Fill in shipping info:
   - First Name: John
   - Last Name: Test
   - Phone: +233241234567
   - Address: 123 Main St
   - City: Accra
   - Postal Code: 00233
3. Select "Cash on Delivery" payment
4. Select shipping method
5. Click "Place Order"
6. **Expected:** Redirected to order confirmation page
7. **Check Database:**
   ```bash
   sqlite3 digitalhome.db
   SELECT * FROM payment;  # Should be EMPTY (no payment record for COD)
   SELECT id, order_number, payment_status FROM "order" WHERE payment_method='cod';
   ```

### Test 4: Manual Payment Method (10 min)
1. Add items to cart again
2. Go to checkout
3. Fill in shipping info
4. Select "Bank Transfer (Manual)" or "Mobile Money (Manual)"
5. Click "Place Order"
6. **Expected:** Order confirmation page
7. **Check Database:**
   ```bash
   sqlite3 digitalhome.db
   SELECT id, order_number, payment_status FROM "order" WHERE payment_method='bank_transfer';
   ```

### Test 5: Paystack Payment - Initialization (15 min)
1. Add items to cart
2. Go to checkout
3. Fill in shipping info completely
4. **Select "Pay with Card/Mobile Money (Secure)"**
5. Click "Place Order"
6. **Expected:** 
   - Loading message appears
   - Paystack checkout popup opens
   - Can see payment options (Card, Mobile Money, etc.)
7. **Check Database (Order Created):**
   ```bash
   sqlite3 digitalhome.db
   SELECT id, order_number, payment_status FROM "order" WHERE payment_method='paystack';
   ```
8. **Check Database (Payment Record Created):**
   ```bash
   sqlite3 digitalhome.db
   SELECT id, paystack_reference, amount, status FROM payment;
   SELECT * FROM payment_log;
   ```

### Test 6: Paystack Payment - Success Flow (15 min)
1. When Paystack popup appears, enter test card details:
   - **Card Number:** 4084 0840 8408 4081
   - **Expiry:** 01/25 (or any future date)
   - **CVV:** 408
   - **OTP:** 123456
2. Click "Charge"
3. **Expected:**
   - Payment processes
   - Redirected to `/payment-confirmed/<reference>`
   - Confirmation page shows "Payment Successful!"
   - Shows payment details and order info
4. **Check Database (Payment Updated):**
   ```bash
   sqlite3 digitalhome.db
   SELECT id, status, completed_at FROM payment WHERE status='success';
   ```
5. **Check Order Status (Should be updated):**
   ```bash
   sqlite3 digitalhome.db
   SELECT order_number, payment_status, status FROM "order" WHERE payment_status='paid';
   ```

### Test 7: Paystack Payment - Failed Flow (10 min)
1. Add items to cart again
2. Go to checkout
3. Select "Pay with Card/Mobile Money (Secure)"
4. When Paystack popup appears, enter failed test card:
   - **Card Number:** 4111 1111 1111 1111
   - **Expiry:** 01/25
   - **CVV:** 111
5. **Expected:**
   - Payment fails
   - Error message displayed
   - Can retry payment
6. **Check Database (Payment Record with Failed Status):**
   ```bash
   sqlite3 digitalhome.db
   SELECT id, status, status_reason FROM payment WHERE status='failed';
   ```

### Test 8: Payment History (10 min)
1. Go to `/payment/payment-history`
2. **Expected:**
   - Shows all user's payments
   - Displays status (Success, Failed, Pending)
   - Shows payment method
   - Shows amount and date
3. Click on a payment to see details
4. **Verify:** Modal shows payment information

---

## 📊 Database Verification Commands

### Check All Tables
```bash
sqlite3 digitalhome.db
.tables
```

### Check Payment Records
```sql
-- All payments
SELECT id, paystack_reference, amount, status, initiated_at, completed_at FROM payment;

-- Successful payments
SELECT * FROM payment WHERE status='success';

-- Failed payments
SELECT * FROM payment WHERE status='failed';

-- Pending payments
SELECT * FROM payment WHERE status='pending';
```

### Check Payment Log (Audit Trail)
```sql
-- All payment events
SELECT p.id, p.paystack_reference, p.status, pl.action, pl.details, pl.timestamp 
FROM payment p 
LEFT JOIN payment_log pl ON p.id = pl.payment_id 
ORDER BY p.id DESC;
```

### Check Order Status
```sql
-- Orders with payment info
SELECT id, order_number, payment_method, payment_status, status, created_at 
FROM "order" 
ORDER BY id DESC 
LIMIT 10;

-- Orders by payment method
SELECT payment_method, COUNT(*) as count, SUM(total_amount) as total 
FROM "order" 
GROUP BY payment_method;

-- Paid orders
SELECT id, order_number, total_amount FROM "order" WHERE payment_status='paid';
```

---

## 🔍 What to Look For

### ✅ Success Indicators
- [ ] Order created with correct order_number
- [ ] Payment record created with unique paystack_reference
- [ ] Payment status transitions from 'pending' → 'success'
- [ ] Order payment_status changes from 'unpaid' → 'paid'
- [ ] Payment history page shows all payments
- [ ] Payment confirmation page displays correctly
- [ ] Audit trail in payment_log has all events
- [ ] No database errors in logs

### 🐛 Potential Issues to Watch For
- [ ] Paystack popup doesn't open → Check PAYSTACK_PUBLIC_KEY in .env
- [ ] Payment not created → Check Payment model and routes.py
- [ ] Status not updating → Check verification endpoint
- [ ] Database locked → Close other connections
- [ ] CORS errors → Check Flask configuration
- [ ] JavaScript errors → Check browser console

---

## 📝 Test Checklist

### Phase 1: Basic Flow
- [ ] Cash on Delivery order created
- [ ] Manual payment order created
- [ ] Payment history page loads
- [ ] Database has test records

### Phase 2: Paystack Payment
- [ ] Paystack popup opens successfully
- [ ] Test card accepted
- [ ] Payment marked as success
- [ ] Confirmation page displays

### Phase 3: Error Handling
- [ ] Failed test card handled
- [ ] Error messages display
- [ ] Retry functionality works

### Phase 4: Data Integrity
- [ ] Payment records correct in database
- [ ] Order status updated correctly
- [ ] Audit trail complete
- [ ] Payment history accurate

---

## 🚨 Troubleshooting

### Problem: "ReferenceError: PAYSTACK_PUBLIC_KEY is not defined"
**Solution:**
1. Check `.env` has PAYSTACK_PUBLIC_KEY
2. Verify key starts with `pk_test_` or `pk_live_`
3. Restart Flask app
4. Check browser console

### Problem: Paystack.js not loading
**Solution:**
1. Check script tag in checkout.html
2. Verify URL: `https://js.paystack.co/v1/inline.js`
3. Check network tab in browser DevTools
4. Ensure HTTPS for external scripts

### Problem: "Payment record not found" error
**Solution:**
1. Check if Payment table created: `SELECT COUNT(*) FROM payment;`
2. Run `python create_tables_direct.py` if needed
3. Verify order_id foreign key exists

### Problem: "ModuleNotFoundError: No module named 'payments.routes'"
**Solution:**
1. Verify `payments/routes.py` exists
2. Verify `payments/__init__.py` exists
3. Restart Flask app

### Problem: Database locked errors
**Solution:**
1. Close all database connections
2. Stop Flask app
3. Ensure no browser is holding connection
4. Restart Flask app

---

## 📊 Success Metrics

After testing, you should have:

**In Database:**
- ✅ Multiple order records
- ✅ Payment records for Paystack orders
- ✅ PaymentLog entries for each payment action
- ✅ Correct payment_status in orders
- ✅ Unique paystack_reference for each payment

**In Browser:**
- ✅ Checkout page loads
- ✅ Payment method options visible
- ✅ Paystack popup opens and functions
- ✅ Payment confirmation page displays
- ✅ Payment history page shows all payments

**In Logs:**
- ✅ No JavaScript errors
- ✅ No Python exceptions
- ✅ Paystack API calls logged
- ✅ Payment verification successful

---

## 🎯 Next Steps After Testing

1. **If Local Tests Pass:**
   - Commit code to git
   - Document any custom modifications
   - Prepare for production deployment

2. **If Issues Found:**
   - Check logs for errors
   - Review database state
   - Compare with documentation
   - Debug specific endpoint

3. **Before Production:**
   - Get live Paystack credentials
   - Update .env with live keys
   - Re-run tests with live keys
   - Setup monitoring/alerts

---

## 📱 Test Paystack Cards

### Successful Payments
| Card | Number | Exp | CVV | OTP |
|------|--------|-----|-----|-----|
| Visa | 4084 0840 8408 4081 | 01/25 | 408 | 123456 |

### Failed Payments
| Card | Number | Exp | CVV |
|------|--------|-----|-----|
| Visa | 4111 1111 1111 1111 | 01/25 | 111 |

### Additional Test Scenarios
- Use any future expiry date
- Use any 3-4 digit CVV for successful card
- OTP is always 123456 when prompted

---

## 💾 Database Export (For Records)

```bash
# Export all orders
sqlite3 digitalhome.db "SELECT * FROM \"order\";" > orders_export.csv

# Export all payments
sqlite3 digitalhome.db "SELECT * FROM payment;" > payments_export.csv

# Export payment logs
sqlite3 digitalhome.db "SELECT * FROM payment_log;" > payment_logs_export.csv
```

---

## 🎓 Key Files for Reference

| File | Purpose | Location |
|------|---------|----------|
| checkout.html | UI & JavaScript | templates/ |
| app.py (checkout route) | Paystack handling | app.py:830-900 |
| paystack_gateway.py | API wrapper | payments/ |
| routes.py | Payment endpoints | payments/ |
| models.py | Payment models | models.py |
| config.py | Paystack config | config.py |
| .env | Credentials | . |

---

## 🔐 Security Notes

- ✅ Secret key not exposed in frontend
- ✅ Signature verification on webhooks
- ✅ User ownership verified on all routes
- ✅ Payment amounts verified with API
- ✅ Test mode uses sandbox credentials

---

**Ready to Test!**

Start with Test 1 and work your way through. Document any issues and refer to troubleshooting section.

*Estimated Total Testing Time: 1.5-2 hours*

---

*Generated: November 2024*
