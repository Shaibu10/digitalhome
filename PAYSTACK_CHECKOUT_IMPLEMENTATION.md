# Paystack Checkout Integration - Complete Implementation

## Overview

This guide shows how to integrate Paystack payment directly into the checkout flow so users can pay with cards, mobile money, bank transfers, and USSD.

---

## Step 1: Update checkout.html to Add Paystack Option

Replace the payment method section with:

```html
<!-- Payment Method -->
<div class="card shadow-sm mb-4">
    <div class="card-header bg-primary text-white">
        <h5 class="card-title mb-0">
            <i class="fas fa-credit-card me-2"></i>Payment Method
        </h5>
    </div>
    <div class="card-body">
        <!-- Cash on Delivery -->
        <div class="form-check mb-3">
            <input class="form-check-input" type="radio" name="payment_method" id="payment_cod" 
                   value="cod" checked>
            <label class="form-check-label" for="payment_cod">
                <strong>Cash on Delivery</strong>
                <br>
                <small class="text-muted">Pay when your order arrives</small>
            </label>
        </div>

        <!-- Paystack Online Payment -->
        <div class="form-check mb-3">
            <input class="form-check-input" type="radio" name="payment_method" id="payment_paystack" 
                   value="paystack">
            <label class="form-check-label" for="payment_paystack">
                <strong>Pay with Card/Mobile Money</strong>
                <br>
                <small class="text-muted">
                    <i class="fas fa-lock text-success me-1"></i>
                    Secure payment via Paystack (Cards, Mobile Money, Bank Transfers, USSD)
                </small>
            </label>
        </div>

        <!-- Bank Transfer (Manual) -->
        <div class="form-check mb-3">
            <input class="form-check-input" type="radio" name="payment_method" id="payment_bank" 
                   value="bank_transfer">
            <label class="form-check-label" for="payment_bank">
                <strong>Bank Transfer</strong>
                <br>
                <small class="text-muted">Transfer to our account (details provided after order)</small>
            </label>
        </div>

        <!-- Mobile Money (Manual) -->
        <div class="form-check">
            <input class="form-check-input" type="radio" name="payment_method" id="payment_mobile" 
                   value="mobile_money">
            <label class="form-check-label" for="payment_mobile">
                <strong>Mobile Money (Manual)</strong>
                <br>
                <small class="text-muted">MTN Mobile Money, Vodafone Cash, etc. (details provided after order)</small>
            </label>
        </div>
    </div>
</div>
```

---

## Step 2: Update checkout.py Route for Paystack

Modify the `checkout()` function POST handler:

