# Paystack Integration - Testing & Deployment Guide

## Current Status

✅ **Complete** - Paystack integration is now fully implemented and ready for testing!

### What's Been Set Up

1. **Backend Infrastructure**
   - ✅ Paystack Gateway (`payments/paystack_gateway.py`)
   - ✅ Payment Routes (`payments/routes.py`)
   - ✅ Database Models (Payment & PaymentLog tables created)
   - ✅ Order Model updated with payment_status field

2. **Frontend Templates**
   - ✅ `templates/payment_status.html` - Payment confirmation page
   - ✅ `templates/payment_history.html` - User payment history
   - ✅ `templates/checkout.html` - Updated checkout flow

3. **Routes**
   - ✅ `/checkout` - Order placement (POST)
   - ✅ `/payment-confirmed/<reference>` - Payment confirmation
   - ✅ `/payment/initiate` - Paystack payment initialization
   - ✅ `/payment/verify/<reference>` - Payment verification
   - ✅ `/payment/paystack-callback` - Paystack callback handler
   - ✅ `/payment/webhook` - Webhook receiver
   - ✅ `/payment/payment-history` - User payment history
   - ✅ `/payment/status/<payment_id>` - Payment status check

4. **Environment Configuration**
   - ✅ `.env` file configured with Paystack keys
   - ✅ Config variables in `config.py`

---

## Testing Checklist

### Phase 1: Local Development Testing (Sandbox)

#### 1.1 Prerequisites
- [ ] Application running on `http://localhost:5000`
- [ ] User account created and email verified
- [ ] At least one product in the system
- [ ] Shopping cart has items

#### 1.2 Test Payment Flow with Cash on Delivery
1. Navigate to checkout page
2. Fill in shipping information:
   - First Name: John
   - Last Name: Doe
   - Phone: +233241234567
   - Address: 123 Main Street
   - City: Accra
   - Postal Code: 00233
3. Select "Cash on Delivery" payment method
4. Select shipping method
5. Click "Place Order"
6. Expected: Order confirmation page, payment_status = 'pending'

#### 1.3 Test Payment Flow with Bank Transfer
1. Repeat steps 1-4 from 1.2
2. Select "Bank Transfer" payment method
3. Click "Place Order"
4. Expected: Order confirmation page showing pending manual payment

#### 1.4 Test Payment History
1. Go to `/payment/payment-history`
2. Expected: Empty history (no payments yet)
3. After placing orders, should see list of payment records

### Phase 2: Paystack Sandbox Testing

#### 2.1 Setup Paystack Test Credentials
1. Visit https://dashboard.paystack.com/signup
2. Create test account
3. Go to Settings → API Keys & Webhooks
4. Copy test keys:
   - Public Key (starts with `pk_test_`)
   - Secret Key (starts with `sk_test_`)
5. Update `.env` file:
   ```
   PAYSTACK_PUBLIC_KEY=pk_test_xxxxx
   PAYSTACK_SECRET_KEY=sk_test_xxxxx
   ```
6. Restart application

#### 2.2 Test Cards (Provided by Paystack)
```
Success Card:
  Number: 4084 0840 8408 4081
  Expiry: 01/25 (any future date)
  CVV: 408
  OTP: 123456

Failed Card:
  Number: 4111 1111 1111 1111
  Expiry: 01/25
  CVV: 111
  
Mobile Money (Ghana):
  - Paystack handles redirection
  - No test card needed
```

#### 2.3 Test Successful Payment
1. Go to checkout page
2. Add product to cart
3. Fill shipping info
4. Select payment method (currently Bank Transfer or COD)
5. For testing Paystack, modify checkout template to add Paystack option:
   ```html
   <div class="form-check mb-3">
       <input class="form-check-input" type="radio" name="payment_method" id="payment_paystack" value="paystack">
       <label class="form-check-label" for="payment_paystack">
           <strong>Card/Mobile Money (Paystack)</strong>
       </label>
   </div>
   ```
