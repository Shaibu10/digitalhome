# Paystack Integration - Implementation Checklist

## Phase 1: Pre-Implementation Setup (Week 1)

### Account & Credentials
- [ ] Register at https://dashboard.paystack.com/signup
- [ ] Complete KYC verification
- [ ] Add bank account for settlements
- [ ] Go to Settings → API Keys & Webhooks
- [ ] Copy Public Key: `pk_test_...`
- [ ] Copy Secret Key: `sk_test_...`
- [ ] Copy Webhook Secret (if provided)

### Environment Setup
- [ ] Create `.env` file in project root
- [ ] Add environment variables:
  ```
  PAYSTACK_PUBLIC_KEY=pk_test_your_key
  PAYSTACK_SECRET_KEY=sk_test_your_key
  PAYSTACK_CALLBACK_URL=http://localhost:5000/payment/paystack-callback
  PAYSTACK_WEBHOOK_SECRET=your_webhook_secret
  ```
- [ ] Install required packages: `pip install requests`
- [ ] Update `requirements.txt`

### Configuration
- [ ] Update `config.py` with Paystack settings
- [ ] Verify SQLALCHEMY_DATABASE_URI is set
- [ ] Test database connection

---

## Phase 2: Database Setup (Week 1-2)

### Models
- [ ] Review `Payment` model in documentation
- [ ] Review `PaymentLog` model in documentation
- [ ] Add to your `models.py`:
  ```python
  # Copy Payment and PaymentLog models from guide
  ```
- [ ] Update `Order` model if needed:
  - Add `payment_status` column
  - Add `paystack_reference` column

### Migrations
- [ ] Create migration: `flask db migrate -m "Add payment tables"`
- [ ] Review migration file
- [ ] Apply migration: `flask db upgrade`
- [ ] Verify tables created: `sqlite3 app.db ".tables"`

---

## Phase 3: Payment Gateway Service (Week 2)

### Files
- [ ] `payments/paystack_gateway.py` (provided)
  - Copy the complete PaystackGateway class
  - Verify all methods are present
  - Check logging is configured

- [ ] `payments/__init__.py` (provided)
  - Copy the init file for payments module

### Testing Service
- [ ] Test in Python shell:
  ```python
  from payments.paystack_gateway import PaystackGateway
  gateway = PaystackGateway()
  print(gateway.public_key)  # Should print your public key
  ```

---

## Phase 4: Payment Routes (Week 2-3)

### Routes File
- [ ] Create/update `routes/payments.py` (provided)
- [ ] Verify all endpoints:
  - `/payment/initiate` - POST
  - `/payment/verify/<reference>` - GET
  - `/payment/paystack-callback` - GET/POST
  - `/payment/webhook` - POST
  - `/payment/payment-history` - GET
  - `/payment/status/<payment_id>` - GET

### Register Blueprint
- [ ] In `app.py` or app initialization:
  ```python
  from routes.payments import payment_bp
  app.register_blueprint(payment_bp)
  ```

### Test Routes
- [ ] Test route registration:
  ```bash
  python -c "from app import app; print([rule for rule in app.url_map.iter_rules() if 'payment' in rule.rule])"
  ```

---

## Phase 5: Frontend Integration (Week 3)

### Templates
- [ ] Create `templates/checkout.html` (from guide)
- [ ] Create `templates/payment_status.html` (from guide)
- [ ] Create `templates/payment_history.html` (from guide)

### Checkout Page Updates
- [ ] Update existing checkout template to include payment method selection
- [ ] Add payment form with radio buttons
- [ ] Add JavaScript to handle payment button click
- [ ] Test form submission

### Payment Status Page
- [ ] Create dedicated payment confirmation/status page
- [ ] Handle success state display
- [ ] Handle failed state display
- [ ] Handle pending state with polling/refresh

### CSS/Styling
- [ ] Add CSS for payment method selection
- [ ] Add loading spinner styles
- [ ] Add success/failure alert styles
- [ ] Test responsive design on mobile

