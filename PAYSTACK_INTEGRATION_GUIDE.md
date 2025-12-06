# Paystack Integration Guide - Complete Implementation

## Executive Summary

This guide provides a complete, production-ready Paystack integration for your Flask e-commerce platform. Paystack handles all payment methods (cards, mobile money, bank transfers, USSD) through a single, reliable API.

---

## 1. Quick Start Overview

### What Paystack Provides
- ✅ Card payments (Visa, Mastercard, Amex)
- ✅ Mobile Money (MTN, Vodafone, AirtelTigo)
- ✅ Bank transfers
- ✅ USSD codes
- ✅ PCI DSS compliance (handled by Paystack)
- ✅ Webhook support for payment confirmations
- ✅ Sandbox environment for testing

### Setup Time: 2-3 weeks

---

## 2. Pre-Implementation Checklist

### 2.1 Register with Paystack

1. **Create Business Account**
   - Visit: https://dashboard.paystack.com/signup
   - Sign up with business email
   - Verify email address

2. **Complete KYC Verification**
   - Submit business information
   - Upload business registration documents
   - Add bank account for settlements
   - Verify phone number

3. **Get API Credentials**
   - Go to Settings → API Keys
   - Copy your **Public Key** (use on frontend)
   - Copy your **Secret Key** (use on backend only)
   - Note your **Webhook URL** setting

### 2.2 Environment Setup

```bash
# Install required packages
pip install paystack
pip install requests
pip install python-dotenv
```

### 2.3 Configuration

Create `.env` file:
```env
# Paystack Configuration
PAYSTACK_PUBLIC_KEY=pk_test_your_public_key_here
PAYSTACK_SECRET_KEY=sk_test_your_secret_key_here
PAYSTACK_CALLBACK_URL=https://yourdomain.com/payment/paystack-callback
PAYSTACK_WEBHOOK_SECRET=your_webhook_secret_here

# For production
# PAYSTACK_PUBLIC_KEY=pk_live_your_public_key_here
# PAYSTACK_SECRET_KEY=sk_live_your_secret_key_here
```

---

## 3. Database Models

### 3.1 Add Payment Model

```python
# models.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Payment(db.Model):
    """Paystack Payment Records"""
    __tablename__ = 'payment'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Order Reference
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    
    # Customer Information
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20))
    
    # Payment Details
    amount = db.Column(db.Float, nullable=False)  # In GHS
    currency = db.Column(db.String(3), default='GHS')
    
    # Paystack References
    paystack_reference = db.Column(db.String(100), unique=True, nullable=False)
    paystack_authorization_code = db.Column(db.String(100))
    paystack_customer_id = db.Column(db.Integer)
    
    # Payment Method (set after payment)
    payment_method = db.Column(db.String(50))  # 'card', 'mobile_money', 'bank_transfer', 'ussd'
    
    # Status
    status = db.Column(
        db.String(50),
        default='pending'
    )  # pending, success, failed, abandoned
    
    status_reason = db.Column(db.String(255))  # Reason for failure
    
    # Timestamps
    initiated_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationship
    order = db.relationship('Order', backref='payment_record')
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.paystack_reference}>'


class PaymentLog(db.Model):
    """Payment Transaction Audit Log"""
    __tablename__ = 'payment_log'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
    
    action = db.Column(db.String(100))  # 'initiated', 'verified', 'confirmed', 'failed'
    details = db.Column(db.Text)  # JSON details
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    payment = db.relationship('Payment', backref='logs')
```

### 3.2 Update Order Model

```python
# In your Order model, add payment_status if not present

class Order(db.Model):
    # ... existing fields ...
    
    payment_status = db.Column(
        db.String(50),
        default='pending'
    )  # pending, paid, failed
    
    paystack_reference = db.Column(db.String(100))  # Link to payment
```

### 3.3 Create Migration

```bash
# Run this to create tables
flask db migrate -m "Add payment tables"
flask db upgrade
```

---

## 4. Configuration Setup

### 4.1 Update config.py