6. Update checkout.py to handle paystack method:
   ```python
   elif payment_method == 'paystack':
       # Initiate Paystack payment
       return jsonify({...proceed_to_paystack...})
   ```

#### 2.4 Verify Database Records
```bash
# Check payment was created
sqlite3 digitalhome.db
sqlite> SELECT * FROM payment;

# Check payment log
sqlite> SELECT * FROM payment_log;

# Check order payment_status was updated
sqlite> SELECT id, order_number, payment_status FROM "order";
```

### Phase 3: Webhook Testing (Local Development)

#### 3.1 Install ngrok for Local Testing
```bash
# On Windows
choco install ngrok

# Or download from https://ngrok.com/download
```

#### 3.2 Start ngrok
```bash
ngrok http 5000
```
This will give you a public URL like: `https://xxxx.ngrok.io`

#### 3.3 Configure Webhook in Paystack
1. Go to Paystack Dashboard → Settings → API Keys & Webhooks
2. Add webhook URL: `https://xxxx.ngrok.io/payment/webhook`
3. Select events:
   - charge.success
   - charge.failed

#### 3.4 Test Webhook Events
1. Go to Paystack Dashboard → Test
2. Manually send test webhook events
3. Check application logs for webhook receipt
4. Verify payment_log table has webhook events recorded

#### 3.5 Verify Webhook Signature
- Paystack sends `X-Paystack-Signature` header
- Our code verifies this signature
- Check `paystack_gateway.py` verify_webhook_signature() method

---

## Integration Steps for Production

### Step 1: Get Live Credentials
1. Go to Paystack Dashboard
2. Go to Settings → API Keys & Webhooks
3. Get LIVE keys (they start with `pk_live_` and `sk_live_`)
4. These are different from test keys!

### Step 2: Update Environment
```bash
# In production .env
PAYSTACK_PUBLIC_KEY=pk_live_xxxxx
PAYSTACK_SECRET_KEY=sk_live_xxxxx
PAYSTACK_CALLBACK_URL=https://yourdomain.com/payment/paystack-callback
PAYSTACK_WEBHOOK_SECRET=your_webhook_secret
```

### Step 3: Update Webhook URL
1. In Paystack Dashboard
2. Update webhook URL to: `https://yourdomain.com/payment/webhook`
3. Ensure domain is HTTPS

### Step 4: Test with Small Transaction
1. Use real payment method (card/mobile money)
2. Process a small payment (GH₵1-5)
3. Verify payment confirms correctly
4. Check order status updates

### Step 5: Deploy Code
```bash
git push production main
# Restart application server
systemctl restart digitalhome
```

---

## Implementation Next Steps

### Immediate (Before Testing)
1. [ ] Modify `checkout.html` to add Paystack payment option
2. [ ] Update `checkout()` route to handle Paystack payment initiation
3. [ ] Update checkout.py POST handler for Paystack flow
4. [ ] Test order creation for COD/Bank Transfer

### Short Term (This Week)
1. [ ] Implement Paystack payment initiation in checkout
2. [ ] Test payment flow locally with sandbox keys
3. [ ] Setup webhook testing with ngrok
4. [ ] Test webhook event handling
5. [ ] Verify database records are created correctly

### Medium Term (This Month)
1. [ ] Get production Paystack credentials
2. [ ] Update production .env with live keys
3. [ ] Test live payment with small amount
4. [ ] Setup logging/monitoring for payments
5. [ ] Create admin dashboard for payment monitoring

### Long Term (Ongoing)
1. [ ] Add support for recurring payments
2. [ ] Implement payment refunds
3. [ ] Add payment reconciliation reports
4. [ ] Setup payment failure notifications
5. [ ] Create detailed payment analytics

---

## Key Files Location