---

## Phase 6: Testing with Sandbox (Week 3-4)

### Test Cards
- [ ] Visa (Success): `4084 0840 8408 4081`
- [ ] Visa (Failed): `4111 1111 1111 1111`
- [ ] Mastercard (Success): `5399 8381 4732 0366`

### Manual Testing
- [ ] Start app: `python app.py`
- [ ] Navigate to checkout
- [ ] Select a payment method
- [ ] Click "Proceed to Payment"
- [ ] Verify redirected to Paystack checkout
- [ ] Enter test card details
- [ ] Complete payment
- [ ] Verify redirected back to your site
- [ ] Check payment record created in database

### Test Scenarios
- [ ] ✓ Successful card payment
- [ ] ✓ Failed card payment (use failed test card)
- [ ] ✓ Payment verification on callback
- [ ] ✓ Order status updated after payment
- [ ] ✓ Payment history displays correctly
- [ ] ✓ Invalid payment reference handling

### Database Verification
- [ ] Check `payment` table has records
- [ ] Check `payment_log` table has audit trail
- [ ] Check `order` table updated with payment_status
- [ ] Verify all timestamps are correct

---

## Phase 7: Webhook Setup (Week 4)

### Local Webhook Testing
- [ ] Install ngrok: `choco install ngrok` (Windows)
- [ ] Start ngrok: `ngrok http 5000`
- [ ] Copy ngrok URL: `https://xxx.ngrok.io`
- [ ] Note the URL for next step

### Paystack Webhook Configuration
- [ ] Log in to Paystack Dashboard
- [ ] Go to Settings → API Keys & Webhooks
- [ ] Scroll to "Webhooks"
- [ ] Add webhook URL: `https://xxx.ngrok.io/payment/webhook` (use ngrok URL)
- [ ] Enable these events:
  - [ ] charge.success
  - [ ] charge.failed
- [ ] Save webhook

### Webhook Testing
- [ ] In Paystack dashboard, find "Webhooks" test section
- [ ] Send test webhook for charge.success
- [ ] Check your logs for webhook reception
- [ ] Verify database was updated
- [ ] Send test webhook for charge.failed
- [ ] Verify failure was logged correctly

### Production Webhook Configuration (Later)
- [ ] Update webhook URL to production domain
- [ ] Use HTTPS production domain
- [ ] Example: `https://yourdomain.com/payment/webhook`

---

## Phase 8: Production Preparation (Week 4-5)

### Credentials Switch
- [ ] Create `.env.production` file
- [ ] Get PRODUCTION Paystack keys from dashboard
  - Look for "LIVE" keys (not TEST keys)
  - Note the prefix changes: `pk_live_` and `sk_live_`
- [ ] Update production environment variables
- [ ] DO NOT commit keys to Git

### Security Checklist
- [ ] ✓ Secret key stored in environment variable (not hardcoded)
- [ ] ✓ HTTPS enabled on all payment endpoints
- [ ] ✓ Webhook signature verification implemented
- [ ] ✓ Error messages don't expose sensitive data
- [ ] ✓ Input validation on all endpoints
- [ ] ✓ CORS properly configured (if API-based)
- [ ] ✓ Rate limiting on payment endpoints

### Error Handling
- [ ] ✓ Network timeout handling
- [ ] ✓ Invalid reference handling
- [ ] ✓ Missing order handling
- [ ] ✓ Duplicate payment detection
- [ ] ✓ Webhook retry handling
- [ ] ✓ Logging of all errors

### Monitoring Setup
- [ ] Set up error logging (Sentry, CloudWatch, etc.)
- [ ] Create payment monitoring dashboard
- [ ] Set up alerts for failed payments
- [ ] Monitor webhook delivery
- [ ] Track transaction volume and revenue

---

## Phase 9: Deployment (Week 5)