```python
# config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base Configuration"""
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Paystack Configuration
    PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
    PAYSTACK_CALLBACK_URL = os.getenv('PAYSTACK_CALLBACK_URL')
    PAYSTACK_WEBHOOK_SECRET = os.getenv('PAYSTACK_WEBHOOK_SECRET')
    
    # Payment Settings
    PAYMENT_CURRENCY = 'GHS'
    PAYMENT_TIMEOUT = 3600  # 1 hour in seconds
    WEBHOOK_RETRY_LIMIT = 3


class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing Configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

---

## 5. Payment Gateway Service

### 5.1 Create Paystack Gateway Service

```python
# payments/paystack_gateway.py

import requests
import hmac
import hashlib
from flask import current_app
from datetime import datetime


class PaystackGateway:
    """Paystack Payment Gateway Service"""
    
    BASE_URL = 'https://api.paystack.co'
    
    def __init__(self):
        self.secret_key = current_app.config['PAYSTACK_SECRET_KEY']
        self.public_key = current_app.config['PAYSTACK_PUBLIC_KEY']
    
    def _get_headers(self):
        """Get headers for Paystack API requests"""
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def initialize_payment(self, email, amount, reference, callback_url=None, metadata=None):
        """
        Initialize payment on Paystack
        
        Args:
            email (str): Customer email
            amount (float): Amount in GHS
            reference (str): Unique reference for this transaction
            callback_url (str): URL to redirect after payment
            metadata (dict): Additional data to store with payment
        
        Returns:
            dict: Response with authorization_url and other details
        """
        
        # Convert amount to kobo (Paystack uses smallest currency unit)
        amount_kobo = int(amount * 100)
        
        payload = {
            'email': email,
            'amount': amount_kobo,
            'reference': reference,
            'callback_url': callback_url or current_app.config['PAYSTACK_CALLBACK_URL'],
        }
        
        if metadata:
            payload['metadata'] = metadata
        
        try:
            response = requests.post(
                f'{self.BASE_URL}/transaction/initialize',
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'authorization_url': data['data']['authorization_url'],
                    'access_code': data['data']['access_code'],
                    'reference': data['data']['reference']
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Payment initialization failed')
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API connection failed: {str(e)}'
            }
    
    def verify_payment(self, reference):
        """
        Verify payment status with Paystack
        
        Args:
            reference (str): Payment reference to verify
        
        Returns:
            dict: Payment details and status
        """
        
        try:
            response = requests.get(
                f'{self.BASE_URL}/transaction/verify/{reference}',
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') and data['data']['status'] == 'success':
                return {
                    'success': True,
                    'status': 'success',
                    'amount': data['data']['amount'] / 100,  # Convert from kobo
                    'reference': data['data']['reference'],
                    'customer_email': data['data']['customer']['email'],
                    'authorization': data['data'].get('authorization', {}),
                    'payment_method': self._extract_payment_method(data['data']),
                    'authorization_code': data['data']['authorization'].get('authorization_code'),
                    'timestamp': data['data']['paid_at']
                }
            else:
                return {
                    'success': False,
                    'status': data['data'].get('status', 'unknown'),
                    'error': 'Payment verification failed'
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Verification failed: {str(e)}'
            }
    
    def _extract_payment_method(self, transaction_data):
        """Extract payment method from transaction data"""
        auth = transaction_data.get('authorization', {})
        channel = auth.get('channel', 'unknown')
        
        method_map = {
            'card': 'card',
            'mobile_money': 'mobile_money',
            'bank': 'bank_transfer',
            'ussd': 'ussd'
        }
        
        return method_map.get(channel, channel)
    
    def verify_webhook_signature(self, payload, signature):
        """
        Verify webhook signature from Paystack
        
        Args:
            payload (bytes): Raw request body
            signature (str): X-Paystack-Signature header value
        
        Returns:
            bool: True if signature is valid
        """
        
        expected_signature = hmac.new(
            current_app.config['PAYSTACK_WEBHOOK_SECRET'].encode() 
            if current_app.config.get('PAYSTACK_WEBHOOK_SECRET')
            else current_app.config['PAYSTACK_SECRET_KEY'].encode(),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def get_balance(self):
        """Get account balance"""
        try:
            response = requests.get(
                f'{self.BASE_URL}/balance',
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'balance': data['data'][0]['balance'] / 100  # Convert from kobo
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Balance fetch failed')
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Balance fetch failed: {str(e)}'
            }
    
    def create_customer(self, email, first_name, last_name, phone=None):
        """Create or get customer"""
        payload = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name
        }
        
        if phone:
            payload['phone'] = phone
        
        try:
            response = requests.post(
                f'{self.BASE_URL}/customer',
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'customer_id': data['data']['customer_code']
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Customer creation failed')
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Customer creation failed: {str(e)}'
            }
```

---

## 6. Payment Routes/Endpoints

### 6.1 Create Payment Routes

```python
# routes/payments.py

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime
import uuid
from models import db, Payment, PaymentLog, Order
from payments.paystack_gateway import PaystackGateway


payment_bp = Blueprint('payments', __name__, url_prefix='/payment')
paystack = PaystackGateway()


@payment_bp.route('/initiate', methods=['POST'])
@login_required
def initiate_payment():
    """Initiate Paystack payment"""
    
    try:
        data = request.get_json()
        
        # Get user's pending order
        order = Order.query.filter_by(
            user_id=current_user.id,
            status='pending'
        ).first()
        
        if not order:
            return jsonify({
                'success': False,
                'error': 'No pending order found'
            }), 404
        
        if order.total_amount <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid order amount'
            }), 400
        
        # Generate unique reference
        paystack_reference = f"{order.id}-{uuid.uuid4().hex[:8]}"
        
        # Metadata to store with payment
        metadata = {
            'order_id': order.id,
            'user_id': current_user.id,
            'user_email': current_user.email
        }
        
        # Initialize payment with Paystack
        paystack_response = paystack.initialize_payment(
            email=current_user.email,
            amount=order.total_amount,
            reference=paystack_reference,
            metadata=metadata
        )
        
        if not paystack_response['success']:
            return jsonify({
                'success': False,
                'error': paystack_response.get('error', 'Payment initialization failed')
            }), 500
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            customer_email=current_user.email,
            customer_phone=current_user.phone if hasattr(current_user, 'phone') else None,
            amount=order.total_amount,
            paystack_reference=paystack_reference,
            status='pending'
        )
        
        db.session.add(payment)
        
        # Log payment initiation
        payment_log = PaymentLog(
            payment_id=payment.id,
            action='initiated',
            details=f'Payment initialized with reference: {paystack_reference}'
        )
        db.session.add(payment_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'authorization_url': paystack_response['authorization_url'],
            'reference': paystack_reference,
            'access_code': paystack_response['access_code']
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Payment initiation error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Payment initialization failed'
        }), 500


