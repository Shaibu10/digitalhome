"""Payment processing routes"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

# These imports should be from your actual project structure
# Adjust based on your models location
try:
    from models import db, Payment, PaymentLog, Order
    from payments.paystack_gateway import PaystackGateway
except ImportError:
    logger.error("Failed to import models or PaystackGateway")


payment_bp = Blueprint('payments', __name__, url_prefix='/payment')
paystack = None


def get_paystack():
    """Get Paystack gateway instance"""
    global paystack
    if paystack is None:
        paystack = PaystackGateway()
    return paystack


@payment_bp.route('/initiate', methods=['POST'])
@login_required
def initiate_payment():
    """
    Initiate Paystack payment
    
    Request body (JSON):
        {
            'payment_method': str (optional, for future use)
        }
    
    Response:
        {
            'success': bool,
            'authorization_url': str,
            'reference': str,
            'access_code': str,
            'error': str (if failed)
        }
    """
    
    try:
        data = request.get_json() or {}
        
        # Get user's pending order
        order = Order.query.filter_by(
            user_id=current_user.id,
            status='pending'
        ).first()
        
        if not order:
            logger.warning(f'No pending order for user {current_user.id}')
            return jsonify({
                'success': False,
                'error': 'No pending order found'
            }), 404
        
        if order.total_amount <= 0:
            logger.warning(f'Invalid order amount: {order.total_amount}')
            return jsonify({
                'success': False,
                'error': 'Invalid order amount'
            }), 400
        
        # Generate unique reference
        paystack_reference = f"ORDER-{order.id}-{uuid.uuid4().hex[:8]}"
        
        # Metadata to store with payment
        metadata = {
            'order_id': order.id,
            'user_id': current_user.id,
            'user_email': current_user.email
        }
        
        # Initialize payment with Paystack
        gateway = get_paystack()
        paystack_response = gateway.initialize_payment(
            email=current_user.email,
            amount=order.total_amount,
            reference=paystack_reference,
            metadata=metadata
        )
        
        if not paystack_response['success']:
            error_msg = paystack_response.get('error', 'Payment initialization failed')
            logger.error(f'Payment initialization failed: {error_msg}')
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            customer_email=current_user.email,
            customer_phone=getattr(current_user, 'phone', None),
            amount=order.total_amount,
            paystack_reference=paystack_reference,
            status='pending'
        )
        
        db.session.add(payment)
        
        # Log payment initiation
        payment_log = PaymentLog(
            action='initiated',
            details=f'Payment initiated with reference: {paystack_reference}'
        )
        payment.logs.append(payment_log)
        
        db.session.commit()
        
        logger.info(f'Payment initiated: {paystack_reference} for order {order.id}')
        
        return jsonify({
            'success': True,
            'authorization_url': paystack_response['authorization_url'],
            'reference': paystack_reference,
            'access_code': paystack_response['access_code']
        }), 200
    
    except Exception as e:
        logger.error(f'Payment initiation error: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Payment initialization failed'
        }), 500


@payment_bp.route('/verify/<reference>', methods=['GET'])
@login_required
def verify_payment(reference):
    """
    Verify payment status
    
    Args:
        reference (str): Payment reference
    
    Response:
        {
            'success': bool,
            'status': str (success, failed, pending),
            'order_id': int,
            'amount': float,
            'error': str (if failed)
        }
    """
    
    try:
        # Verify with Paystack
        gateway = get_paystack()
        verification_result = gateway.verify_payment(reference)
        
        if not verification_result['success']:
            error_msg = verification_result.get('error', 'Verification failed')
            logger.warning(f'Payment verification failed: {error_msg}')
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Get payment record
        payment = Payment.query.filter_by(
            paystack_reference=reference
        ).first()
        
        if not payment:
            logger.warning(f'Payment record not found: {reference}')
            return jsonify({
                'success': False,
                'error': 'Payment record not found'
            }), 404
        
        # Update payment record if successful
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
                action='verified',
                details=f'Payment verified successfully via API'
            )
            payment.logs.append(payment_log)
            
            db.session.commit()
            
            logger.info(f'Payment verified successfully: {reference}')
            
            # Send confirmation email would go here
            # send_payment_confirmation_email(order)
        
        else:
            payment.status = 'failed'
            payment.status_reason = verification_result.get('error', 'Verification failed')
            db.session.commit()
            logger.warning(f'Payment verification returned failed status: {reference}')
        
        return jsonify({
            'success': True,
            'status': payment.status,
            'order_id': payment.order_id,
            'amount': payment.amount
        }), 200
    
    except Exception as e:
        logger.error(f'Payment verification error: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Verification failed'
        }), 500


@payment_bp.route('/paystack-callback', methods=['GET', 'POST'])
def paystack_callback():
    """
    Handle Paystack payment callback
    
    This is called by Paystack after payment attempt
    """
    
    try:
        if request.method == 'GET':
            reference = request.args.get('reference')
            
            if not reference:
                logger.warning('Callback received without reference')
                return redirect(url_for('main.checkout', error='No reference provided'))
            
            # Verify payment
            gateway = get_paystack()
            verification_result = gateway.verify_payment(reference)
            
            if verification_result['success'] and verification_result['status'] == 'success':
                logger.info(f'Callback redirecting to confirmation: {reference}')
                return redirect(url_for('main.payment_confirmed', reference=reference))
            else:
                error_msg = verification_result.get('error', 'Payment verification failed')
                logger.warning(f'Callback verification failed: {error_msg}')
                return redirect(url_for('main.checkout', error=error_msg))
        
        return jsonify({'success': False}), 400
    
    except Exception as e:
        logger.error(f'Callback error: {str(e)}', exc_info=True)
        return redirect(url_for('main.checkout', error='An error occurred'))


@payment_bp.route('/webhook', methods=['POST'])
def paystack_webhook():
    """
    Paystack webhook endpoint for payment confirmations
    
    Configure this URL in Paystack dashboard:
    Settings → API Keys & Webhooks → Webhooks
    URL: https://yourdomain.com/payment/webhook
    
    Events to enable:
    - charge.success
    - charge.failed
    """
    
    try:
        # Verify webhook signature
        signature = request.headers.get('X-Paystack-Signature', '')
        
        if not signature:
            logger.warning('Webhook received without signature')
            return jsonify({'success': False}), 401
        
        # Verify signature
        gateway = get_paystack()
        if not gateway.verify_webhook_signature(request.data, signature):
            logger.warning('Invalid webhook signature')
            return jsonify({'success': False}), 401
        
        data = request.get_json() or {}
        
        if data.get('event') == 'charge.success':
            event_data = data.get('data', {})
            reference = event_data.get('reference')
            
            logger.info(f'Webhook: charge.success for {reference}')
            
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
                    action='webhook_confirmed',
                    details=f'Payment confirmed via webhook'
                )
                payment.logs.append(payment_log)
                db.session.commit()
                
                logger.info(f'Payment {reference} confirmed via webhook')
                
                # Send confirmation email would go here
                # send_payment_confirmation_email(order)
        
        elif data.get('event') == 'charge.failed':
            event_data = data.get('data', {})
            reference = event_data.get('reference')
            
            logger.warning(f'Webhook: charge.failed for {reference}')
            
            payment = Payment.query.filter_by(
                paystack_reference=reference
            ).first()
            
            if payment:
                payment.status = 'failed'
                payment.status_reason = event_data.get('gateway_response', 'Payment failed')
                
                payment_log = PaymentLog(
                    action='webhook_failed',
                    details=f'Payment failed: {event_data.get("gateway_response")}'
                )
                payment.logs.append(payment_log)
                db.session.commit()
                
                logger.warning(f'Payment {reference} failed via webhook')
        
        return jsonify({'success': True}), 200
    
    except Exception as e:
        logger.error(f'Webhook error: {str(e)}', exc_info=True)
        db.session.rollback()
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
        logger.error(f'Payment history error: {str(e)}', exc_info=True)
        return redirect(url_for('main.index'))


@payment_bp.route('/status/<int:payment_id>', methods=['GET'])
@login_required
def payment_status(payment_id):
    """Get payment status"""
    
    try:
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({'success': False, 'error': 'Payment not found'}), 404
        
        # Verify user owns this payment
        if payment.order.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'status': payment.status,
            'amount': payment.amount,
            'payment_method': payment.payment_method,
            'completed_at': payment.completed_at.isoformat() if payment.completed_at else None
        }), 200
    
    except Exception as e:
        logger.error(f'Payment status error: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': 'Error fetching payment status'}), 500
