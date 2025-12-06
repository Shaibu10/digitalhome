"""Paystack Payment Gateway Integration"""

import requests
import hmac
import hashlib
import logging
from flask import current_app
from datetime import datetime

logger = logging.getLogger(__name__)


class PaystackGateway:
    """Paystack Payment Gateway Service
    
    Handles all payment processing through Paystack API.
    Supports: Cards, Mobile Money, Bank Transfer, USSD
    """
    
    BASE_URL = 'https://api.paystack.co'
    
    def __init__(self):
        """Initialize Paystack gateway with API credentials"""
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
                {
                    'success': bool,
                    'authorization_url': str,
                    'access_code': str,
                    'reference': str,
                    'error': str (if failed)
                }
        """
        
        # Convert amount to kobo (Paystack uses smallest currency unit)
        amount_kobo = int(amount * 100)
        
        payload = {
            'email': email,
            'amount': amount_kobo,
            'reference': reference,
            'callback_url': callback_url or current_app.config.get('PAYSTACK_CALLBACK_URL'),
        }
        
        if metadata:
            payload['metadata'] = metadata
        
        try:
            logger.info(f'Initializing payment for {email}, amount: {amount} GHS, ref: {reference}')
            
            response = requests.post(
                f'{self.BASE_URL}/transaction/initialize',
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                logger.info(f'Payment initialized successfully: {reference}')
                return {
                    'success': True,
                    'authorization_url': data['data']['authorization_url'],
                    'access_code': data['data']['access_code'],
                    'reference': data['data']['reference']
                }
            else:
                error_msg = data.get('message', 'Payment initialization failed')
                logger.warning(f'Payment initialization failed: {error_msg}')
                return {
                    'success': False,
                    'error': error_msg
                }
        
        except requests.exceptions.RequestException as e:
            error_msg = f'API connection failed: {str(e)}'
            logger.error(f'Payment initialization error: {error_msg}')
            return {
                'success': False,
                'error': error_msg
            }
    
    def verify_payment(self, reference):
        """
        Verify payment status with Paystack
        
        Args:
            reference (str): Payment reference to verify
        
        Returns:
            dict: Payment details and status
                {
                    'success': bool,
                    'status': str,
                    'amount': float,
                    'reference': str,
                    'customer_email': str,
                    'payment_method': str,
                    'authorization_code': str,
                    'timestamp': str,
                    'error': str (if failed)
                }
        """
        
        try:
            logger.info(f'Verifying payment: {reference}')
            
            response = requests.get(
                f'{self.BASE_URL}/transaction/verify/{reference}',
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') and data['data']['status'] == 'success':
                payment_data = data['data']
                logger.info(f'Payment verified successfully: {reference}')
                
                return {
                    'success': True,
                    'status': 'success',
                    'amount': payment_data['amount'] / 100,  # Convert from kobo
                    'reference': payment_data['reference'],
                    'customer_email': payment_data['customer']['email'],
                    'authorization': payment_data.get('authorization', {}),
                    'payment_method': self._extract_payment_method(payment_data),
                    'authorization_code': payment_data['authorization'].get('authorization_code'),
                    'timestamp': payment_data['paid_at']
                }
            else:
                status = data['data'].get('status', 'unknown') if data.get('data') else 'unknown'
                error_msg = f'Payment status: {status}'
                logger.warning(f'Payment verification failed: {error_msg}')
                
                return {
                    'success': False,
                    'status': status,
                    'error': error_msg
                }
        
        except requests.exceptions.RequestException as e:
            error_msg = f'Verification failed: {str(e)}'
            logger.error(f'Payment verification error: {error_msg}')
            return {
                'success': False,
                'error': error_msg
            }
    
    def _extract_payment_method(self, transaction_data):
        """Extract payment method from transaction data
        
        Args:
            transaction_data (dict): Transaction data from Paystack
        
        Returns:
            str: Payment method identifier
        """
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
        
        try:
            # Use webhook secret if available, otherwise use secret key
            secret = current_app.config.get('PAYSTACK_WEBHOOK_SECRET') or \
                     current_app.config['PAYSTACK_SECRET_KEY']
            
            expected_signature = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha512
            ).hexdigest()
            
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if not is_valid:
                logger.warning(f'Invalid webhook signature: {signature[:20]}...')
            
            return is_valid
        
        except Exception as e:
            logger.error(f'Webhook signature verification error: {str(e)}')
            return False
    
    def get_balance(self):
        """Get account balance
        
        Returns:
            dict: Account balance in GHS
                {
                    'success': bool,
                    'balance': float,
                    'error': str (if failed)
                }
        """
        try:
            response = requests.get(
                f'{self.BASE_URL}/balance',
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                balance = data['data'][0]['balance'] / 100  # Convert from kobo
                logger.info(f'Account balance retrieved: {balance} GHS')
                return {
                    'success': True,
                    'balance': balance
                }
            else:
                error_msg = data.get('message', 'Balance fetch failed')
                logger.warning(f'Balance fetch failed: {error_msg}')
                return {
                    'success': False,
                    'error': error_msg
                }
        
        except requests.exceptions.RequestException as e:
            error_msg = f'Balance fetch failed: {str(e)}'
            logger.error(f'Balance fetch error: {error_msg}')
            return {
                'success': False,
                'error': error_msg
            }
    
    def create_customer(self, email, first_name, last_name, phone=None):
        """Create or get customer
        
        Args:
            email (str): Customer email
            first_name (str): Customer first name
            last_name (str): Customer last name
            phone (str): Customer phone number
        
        Returns:
            dict: Customer ID from Paystack
                {
                    'success': bool,
                    'customer_id': str,
                    'error': str (if failed)
                }
        """
        payload = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name
        }
        
        if phone:
            payload['phone'] = phone
        
        try:
            logger.info(f'Creating customer: {email}')
            
            response = requests.post(
                f'{self.BASE_URL}/customer',
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                customer_id = data['data']['customer_code']
                logger.info(f'Customer created: {customer_id}')
                return {
                    'success': True,
                    'customer_id': customer_id
                }
            else:
                error_msg = data.get('message', 'Customer creation failed')
                logger.warning(f'Customer creation failed: {error_msg}')
                return {
                    'success': False,
                    'error': error_msg
                }
        
        except requests.exceptions.RequestException as e:
            error_msg = f'Customer creation failed: {str(e)}'
            logger.error(f'Customer creation error: {error_msg}')
            return {
                'success': False,
                'error': error_msg
            }
    
    def list_transactions(self, limit=50, offset=0):
        """List transactions
        
        Args:
            limit (int): Number of transactions to fetch
            offset (int): Starting point
        
        Returns:
            dict: List of transactions
        """
        try:
            response = requests.get(
                f'{self.BASE_URL}/transaction?limit={limit}&offset={offset}',
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'transactions': data['data'],
                    'total': data['data'][0]['total'] if data['data'] else 0
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Failed to fetch transactions')
                }
        
        except requests.exceptions.RequestException as e:
            logger.error(f'Transaction list error: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