### Pre-Deployment
- [ ] Code review of all payment code
- [ ] Security audit of payment flows
- [ ] Load testing with concurrent payments
- [ ] Full integration test suite passes

### Deployment Steps
- [ ] Deploy to production server
- [ ] Update `.env` with production credentials
- [ ] Run database migrations on production
- [ ] Update webhook URL to production domain in Paystack
- [ ] Test payment flow end-to-end on production
- [ ] Monitor for errors in first 24 hours

### Post-Deployment
- [ ] Test with small transaction amount first
- [ ] Verify payment confirmation emails working
- [ ] Check payment history for all users
- [ ] Monitor payment success rate
- [ ] Verify webhook processing
- [ ] Monitor server logs for errors
- [ ] Have rollback plan ready

---

## Phase 10: Documentation & Support (Week 5-6)

### Documentation
- [ ] Document payment flow for support team
- [ ] Create troubleshooting guide
- [ ] Document API endpoints
- [ ] Create runbook for failed payments
- [ ] Document backup/recovery procedures

### Support Training
- [ ] Train support team on payment issues
- [ ] Document common error messages
- [ ] Create FAQ for customers
- [ ] Set up payment support escalation

### Ongoing Maintenance
- [ ] Monitor payment metrics weekly
- [ ] Review failed transactions
- [ ] Test webhook delivery monthly
- [ ] Update documentation as needed
- [ ] Plan for future features (refunds, subscriptions)

---

## Quick File Checklist

### Files Provided in Guide
- [ ] `PAYSTACK_INTEGRATION_GUIDE.md` - Complete guide (already created)
- [ ] `payments/paystack_gateway.py` - Gateway service (already created)
- [ ] `payments/__init__.py` - Module init (already created)
- [ ] `routes/payments.py` - Payment routes (already created)

### Files You Need to Create/Modify
- [ ] `.env` - Environment variables
- [ ] `models.py` - Add Payment and PaymentLog models
- [ ] `config.py` - Add Paystack configuration
- [ ] `app.py` - Register payment blueprint
- [ ] `templates/checkout.html` - Payment UI
- [ ] `templates/payment_status.html` - Status page
- [ ] `templates/payment_history.html` - History page
- [ ] `requirements.txt` - Add requests package

---

## Testing Verification

Run these commands to verify setup:

```bash
# 1. Check imports work
python -c "from payments.paystack_gateway import PaystackGateway; print('✓ Gateway import OK')"

# 2. Check models exist
python -c "from models import Payment, PaymentLog; print('✓ Models import OK')"

# 3. Check routes registered
python -c "from app import app; routes = [rule for rule in app.url_map.iter_rules() if 'payment' in rule.rule]; print(f'✓ Found {len(routes)} payment routes')"

# 4. Check database tables
sqlite3 app.db ".schema payment"

# 5. Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'PAYSTACK_PUBLIC_KEY: {os.getenv(\"PAYSTACK_PUBLIC_KEY\", \"NOT SET\")[:20]}...')"
```

---

## Support & Troubleshooting

### Common Issues

**Issue**: "No payment record found"
- Check that payment was created in database
- Verify order_id matches
- Check for duplicate payment records

**Issue**: "Invalid webhook signature"
- Verify PAYSTACK_WEBHOOK_SECRET is correct
- Check webhook payload is not modified
- Check signature header name is correct

**Issue**: "Payment initialization failed"
- Verify API credentials are correct
- Check internet connection
- Verify Paystack account is active
- Check request payload format

### Getting Help
- Paystack Documentation: https://paystack.com/docs
- Paystack Support: support@paystack.com
- Check application logs: `tail -f logs/payments.log`
- Review database records: Check payment table

---

## Completion Status

- [ ] All 10 phases completed
- [ ] All manual tests passed
- [ ] Production credentials configured
- [ ] Webhook live and processing
- [ ] Monitoring and alerts active
- [ ] Support team trained
- [ ] Ready for production traffic

**Estimated Timeline**: 4-6 weeks from start to full production deployment