@payment_bp.route('/verify/<reference>', methods=['GET'])
@login_required
def verify_payment(reference):
    """Verify payment status"""
    
    try:
        # Verify with Paystack
        verification_result = paystack.verify_payment(reference)
        
        if not verification_result['success']:
            return jsonify({
                'success': False,
                'error': verification_result.get('error', 'Verification failed')
            }), 400
        
        # Get payment record
        payment = Payment.query.filter_by(
            paystack_reference=reference
        ).first()
        
        if not payment:
            return jsonify({
                'success': False,
                'error': 'Payment record not found'
            }), 404
        
        # Update payment record
        if verification_result['status'] == 'success':
            payment.status = 'success'
            payment.completed_at = datetime.utcnow()
            payment.payment_method = verification_result.get('payment_method')
            payment.paystack_authorization_code = verification_result.get('authorization_code')
            
            # Update order
            order = payment.order
            order.status = 'confirmed'
            order.payment_status = 'paid'
            
            # Log successful payment
            payment_log = PaymentLog(
                payment_id=payment.id,
                action='verified',
                details=f'Payment verified successfully'
            )
            db.session.add(payment_log)
            
            # Send confirmation email (implement as needed)
            send_payment_confirmation_email(order)
        
        else:
            payment.status = 'failed'
            payment.status_reason = verification_result.get('error', 'Verification failed')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'status': payment.status,
            'order_id': payment.order_id,
            'amount': payment.amount
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'Payment verification error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Verification failed'
        }), 500