```python
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page for order placement with Paystack payment support."""
    from models import SystemSettings
    
    # ... (GET method remains the same)
    
    # POST - Process order
    data = request.get_json()
    settings = SystemSettings.get_settings()
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'postal_code', 'payment_method', 'shipping_method']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400
    
    # Get cart items and calculate totals (same as before)
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return jsonify({'success': False, 'message': 'Your cart is empty'}), 400
    
    subtotal = sum(item.product.final_price() * item.quantity for item in cart_items)
    shipping_options = calculate_shipping_cost(subtotal, cart_items)
    
    selected_shipping = data.get('shipping_method')
    if selected_shipping not in shipping_options:
        return jsonify({'success': False, 'message': 'Invalid shipping method'}), 400
    
    shipping_cost = shipping_options[selected_shipping]['cost']
    discount_amount = 0
    tax = subtotal * settings.tax_rate
    total = subtotal + shipping_cost + tax - discount_amount
    
    # Create order
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    payment_method = data.get('payment_method')
    
    # Determine payment status
    if payment_method == 'cod':
        payment_status = 'pending'  # COD - pending until delivery
    elif payment_method == 'paystack':
        payment_status = 'unpaid'  # Will be marked paid after successful payment
    else:
        payment_status = 'pending'  # Manual methods - pending manual payment
    
    order = Order(
        user_id=current_user.id,
        order_number=order_number,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        discount_amount=discount_amount,
        discount_percentage=0,
        total_amount=total,
        status='pending',
        payment_method=payment_method,
        payment_status=payment_status,
        shipping_address=f"{data.get('first_name')} {data.get('last_name')}",
        shipping_city=data.get('city'),
        shipping_postal_code=data.get('postal_code'),
        shipping_phone=data.get('phone'),
        notes=data.get('notes', '')
    )
    
    # Add order items
    for cart_item in cart_items:
        order_item = OrderItem(
            product_id=cart_item.product_id,
            product_name=cart_item.product.name,
            quantity=cart_item.quantity,
            unit_price=cart_item.product.final_price(),
            total_price=cart_item.product.final_price() * cart_item.quantity
        )
        order.order_items.append(order_item)
    
    db.session.add(order)
    db.session.commit()
    
    # Clear cart
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    log_user_activity(current_user, 'place_order', 
                     f'Placed order {order_number} for GH₵ {total:.2f}', request)
    
    # Handle payment methods
    if payment_method == 'cod':
        return jsonify({
            'success': True,
            'payment_method': 'cod',
            'redirect_url': url_for('order_confirmation', order_id=order.id)
        })
    
    elif payment_method == 'paystack':
        # Initiate Paystack payment
        from payments.paystack_gateway import PaystackGateway
        import uuid
        
        gateway = PaystackGateway()
        paystack_reference = f"ORDER-{order.id}-{uuid.uuid4().hex[:8]}"
        
        metadata = {
            'order_id': order.id,
            'user_id': current_user.id,
            'order_number': order_number
        }
        
        paystack_response = gateway.initialize_payment(
            email=current_user.email,
            amount=total,
            reference=paystack_reference,
            metadata=metadata
        )
        
        if not paystack_response['success']:
            return jsonify({
                'success': False,
                'message': 'Failed to initiate payment: ' + paystack_response.get('error', 'Unknown error')
            }), 500
        
        # Create payment record
        from models import Payment, PaymentLog
        
        payment = Payment(
            order_id=order.id,
            customer_email=current_user.email,
            customer_phone=getattr(current_user, 'phone_number', None),
            amount=total,
            paystack_reference=paystack_reference,
            status='pending'
        )
        
        db.session.add(payment)
        
        # Log payment initiation
        payment_log = PaymentLog(
            payment_id=None,  # Will be set after payment is added
            action='initiated',
            details=f'Payment initiated with reference: {paystack_reference}'
        )
        payment.logs.append(payment_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'payment_method': 'paystack',
            'authorization_url': paystack_response['authorization_url'],
            'reference': paystack_reference
        })
    
    else:  # Bank transfer, mobile money (manual)
        return jsonify({
            'success': True,
            'payment_method': payment_method,
            'redirect_url': url_for('order_confirmation', order_id=order.id)
        })
```

---

## Step 3: Add Paystack Initialization to checkout.html JavaScript

Add this at the end of checkout.html:

