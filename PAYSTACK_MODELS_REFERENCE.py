"""
Paystack Payment Models - Add these to your models.py file

This file shows the exact models to add to your existing models.py.
Simply copy the Payment and PaymentLog classes and add them to your models.py file.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Assuming db is already initialized in your project
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

# If you're adding to existing models.py, just add these two classes:


class Payment(db.Model):
    """Paystack Payment Records
    
    Stores information about all payments processed through Paystack.
    Links to Order and User.
    """
    __tablename__ = 'payment'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Order Reference
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    
    # Customer Information
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20))
    
    # Payment Details
    amount = db.Column(db.Float, nullable=False)  # Amount in GHS
    currency = db.Column(db.String(3), default='GHS')
    
    # Paystack References
    paystack_reference = db.Column(db.String(100), unique=True, nullable=False)
    paystack_authorization_code = db.Column(db.String(100))
    paystack_customer_id = db.Column(db.Integer)
    
    # Payment Method (set after payment completes)
    payment_method = db.Column(db.String(50))  # 'card', 'mobile_money', 'bank_transfer', 'ussd'
    
    # Status Tracking
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
    logs = db.relationship('PaymentLog', backref='payment', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.paystack_reference}>'
    
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == 'success'
    
    def is_pending(self):
        """Check if payment is pending"""
        return self.status == 'pending'
    
    def is_failed(self):
        """Check if payment failed"""
        return self.status == 'failed'
    
    def time_since_initiated(self):
        """Get seconds since payment was initiated"""
        return (datetime.utcnow() - self.initiated_at).total_seconds()


class PaymentLog(db.Model):
    """Payment Transaction Audit Log
    
    Stores audit trail of all payment actions for debugging and compliance.
    Every payment action is logged with timestamp and details.
    """
    __tablename__ = 'payment_log'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    
    # Action Details
    action = db.Column(db.String(100), nullable=False)  # initiated, verified, confirmed, failed, webhook_confirmed, webhook_failed
    details = db.Column(db.Text)  # Detailed information (can store JSON)
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PaymentLog {self.id} - {self.action}>'


# ============================================================================
# ALSO UPDATE YOUR ORDER MODEL TO INCLUDE THESE FIELDS IF NOT PRESENT
# ============================================================================
# In your existing Order model, add these columns if not already present:
#
# class Order(db.Model):
#     # ... existing fields ...
#     
#     # Add these payment-related fields:
#     payment_status = db.Column(
#         db.String(50),
#         default='pending'
#     )  # pending, paid, failed - Status of payment
#     
#     paystack_reference = db.Column(db.String(100))  # Link to Paystack payment reference
#     
#     # ... rest of model ...


# ============================================================================
# MIGRATION COMMAND
# ============================================================================
# After adding these models to models.py, run:
#
#   flask db migrate -m "Add Paystack payment models"
#   flask db upgrade
#
# This will create the payment and payment_log tables in your database.


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
# Create a payment record
payment = Payment(
    order_id=123,
    customer_email='user@example.com',
    amount=100.50,
    paystack_reference='ORDER-123-abc123',
    status='pending'
)
db.session.add(payment)
db.session.commit()

# Add audit log
log = PaymentLog(
    payment_id=payment.id,
    action='initiated',
    details='Payment initiated with Paystack'
)
payment.logs.append(log)
db.session.commit()

# Query payments for an order
payments = Payment.query.filter_by(order_id=123).all()

# Query successful payments
successful = Payment.query.filter_by(status='success').all()

# Get audit trail for a payment
payment = Payment.query.get(1)
for log in payment.logs:
    print(f"{log.timestamp}: {log.action} - {log.details}")

# Calculate payment success rate
from sqlalchemy import func
total = db.session.query(func.count(Payment.id)).scalar()
successful = db.session.query(func.count(Payment.id)).filter_by(status='success').scalar()
success_rate = (successful / total * 100) if total > 0 else 0
print(f"Payment success rate: {success_rate:.2f}%")
"""