@payment_bp.route('/paystack-callback', methods=['GET', 'POST'])
def paystack_callback():
    """Handle Paystack payment callback"""
    
    if request.method == 'GET':
        reference = request.args.get('reference')
        
        if not reference:
            return redirect(url_for('main.checkout', error='No reference provided'))
        
        # Verify payment
        verification_result = paystack.verify_payment(reference)
        
        if verification_result['success']:
            return redirect(url_for('main.order_confirmation', reference=reference))
        else:
            return redirect(url_for('main.checkout', error='Payment verification failed'))
    
    return jsonify({'success': False}), 400


@payment_bp.route('/webhook', methods=['POST'])
def paystack_webhook():
    """
    Paystack webhook endpoint for payment confirmations
    
    Set this URL in Paystack dashboard:
    Settings → API Keys & Webhooks → Webhooks
    URL: https://yourdomain.com/payment/webhook
    """
    
    try:
        # Verify webhook signature
        signature = request.headers.get('X-Paystack-Signature', '')
        
        if not signature:
            current_app.logger.warning('Webhook received without signature')
            return jsonify({'success': False}), 401
        
        # Verify signature
        if not paystack.verify_webhook_signature(request.data, signature):
            current_app.logger.warning('Invalid webhook signature')
            return jsonify({'success': False}), 401
        
        data = request.get_json()
        
        if data.get('event') == 'charge.success':
            event_data = data.get('data', {})
            reference = event_data.get('reference')
            
            # Get payment record
            payment = Payment.query.filter_by(
                paystack_reference=reference
            ).first()
            
            if payment:
                payment.status = 'success'
                payment.completed_at = datetime.utcnow()
                payment.payment_method = event_data.get('channel', 'unknown')
                payment.paystack_authorization_code = event_data.get(
                    'authorization', {}
                ).get('authorization_code')
                
                # Update order
                order = payment.order
                order.status = 'confirmed'
                order.payment_status = 'paid'
                
                # Log webhook
                payment_log = PaymentLog(
                    payment_id=payment.id,
                    action='webhook_confirmed',
                    details=f'Payment confirmed via webhook'
                )
                db.session.add(payment_log)
                db.session.commit()
                
                current_app.logger.info(f'Payment {reference} confirmed via webhook')
                
                # Send confirmation email
                send_payment_confirmation_email(order)
        
        elif data.get('event') == 'charge.failed':
            event_data = data.get('data', {})
            reference = event_data.get('reference')
            
            payment = Payment.query.filter_by(
                paystack_reference=reference
            ).first()
            
            if payment:
                payment.status = 'failed'
                payment.status_reason = event_data.get('gateway_response', 'Payment failed')
                
                payment_log = PaymentLog(
                    payment_id=payment.id,
                    action='webhook_failed',
                    details=f'Payment failed: {event_data.get("gateway_response")}'
                )
                db.session.add(payment_log)
                db.session.commit()
                
                current_app.logger.warning(f'Payment {reference} failed via webhook')
        
        return jsonify({'success': True}), 200
    
    except Exception as e:
        current_app.logger.error(f'Webhook error: {str(e)}')
        return jsonify({'success': False}), 500


@payment_bp.route('/payment-history', methods=['GET'])
@login_required
def payment_history():
    """Get user's payment history"""
    
    try:
        payments = Payment.query.join(Order).filter(
            Order.user_id == current_user.id
        ).order_by(Payment.initiated_at.desc()).all()
        
        return render_template('payment_history.html', payments=payments)
    
    except Exception as e:
        current_app.logger.error(f'Payment history error: {str(e)}')
        return redirect(url_for('main.index'))


def send_payment_confirmation_email(order):
    """Send payment confirmation email"""
    # Implement using your email service
    # Example: send_email(
    #     recipient=order.user.email,
    #     subject=f'Order Confirmation - {order.id}',
    #     template='emails/payment_confirmation.html',
    #     order=order
    # )
    pass
```

---

## 7. Frontend Integration

### 7.1 Checkout Template

```html
<!-- templates/checkout.html -->

