# Paystack Integration - Complete Example

This file shows a working example of how all components fit together.

## Example 1: Adding Models to Your Existing models.py

```python
# models.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model - EXISTING"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    # ... other fields ...


class Order(db.Model):
    """Order model - UPDATE with payment fields"""
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Existing fields
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, shipped, delivered
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ADD THESE NEW FIELDS FOR PAYMENT:
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, failed
    paystack_reference = db.Column(db.String(100))  # Link to payment
    
    # Relationship
    user = db.relationship('User', backref='orders')


# ======================== ADD THESE NEW CLASSES ========================

class Payment(db.Model):
    """Paystack Payment Records - NEW"""
    __tablename__ = 'payment'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Order Reference
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    
    # Customer Information
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20))
    
    # Payment Details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='GHS')
    
    # Paystack References
    paystack_reference = db.Column(db.String(100), unique=True, nullable=False)
    paystack_authorization_code = db.Column(db.String(100))
    paystack_customer_id = db.Column(db.Integer)
    
    # Payment Method
    payment_method = db.Column(db.String(50))  # card, mobile_money, bank_transfer, ussd
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, success, failed
    status_reason = db.Column(db.String(255))
    
    # Timestamps
    initiated_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    order = db.relationship('Order', backref='payment_record')
    logs = db.relationship('PaymentLog', backref='payment', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.paystack_reference}>'
    
    def is_successful(self):
        return self.status == 'success'


class PaymentLog(db.Model):
    """Payment Audit Log - NEW"""
    __tablename__ = 'payment_log'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PaymentLog {self.id} - {self.action}>'
```

---

## Example 2: Configuration in config.py

```python
# config.py

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base Configuration"""
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///digitalhome.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Paystack Configuration - ADD THESE
    PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
    PAYSTACK_CALLBACK_URL = os.getenv('PAYSTACK_CALLBACK_URL')
    PAYSTACK_WEBHOOK_SECRET = os.getenv('PAYSTACK_WEBHOOK_SECRET')
    
    # Payment Settings
    PAYMENT_CURRENCY = 'GHS'
    PAYMENT_TIMEOUT = 3600  # 1 hour


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

## Example 3: Registering Blueprint in app.py

```python
# app.py

from flask import Flask
from flask_login import LoginManager
from models import db
from config import config


def create_app(config_name='development'):
    """Application factory"""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.admin import admin_bp
    from routes.payments import payment_bp  # ADD THIS
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_bp)  # ADD THIS
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True)
```

---

## Example 4: .env File Setup

```bash
# .env

# Database
DATABASE_URL=sqlite:///digitalhome.db

# Secret Key
SECRET_KEY=your-secret-key-here

# Paystack - Get these from https://dashboard.paystack.com
# Use test keys for development
PAYSTACK_PUBLIC_KEY=pk_test_your_public_key_here
PAYSTACK_SECRET_KEY=sk_test_your_secret_key_here
PAYSTACK_CALLBACK_URL=http://localhost:5000/payment/paystack-callback
PAYSTACK_WEBHOOK_SECRET=your_webhook_secret_here

# For production, replace with live keys:
# PAYSTACK_PUBLIC_KEY=pk_live_your_live_public_key
# PAYSTACK_SECRET_KEY=sk_live_your_live_secret_key
# PAYSTACK_CALLBACK_URL=https://yourdomain.com/payment/paystack-callback
```

---

## Example 5: Update Checkout Template

```html
<!-- templates/checkout.html -->

{% extends 'base.html' %}