```html
<script src="https://js.paystack.co/v1/inline.js"></script>

<script>
const PAYSTACK_PUBLIC_KEY = "{{ config.PAYSTACK_PUBLIC_KEY }}";

// Handle checkout form submission
document.getElementById('checkoutForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const paymentMethod = document.querySelector('input[name="payment_method"]:checked').value;
    
    // If Paystack, handle specially
    if (paymentMethod === 'paystack') {
        handlePaystackCheckout();
    } else {
        handleRegularCheckout();
    }
});

function handleRegularCheckout() {
    // Regular checkout for COD, manual payment methods
    submitCheckoutForm();
}

function handlePaystackCheckout() {
    // First, create the order and get payment reference
    const formData = getCheckoutFormData();
    
    // Show loading
    const submitBtn = document.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    
    fetch('{{ url_for("checkout") }}', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            alert('Error: ' + data.message);
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
            return;
        }
        
        if (data.payment_method !== 'paystack') {
            // Non-Paystack method
            window.location.href = data.redirect_url;
            return;
        }
        
        // Initialize Paystack checkout
        const handler = PaystackPop.setup({
            key: PAYSTACK_PUBLIC_KEY,
            email: '{{ current_user.email }}',
            amount: parseFloat('{{ cart_total }}' || 0) * 100,  // Amount in kobo
            ref: data.reference,
            onClose: function() {
                alert('Payment window closed.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            },
            onSuccess: function(response) {
                // Redirect to payment confirmation
                window.location.href = `/payment-confirmed/${data.reference}`;
            }
        });
        
        handler.openIframe();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    });
}

function getCheckoutFormData() {
    return {
        first_name: document.getElementById('first_name').value,
        last_name: document.getElementById('last_name').value,
        phone: document.getElementById('phone').value,
        address: document.getElementById('address').value,
        city: document.getElementById('city').value,
        postal_code: document.getElementById('postal_code').value,
        email: document.getElementById('email').value,
        payment_method: document.querySelector('input[name="payment_method"]:checked').value,
        shipping_method: document.querySelector('input[name="shipping_method"]:checked').value,
        notes: document.querySelector('textarea[name="notes"]').value
    };
}

function submitCheckoutForm() {
    const formData = getCheckoutFormData();
    const submitBtn = document.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    
    fetch('{{ url_for("checkout") }}', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        alert('An error occurred while placing your order');
    });
}
</script>
```

---

## Step 4: Update checkout.html to Pass Cart Total

In the checkout.html checkout form section, make sure the total is accessible to JavaScript:

```html
<!-- Add this hidden input near the form -->
<input type="hidden" id="cart_total" value="{{ total }}">
```

Then update the JavaScript:

```javascript
amount: parseFloat(document.getElementById('cart_total').value || 0) * 100,
```

---

## Step 5: Verify Configuration

Make sure in `config.py`:

```python
# Paystack Payment Configuration
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_CALLBACK_URL = os.environ.get('PAYSTACK_CALLBACK_URL', 'http://localhost:5000/payment/paystack-callback')
PAYSTACK_WEBHOOK_SECRET = os.environ.get('PAYSTACK_WEBHOOK_SECRET')
```

And `.env`:

```env
PAYSTACK_PUBLIC_KEY=pk_test_your_public_key
PAYSTACK_SECRET_KEY=sk_test_your_secret_key
PAYSTACK_CALLBACK_URL=http://localhost:5000/payment/paystack-callback
PAYSTACK_WEBHOOK_SECRET=your_webhook_secret
```

---

## Step 6: Test the Flow

1. Start the app: `python run.py`
2. Create an account and verify email
3. Add items to cart
4. Go to checkout
5. Select "Pay with Card/Mobile Money"
6. Complete the form
7. Click "Place Order"
8. Paystack checkout should open
9. Use test card: 4084 0840 8408 4081
10. Complete payment
11. Should be redirected to payment confirmation

---

## Troubleshooting

### "Cannot read property 'setup' of undefined"
- Add `<script src="https://js.paystack.co/v1/inline.js"></script>` to template

### "Paystack public key is not defined"
- Check `.env` has PAYSTACK_PUBLIC_KEY
- Check `{{ config.PAYSTACK_PUBLIC_KEY }}` renders correctly in template

### "Invalid reference"
- Ensure reference is unique and includes only alphanumeric and hyphens
- Check payment record created in database

### Payment succeeds but order not confirmed
- Check payment verification endpoint is called
- Check database - payment.status should be 'success'
- Check order.payment_status should be 'paid'

---

## Next Steps

1. Implement this checkout integration
2. Test with Paystack test cards
3. Setup ngrok for webhook testing
4. Test webhook events
5. Deploy to production with live keys

---

*Implementation Status: Ready for Integration*