{% extends 'base.html' %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-8">
            <h2>Checkout</h2>
            
            <!-- Order Summary -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5>Order Summary</h5>
                </div>
                <div class="card-body">
                    <table class="table table-sm">
                        <tr>
                            <td>Subtotal:</td>
                            <td class="text-right">GHS {{ "%.2f"|format(order.subtotal) }}</td>
                        </tr>
                        <tr>
                            <td>Shipping:</td>
                            <td class="text-right">GHS {{ "%.2f"|format(order.shipping) }}</td>
                        </tr>
                        <tr>
                            <td>Tax:</td>
                            <td class="text-right">GHS {{ "%.2f"|format(order.tax) }}</td>
                        </tr>
                        <tr class="font-weight-bold border-top">
                            <td>Total:</td>
                            <td class="text-right">GHS {{ "%.2f"|format(order.total_amount) }}</td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <!-- Payment Method Selection -->
            <div class="card">
                <div class="card-header">
                    <h5>Select Payment Method</h5>
                </div>
                <div class="card-body">
                    <div id="payment-options" class="mb-4">
                        <div class="payment-method mb-3">
                            <input type="radio" name="payment_method" value="card" id="payment_card" checked>
                            <label for="payment_card" class="ml-2">
                                <img src="/static/images/card-icon.png" alt="Card" style="height: 24px;">
                                Credit/Debit Card
                            </label>
                        </div>
                        
                        <div class="payment-method mb-3">
                            <input type="radio" name="payment_method" value="mobile_money" id="payment_momo">
                            <label for="payment_momo" class="ml-2">
                                <img src="/static/images/momo-icon.png" alt="Mobile Money" style="height: 24px;">
                                Mobile Money (MTN, Vodafone, AirtelTigo)
                            </label>
                        </div>
                        
                        <div class="payment-method mb-3">
                            <input type="radio" name="payment_method" value="bank_transfer" id="payment_bank">
                            <label for="payment_bank" class="ml-2">
                                <img src="/static/images/bank-icon.png" alt="Bank" style="height: 24px;">
                                Bank Transfer
                            </label>
                        </div>
                        
                        <div class="payment-method mb-3">
                            <input type="radio" name="payment_method" value="ussd" id="payment_ussd">
                            <label for="payment_ussd" class="ml-2">
                                <img src="/static/images/ussd-icon.png" alt="USSD" style="height: 24px;">
                                USSD Code
                            </label>
                        </div>
                    </div>
                    
                    <!-- Payment Processing Info -->
                    <div id="payment-info" class="alert alert-info">
                        <small>
                            You will be redirected to Paystack to complete your payment securely.
                            All transactions are encrypted and protected.
                        </small>
                    </div>
                    
                    <!-- Process Payment Button -->
                    <button id="pay-button" class="btn btn-primary btn-lg btn-block">
                        <i class="fas fa-lock"></i> Proceed to Payment
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Order Details Sidebar -->
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5>Delivery Information</h5>
                </div>
                <div class="card-body">
                    <p><strong>Name:</strong> {{ current_user.first_name }} {{ current_user.last_name }}</p>
                    <p><strong>Email:</strong> {{ current_user.email }}</p>
                    <p><strong>Address:</strong> {{ order.shipping_address }}</p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Loading Spinner (hidden by default) -->
<div id="loading-spinner" class="spinner-overlay" style="display: none;">
    <div class="spinner-content">
        <div class="spinner-border" role="status">
            <span class="sr-only">Processing payment...</span>
        </div>
        <p class="mt-3">Processing your payment...</p>
    </div>
</div>

{% endblock %}

{% block scripts %}
<script>
document.getElementById('pay-button').addEventListener('click', function() {
    const paymentMethod = document.querySelector('input[name="payment_method"]:checked').value;
    const loadingSpinner = document.getElementById('loading-spinner');
    
    // Show loading spinner
    loadingSpinner.style.display = 'flex';
    
    // Send payment initiation request
    fetch('{{ url_for("payments.initiate_payment") }}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            payment_method: paymentMethod
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Redirect to Paystack
            window.location.href = data.authorization_url;
        } else {
            loadingSpinner.style.display = 'none';
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        loadingSpinner.style.display = 'none';
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
});
</script>
{% endblock %}
```

### 7.2 Payment Status/Confirmation Page

```html
<!-- templates/payment_status.html -->

{% extends 'base.html' %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            {% if payment.status == 'success' %}
            <!-- Success State -->
            <div class="card border-success">
                <div class="card-body text-center">
                    <div class="mb-4">
                        <i class="fas fa-check-circle text-success" style="font-size: 3rem;"></i>
                    </div>
                    <h4 class="card-title text-success">Payment Successful!</h4>
                    <p class="card-text">Your payment has been processed successfully.</p>
                    
                    <div class="alert alert-light">
                        <table class="table table-sm table-borderless">
                            <tr>
                                <td><strong>Order ID:</strong></td>
                                <td>#{{ payment.order_id }}</td>
                            </tr>
                            <tr>
                                <td><strong>Amount:</strong></td>
                                <td>GHS {{ "%.2f"|format(payment.amount) }}</td>
                            </tr>
                            <tr>
                                <td><strong>Reference:</strong></td>
                                <td>{{ payment.paystack_reference }}</td>
                            </tr>
                            <tr>
                                <td><strong>Payment Method:</strong></td>
                                <td>{{ payment.payment_method|title }}</td>
                            </tr>
                            <tr>
                                <td><strong>Date:</strong></td>
                                <td>{{ payment.completed_at.strftime('%B %d, %Y %H:%M') }}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <p class="text-muted">A confirmation email has been sent to {{ payment.customer_email }}</p>
                    
                    <a href="{{ url_for('main.orders') }}" class="btn btn-primary">View Orders</a>
                </div>
            </div>
            
            {% elif payment.status == 'failed' %}
            <!-- Failed State -->
            <div class="card border-danger">
                <div class="card-body text-center">
                    <div class="mb-4">
                        <i class="fas fa-times-circle text-danger" style="font-size: 3rem;"></i>
                    </div>
                    <h4 class="card-title text-danger">Payment Failed</h4>
                    <p class="card-text">{{ payment.status_reason }}</p>
                    
                    <div class="alert alert-warning">
                        <p>Your payment could not be processed. Please try again or contact support.</p>
                    </div>
                    
                    <a href="{{ url_for('main.checkout') }}" class="btn btn-primary">Try Again</a>
                    <a href="{{ url_for('main.index') }}" class="btn btn-secondary">Return Home</a>
                </div>
            </div>
            
            {% else %}
            <!-- Pending/Processing State -->
            <div class="card">
                <div class="card-body text-center">
                    <div class="mb-4">
                        <div class="spinner-border" role="status">
                            <span class="sr-only">Processing...</span>
                        </div>
                    </div>
                    <h4 class="card-title">Processing Payment</h4>
                    <p class="card-text">Please wait while we process your payment...</p>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

### 7.3 Payment History Template

```html
<!-- templates/payment_history.html -->

{% extends 'base.html' %}

{% block content %}
<div class="container mt-5">
    <h2>Payment History</h2>
    
    {% if payments %}
    <div class="table-responsive">
        <table class="table table-hover">
            <thead class="table-light">
                <tr>
                    <th>Order ID</th>
                    <th>Amount</th>
                    <th>Method</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th>Reference</th>
                </tr>
            </thead>
            <tbody>
                {% for payment in payments %}
                <tr>
                    <td>#{{ payment.order_id }}</td>
                    <td>GHS {{ "%.2f"|format(payment.amount) }}</td>
                    <td>
                        {% if payment.payment_method %}
                            {{ payment.payment_method|title }}
                        {% else %}
                            <span class="badge badge-secondary">Pending</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if payment.status == 'success' %}
                            <span class="badge badge-success">Paid</span>
                        {% elif payment.status == 'failed' %}
                            <span class="badge badge-danger">Failed</span>
                        {% else %}
                            <span class="badge badge-warning">Pending</span>
                        {% endif %}
                    </td>
                    <td>{{ payment.initiated_at.strftime('%b %d, %Y') }}</td>
                    <td>{{ payment.paystack_reference }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="alert alert-info">
        <p>No payments found. Start shopping to make your first purchase!</p>
    </div>
    {% endif %}
</div>
{% endblock %}
```

---

## 8. App Registration

### 8.1 Register Blueprint

```python
# app.py or __init__.py

from flask import Flask
from routes.payments import payment_bp

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load config
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from models import db
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(payment_bp)
    
    return app
```

---

## 9. Testing

### 9.1 Unit Tests

```python
# tests/test_paystack.py

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from models import db, Payment, Order
from payments.paystack_gateway import PaystackGateway


class PaystackTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['PAYSTACK_SECRET_KEY'] = 'sk_test_fake_key'
        self.app.config['PAYSTACK_PUBLIC_KEY'] = 'pk_test_fake_key'
        self.app.config['PAYSTACK_CALLBACK_URL'] = 'http://localhost/payment/paystack-callback'
        
        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    @patch('requests.post')
    def test_initialize_payment(self, mock_post):
        """Test payment initialization"""
        with self.app.app_context():
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'status': True,
                'data': {
                    'authorization_url': 'https://checkout.paystack.com/test',
                    'access_code': 'test_code',
                    'reference': 'ref_123'
                }
            }
            mock_post.return_value = mock_response
            
            gateway = PaystackGateway()
            result = gateway.initialize_payment(
                email='test@example.com',
                amount=100,
                reference='ref_123'
            )
            
            self.assertTrue(result['success'])
            self.assertIn('authorization_url', result)
    
    @patch('requests.get')
    def test_verify_payment(self, mock_get):
        """Test payment verification"""
        with self.app.app_context():
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'status': True,
                'data': {
                    'status': 'success',
                    'amount': 10000,
                    'reference': 'ref_123',
                    'customer': {'email': 'test@example.com'},
                    'authorization': {'authorization_code': 'auth_123'},
                    'paid_at': '2025-01-01T12:00:00Z'
                }
            }
            mock_get.return_value = mock_response
            
            gateway = PaystackGateway()
            result = gateway.verify_payment('ref_123')
            
            self.assertTrue(result['success'])
            self.assertEqual(result['amount'], 100)


if __name__ == '__main__':
    unittest.main()
```

### 9.2 Manual Testing Checklist

```
[ ] Test with sandbox credentials
    [ ] Card payment (use test card: 4084084084084081)
    [ ] Mobile money selection
    [ ] Bank transfer selection
    [ ] USSD selection

[ ] Test callback handling
    [ ] Verify successful payment redirects to confirmation
    [ ] Verify failed payment shows error message
    [ ] Verify payment record is created

[ ] Test webhook verification
    [ ] Send test webhook from Paystack dashboard
    [ ] Verify payment status is updated
    [ ] Verify order status is updated

[ ] Test error scenarios
    [ ] Network timeout
    [ ] Invalid email
    [ ] Missing order
    [ ] Duplicate payment

[ ] Test security
    [ ] Verify webhook signature validation
    [ ] Check that secret key is not exposed
    [ ] Verify HTTPS is used
```

---

## 10. Production Deployment

### 10.1 Pre-Production Checklist

```
[ ] Use production Paystack credentials (not test keys)
[ ] Enable HTTPS/TLS on all payment endpoints
[ ] Set PAYSTACK_CALLBACK_URL to production domain
[ ] Configure webhook URL in Paystack dashboard
[ ] Set up error logging and monitoring
[ ] Test with real transactions (small amounts)
[ ] Set up payment settlement account
[ ] Create runbooks for failed transactions
[ ] Train support team on payment issues
[ ] Test rollback procedures
```

### 10.2 Environment Variables

```bash
# .env.production
PAYSTACK_PUBLIC_KEY=pk_live_your_production_public_key
PAYSTACK_SECRET_KEY=sk_live_your_production_secret_key
PAYSTACK_CALLBACK_URL=https://yourdomain.com/payment/paystack-callback
PAYSTACK_WEBHOOK_SECRET=your_webhook_secret_from_paystack
DATABASE_URL=your_production_database_url
```

### 10.3 Deployment Commands

```bash
# 1. Update dependencies
pip install -r requirements.txt

# 2. Run migrations
flask db upgrade

# 3. Restart application
systemctl restart yourapplication

# 4. Verify webhook endpoint
curl -I https://yourdomain.com/payment/webhook

# 5. Test with small transaction
# (Use Paystack dashboard test tools)
```

---

## 11. Monitoring & Debugging

### 11.1 Key Metrics to Monitor

```python
# Create a monitoring dashboard
- Payment success rate
- Average transaction time
- Failed payment reasons
- Revenue by payment method
- Webhook processing time
- Payment retry success rate
```

### 11.2 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Webhook not firing | Webhook URL not set | Go to Paystack Settings → Webhooks, add URL |
| Invalid signature | Wrong webhook secret | Ensure PAYSTACK_WEBHOOK_SECRET matches |
| Payment timeout | Network delay | Implement retry logic with exponential backoff |
| Duplicate charges | Webhook retry | Use idempotent payment processing |
| Missing records | DB connection issue | Check database logs |

### 11.3 Logging Setup

```python
# Add to your app initialization
import logging

logging.basicConfig(
    filename='logs/payments.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

payment_logger = logging.getLogger('payments')
```

---

## 12. File Structure

```
project_root/
├── payments/
│   ├── __init__.py
│   └── paystack_gateway.py      # Paystack service
├── routes/
│   └── payments.py              # Payment endpoints
├── templates/
│   ├── checkout.html            # Checkout page
│   ├── payment_status.html      # Status page
│   └── payment_history.html     # History page
├── tests/
│   └── test_paystack.py         # Unit tests
├── logs/
│   └── payments.log             # Payment logs
├── models.py                    # Database models
├── config.py                    # Configuration
├── app.py                       # Flask app
└── requirements.txt
```

---

## 13. Implementation Timeline

### Week 1-2: Setup & Configuration
- [ ] Register with Paystack
- [ ] Create `.env` with credentials
- [ ] Update `config.py`
- [ ] Create database models
- [ ] Run migrations

### Week 3: Gateway Integration
- [ ] Implement `PaystackGateway` class
- [ ] Create payment routes
- [ ] Implement webhook handler
- [ ] Set up logging

### Week 4: Frontend Integration
- [ ] Create checkout template
- [ ] Create payment status template
- [ ] Create payment history template
- [ ] Add JavaScript for payment flow

### Week 5: Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing with sandbox
- [ ] Load testing

### Week 6: Deployment
- [ ] Production credentials
- [ ] Set webhook URL
- [ ] Final testing
- [ ] Go live

---

## 14. Troubleshooting

### Webhook not Receiving Events?

1. Check Paystack dashboard for webhook URL
2. Verify HTTPS is enabled
3. Test webhook using Paystack test tools
4. Check server logs for errors
5. Ensure firewall allows Paystack IPs

### Payment Not Updating in Database?

1. Verify webhook signature validation
2. Check database connection
3. Review transaction logs
4. Ensure `db.session.commit()` is called
5. Check for transaction conflicts

### Card Payment Declined?

1. Use Paystack test cards (see test cards list)
2. Check card expiry in test data
3. Verify amount is correct
4. Check API key is correct
5. Review Paystack dashboard for declined reason

---

## 15. Next Steps

1. **Create `.env` file** with Paystack credentials
2. **Run database migrations** to create payment tables
3. **Test payment gateway** with sandbox credentials
4. **Implement checkout flow** with frontend
5. **Test complete payment workflow**
6. **Deploy to production** with live credentials

---

## Additional Resources

- Paystack Documentation: https://paystack.com/docs
- Paystack API Reference: https://paystack.com/docs/api
- Test Cards: https://paystack.com/docs/payments/payment-channels/test-payments/
- Webhook Events: https://paystack.com/docs/webhooks/
- Support: support@paystack.com

---

## Summary

**Paystack Integration provides:**
- ✅ Single integration for all payment methods
- ✅ PCI DSS compliance built-in
- ✅ Reliable webhook infrastructure
- ✅ Easy testing with sandbox
- ✅ Fast settlement times
- ✅ Developer-friendly API

**Your implementation will handle:**
- Payment initialization and verification
- Webhook reception and processing
- Payment status tracking
- Order confirmation
- Transaction audit logging

Start with **Week 1-2** setup, then progress through testing to production deployment.