{% block content %}
<div class="container mt-5">
    <h2>Checkout</h2>
    
    {% if order %}
    <div class="row">
        <!-- Order Summary -->
        <div class="col-md-8">
            <div class="card mb-4">
                <div class="card-header">
                    <h5>Order Summary</h5>
                </div>
                <div class="card-body">
                    <table class="table table-sm">
                        {% for item in order.items %}
                        <tr>
                            <td>{{ item.product_name }}</td>
                            <td>x{{ item.quantity }}</td>
                            <td class="text-right">GHS {{ "%.2f"|format(item.total) }}</td>
                        </tr>
                        {% endfor %}
                        <tr class="border-top">
                            <td colspan="2"><strong>Total:</strong></td>
                            <td class="text-right"><strong>GHS {{ "%.2f"|format(order.total_amount) }}</strong></td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <!-- Payment Section -->
            <div class="card">
                <div class="card-header">
                    <h5>Payment Method</h5>
                </div>
                <div class="card-body">
                    <p class="text-muted">Select your preferred payment method:</p>
                    
                    <div id="payment-methods" class="mb-4">
                        <div class="custom-control custom-radio mb-3">
                            <input type="radio" id="method_card" name="payment_method" value="card" class="custom-control-input" checked>
                            <label class="custom-control-label" for="method_card">
                                <i class="fas fa-credit-card"></i> Credit/Debit Card
                            </label>
                        </div>
                        
                        <div class="custom-control custom-radio mb-3">
                            <input type="radio" id="method_momo" name="payment_method" value="mobile_money" class="custom-control-input">
                            <label class="custom-control-label" for="method_momo">
                                <i class="fas fa-mobile-alt"></i> Mobile Money (MTN, Vodafone, AirtelTigo)
                            </label>
                        </div>
                        
                        <div class="custom-control custom-radio mb-3">
                            <input type="radio" id="method_bank" name="payment_method" value="bank_transfer" class="custom-control-input">
                            <label class="custom-control-label" for="method_bank">
                                <i class="fas fa-university"></i> Bank Transfer
                            </label>
                        </div>
                        
                        <div class="custom-control custom-radio mb-3">
                            <input type="radio" id="method_ussd" name="payment_method" value="ussd" class="custom-control-input">
                            <label class="custom-control-label" for="method_ussd">
                                <i class="fas fa-phone"></i> USSD
                            </label>
                        </div>
                    </div>
                    
                    <button id="pay-btn" class="btn btn-primary btn-block btn-lg">
                        <i class="fas fa-lock"></i> Proceed to Payment
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Delivery Info Sidebar -->
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5>Delivery Information</h5>
                </div>
                <div class="card-body">
                    <p><strong>Name:</strong> {{ current_user.first_name }} {{ current_user.last_name }}</p>
                    <p><strong>Email:</strong> {{ current_user.email }}</p>
                    <p><strong>Phone:</strong> {{ current_user.phone }}</p>
                    <p><strong>Address:</strong> {{ order.shipping_address }}</p>
                </div>
            </div>
        </div>
    </div>
    {% else %}
    <div class="alert alert-warning">No pending order found. <a href="{{ url_for('main.shop') }}">Continue shopping</a></div>
    {% endif %}
</div>

<!-- Loading Overlay -->
<div id="loading-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 8px; text-align: center;">
        <div class="spinner-border mb-3" role="status">
            <span class="sr-only">Loading...</span>
        </div>
        <p>Processing your payment...</p>
    </div>
</div>

{% endblock %}

{% block scripts %}
<script>
document.getElementById('pay-btn').addEventListener('click', function(e) {
    e.preventDefault();
    
    const method = document.querySelector('input[name="payment_method"]:checked').value;
    const loading = document.getElementById('loading-overlay');
    
    // Show loading
    loading.style.display = 'block';
    
    // Send payment initiation request
    fetch('{{ url_for("payments.initiate_payment") }}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            payment_method: method
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Redirect to Paystack checkout
            window.location.href = data.authorization_url;
        } else {
            loading.style.display = 'none';
            alert('Error: ' + (data.error || 'Payment initialization failed'));
        }
    })
    .catch(error => {
        loading.style.display = 'none';
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
});
</script>
{% endblock %}
```

---

## Example 6: Simple Usage in Python

```python
# Example usage in your code

from models import db, Order, Payment, PaymentLog
from payments.paystack_gateway import PaystackGateway
from datetime import datetime
import uuid

# Create payment gateway instance
gateway = PaystackGateway()

# Example: Initiate payment
def process_payment(user, order):
    """Process payment for an order"""
    
    # Create unique reference
    reference = f"ORDER-{order.id}-{uuid.uuid4().hex[:8]}"
    
    # Initialize payment
    response = gateway.initialize_payment(
        email=user.email,
        amount=order.total_amount,
        reference=reference,
        metadata={
            'order_id': order.id,
            'user_id': user.id
        }
    )
    
    if response['success']:
        # Create payment record
        payment = Payment(
            order_id=order.id,
            customer_email=user.email,
            amount=order.total_amount,
            paystack_reference=reference,
            status='pending'
        )
        db.session.add(payment)
        
        # Log the action
        log = PaymentLog(
            action='initiated',
            details=f'Payment initiated for order {order.id}'
        )
        payment.logs.append(log)
        
        db.session.commit()
        
        return {
            'success': True,
            'authorization_url': response['authorization_url'],
            'reference': reference
        }
    else:
        return {
            'success': False,
            'error': response.get('error', 'Payment initialization failed')
        }


# Example: Verify payment
def verify_and_confirm_payment(reference):
    """Verify payment and update order status"""
    
    # Get payment record
    payment = Payment.query.filter_by(paystack_reference=reference).first()
    
    if not payment:
        return {'success': False, 'error': 'Payment not found'}
    
    # Verify with Paystack
    verification = gateway.verify_payment(reference)
    
    if verification['success'] and verification['status'] == 'success':
        # Update payment
        payment.status = 'success'
        payment.completed_at = datetime.utcnow()
        payment.payment_method = verification.get('payment_method')
        
        # Update order
        order = payment.order
        order.status = 'confirmed'
        order.payment_status = 'paid'
        
        # Log success
        log = PaymentLog(
            action='verified',
            details='Payment verified successfully'
        )
        payment.logs.append(log)
        
        db.session.commit()
        
        return {'success': True, 'message': 'Payment confirmed'}
    else:
        payment.status = 'failed'
        payment.status_reason = verification.get('error', 'Verification failed')
        db.session.commit()
        
        return {'success': False, 'error': verification.get('error')}