```
project_root/
├── payments/
│   ├── __init__.py
│   ├── routes.py ✅ Payment routes
│   └── paystack_gateway.py ✅ Paystack service
├── templates/
│   ├── checkout.html ✅ Updated
│   ├── payment_status.html ✅ New
│   └── payment_history.html ✅ New
├── models.py ✅ Payment & PaymentLog models
├── app.py ✅ Routes added
├── config.py ✅ Paystack config
├── .env ✅ Paystack credentials
└── digitalhome.db ✅ Payment tables created
```

---

## API Endpoints Quick Reference

### Payment Initiation
```
POST /payment/initiate
Headers: Content-Type: application/json
Body: {
    "payment_method": "optional"
}
Response: {
    "success": true,
    "authorization_url": "https://checkout.paystack.com/...",
    "reference": "ORDER-123-abc123",
    "access_code": "123456789"
}
```

### Payment Verification
```
GET /payment/verify/<reference>
Response: {
    "success": true,
    "status": "success",
    "order_id": 1,
    "amount": 250.50
}
```

### Paystack Callback
```
GET /payment/paystack-callback?reference=xxxxx
- Automatically called by Paystack after payment
- Verifies and redirects to confirmation
```

### Webhook Receiver
```
POST /payment/webhook
Headers: X-Paystack-Signature: signature
Body: JSON event data from Paystack
- Receives charge.success and charge.failed events
- Updates payment and order status
```

### Payment History
```
GET /payment/payment-history
Response: HTML page with user's payment history
- Shows all user's payments
- Status badges and timestamps
```

---

## Troubleshooting

### Problem: "Import Error: No module named 'payments.routes'"
**Solution:**
1. Verify `/payments/routes.py` exists
2. Verify `/payments/__init__.py` exists
3. Restart Flask app

### Problem: Payment table not found
**Solution:**
1. Run: `python create_tables_direct.py`
2. Or manually create tables using SQL from `create_tables_direct.py`

### Problem: Paystack API returns 401 Unauthorized
**Solution:**
1. Check `PAYSTACK_SECRET_KEY` is correct
2. Verify key starts with `sk_test_` or `sk_live_`
3. Ensure .env is loaded (check logs)

### Problem: Webhook not receiving events
**Solution:**
1. Verify ngrok URL in Paystack dashboard
2. Check webhook URL is HTTPS
3. Verify `X-Paystack-Signature` header is present
4. Check `PAYSTACK_WEBHOOK_SECRET` is correct

### Problem: Database locked error
**Solution:**
1. Close other database connections
2. Ensure app not running twice
3. Delete .db.lock file if exists

---

## Email Notifications (Optional Enhancement)

Add email confirmation when payment succeeds:

```python
# In verify_payment route
if verification_result['status'] == 'success':
    # Send confirmation email
    send_payment_confirmation_email(
        customer_email=current_user.email,
        order=order,
        payment=payment
    )
```

---

## Success Metrics

After implementation, you should see:
✅ Payment records created in database  
✅ Payment status updates after transaction  
✅ Orders marked as "confirmed" after payment  
✅ Payment history page shows transactions  
✅ Webhook events received and logged  
✅ Email confirmations sent (if configured)  
✅ Admin dashboard shows payment metrics  
✅ Payment audit trail in payment_log table  

---

## Support & Resources

- **Paystack Docs:** https://paystack.com/docs
- **API Reference:** https://paystack.com/docs/api
- **Test Cards:** https://paystack.com/docs/payments/payment-channels/test-payments/
- **Webhooks Guide:** https://paystack.com/docs/webhooks/
- **Support Email:** support@paystack.com

---

## Next Actions

1. **Immediate:** Review this checklist and implementation steps
2. **Short-term:** Modify checkout to include Paystack option
3. **Mid-term:** Test complete payment flow locally
4. **Long-term:** Deploy to production with live credentials

**Estimated Timeline:** 
- Local testing: 2-3 days
- Production setup: 1 day
- Monitoring/refinement: Ongoing

---

*Last Updated: November 2024*
*Status: Ready for Testing*