# Example: Get payment history
def get_user_payment_history(user_id):
    """Get all payments for a user"""
    
    payments = db.session.query(Payment).join(Order).filter(
        Order.user_id == user_id
    ).order_by(Payment.initiated_at.desc()).all()
    
    return payments


# Example: Get payment statistics
def get_payment_statistics():
    """Get payment statistics"""
    
    from sqlalchemy import func
    
    total_payments = db.session.query(func.count(Payment.id)).scalar()
    successful = db.session.query(func.count(Payment.id)).filter_by(status='success').scalar()
    failed = db.session.query(func.count(Payment.id)).filter_by(status='failed').scalar()
    pending = db.session.query(func.count(Payment.id)).filter_by(status='pending').scalar()
    
    total_amount = db.session.query(func.sum(Payment.amount)).filter_by(status='success').scalar()
    
    return {
        'total_payments': total_payments,
        'successful': successful,
        'failed': failed,
        'pending': pending,
        'success_rate': (successful / total_payments * 100) if total_payments > 0 else 0,
        'total_revenue': total_amount or 0
    }
```

---

## Example 7: Testing

```python
# tests/test_paystack_integration.py

import unittest
from unittest.mock import patch, MagicMock
from app import create_app
from models import db, Payment, Order, User, PaymentLog


class PaystackIntegrationTestCase(unittest.TestCase):
    """Test Paystack integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test user
            user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                phone='024XXXXXXX'
            )
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id
            
            # Create test order
            order = Order(
                user_id=user.id,
                total_amount=100.50,
                status='pending'
            )
            db.session.add(order)
            db.session.commit()
            self.order_id = order.id
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    @patch('payments.paystack_gateway.requests.post')
    def test_initiate_payment(self, mock_post):
        """Test payment initiation"""
        with self.app.app_context():
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'status': True,
                'data': {
                    'authorization_url': 'https://checkout.paystack.com/test',
                    'access_code': 'test_code',
                    'reference': 'test_ref_123'
                }
            }
            mock_post.return_value = mock_response
            
            from payments.paystack_gateway import PaystackGateway
            gateway = PaystackGateway()
            
            result = gateway.initialize_payment(
                email='test@example.com',
                amount=100.50,
                reference='test_ref_123'
            )
            
            self.assertTrue(result['success'])
            self.assertIn('authorization_url', result)
    
    @patch('payments.paystack_gateway.requests.get')
    def test_verify_payment(self, mock_get):
        """Test payment verification"""
        with self.app.app_context():
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'status': True,
                'data': {
                    'status': 'success',
                    'amount': 10050,  # in kobo
                    'reference': 'test_ref_123',
                    'customer': {'email': 'test@example.com'},
                    'authorization': {'authorization_code': 'auth_123'},
                    'paid_at': '2025-01-01T12:00:00Z'
                }
            }
            mock_get.return_value = mock_response
            
            from payments.paystack_gateway import PaystackGateway
            gateway = PaystackGateway()
            
            result = gateway.verify_payment('test_ref_123')
            
            self.assertTrue(result['success'])
            self.assertEqual(result['amount'], 100.50)
            self.assertEqual(result['status'], 'success')
    
    def test_payment_model(self):
        """Test Payment model"""
        with self.app.app_context():
            payment = Payment(
                order_id=self.order_id,
                customer_email='test@example.com',
                amount=100.50,
                paystack_reference='test_ref_123',
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            
            retrieved = Payment.query.filter_by(
                paystack_reference='test_ref_123'
            ).first()
            
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.amount, 100.50)
            self.assertEqual(retrieved.status, 'pending')
    
    def test_payment_log_model(self):
        """Test PaymentLog model"""
        with self.app.app_context():
            payment = Payment(
                order_id=self.order_id,
                customer_email='test@example.com',
                amount=100.50,
                paystack_reference='test_ref_123',
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            
            log = PaymentLog(
                payment_id=payment.id,
                action='initiated',
                details='Payment initiated'
            )
            db.session.add(log)
            db.session.commit()
            
            retrieved_log = PaymentLog.query.filter_by(
                action='initiated'
            ).first()
            
            self.assertIsNotNone(retrieved_log)
            self.assertEqual(retrieved_log.action, 'initiated')


if __name__ == '__main__':
    unittest.main()
```

---

## Run This to Verify Everything

```bash
# 1. Check models import
python -c "from models import Payment, PaymentLog; print('✓ Models OK')"

# 2. Check gateway import
python -c "from payments.paystack_gateway import PaystackGateway; print('✓ Gateway OK')"

# 3. Check routes import
python -c "from routes.payments import payment_bp; print('✓ Routes OK')"

# 4. Check app creation
python -c "from app import create_app; app = create_app(); print('✓ App OK')"

# 5. Check database
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all(); print('✓ Database OK')"

# 6. Run tests
python -m pytest tests/test_paystack_integration.py -v
```

---

That's everything you need to integrate Paystack! Follow the examples and you'll have a working payment system.
