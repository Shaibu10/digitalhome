import os
import requests
import json
import re
import uuid
from datetime import datetime, timedelta
from flask import current_app
from extensions import db
from models import SMSMessage, SMSCampaign, SMSTemplate, SMSLog, User, SMSBlacklist

class mNotifyService:
    """mNotify SMS service for sending SMS messages"""
    
    BASE_URL = "https://api.mnotify.com/api"
    
    # Class variable to cache the last known balance
    _cached_balance = None
    _cached_balance_timestamp = None
    
    def __init__(self):
        self.api_key = os.environ.get('MNOTIFY_API_KEY')
        self.sender_id = os.environ.get('MNOTIFY_SENDER_ID', 'DigitalHome')
        self.enabled = self.api_key is not None
        
        if self.enabled:
            print(f"✅ mNotify SMS service initialized (sender: {self.sender_id})")
        else:
            if os.environ.get('SHOW_SMS_WARNINGS', 'true').lower() == 'true':
                print("⚠️ SMS service disabled - using console logging for SMS")
    
    def send_sms(self, phone_number, message, priority='high'):
        """
        Send SMS via mNotify API
        
        Args:
            phone_number (str): Recipient phone number (e.g., '0241234567' or '+233241234567')
            message (str): SMS message content
            priority (str): Message priority (high/normal/low)
        
        Returns:
            dict: Response with status and details
        """
        if not phone_number:
            return {
                'status': 'error',
                'message': 'Phone number is required',
                'code': 'INVALID_PHONE'
            }
        
        # Validate phone number
        if not self._validate_phone_number(phone_number):
            return {
                'status': 'error',
                'message': 'Invalid phone number format',
                'code': 'INVALID_FORMAT'
            }
        
        # Fallback: log SMS to console if disabled
        if not self.enabled:
            print("=" * 50)
            print(f"📱 SMS WOULD BE SENT (mNotify not configured)")
            print(f"To: {phone_number}")
            print(f"Sender: {self.sender_id}")
            print(f"Message: {message}")
            print("=" * 50)
            return {
                'status': 'success',
                'message': 'SMS logged to console (mNotify disabled)',
                'message_id': f'LOCAL_TEST_{uuid.uuid4().hex[:12]}'
            }
        
        try:
            payload = {
                'recipient': [phone_number],
                'sender': self.sender_id,
                'message': message,
                'is_schedule': False
            }
            
            params = {'key': self.api_key}
            
            response = requests.post(
                f"{self.BASE_URL}/sms/quick",
                json=payload,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    message_id = result.get('summary', {}).get('_id', '')
                    credit_left = result.get('summary', {}).get('credit_left', 0)
                    
                    # Cache the balance from the response
                    if credit_left is not None:
                        mNotifyService._cached_balance = credit_left
                        mNotifyService._cached_balance_timestamp = datetime.now()
                    
                    print(f"✅ SMS sent to {phone_number}. Message ID: {message_id}, Credits left: {credit_left}")
                    return {
                        'status': 'success',
                        'message': f'SMS sent successfully',
                        'message_id': message_id,
                        'credits_left': credit_left,
                        'data': result.get('summary', {})
                    }
                else:
                    error_msg = result.get('message', 'Unknown error')
                    print(f"❌ Failed to send SMS to {phone_number}: {error_msg}")
                    return {
                        'status': 'error',
                        'message': error_msg,
                        'code': result.get('code', 'API_ERROR')
                    }
            else:
                error_text = response.text
                print(f"❌ SMS API error (Status {response.status_code}): {error_text}")
                return {
                    'status': 'error',
                    'message': f'API error: {response.status_code}',
                    'code': 'HTTP_ERROR'
                }
                
        except requests.exceptions.Timeout:
            print(f"❌ SMS request timeout for {phone_number}")
            return {
                'status': 'error',
                'message': 'Request timeout',
                'code': 'TIMEOUT'
            }
        except requests.exceptions.ConnectionError:
            print(f"❌ SMS connection error for {phone_number}")
            return {
                'status': 'error',
                'message': 'Connection error',
                'code': 'CONNECTION_ERROR'
            }
        except Exception as e:
            print(f"❌ Failed to send SMS to {phone_number}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'code': 'EXCEPTION'
            }
    
    def get_account_balance(self):
        """Get current account balance/credits
        
        Strategy: Since mNotify API doesn't have a dedicated balance endpoint,
        we extract and cache balance from actual SMS send responses.
        """
        if not self.enabled:
            # Return demo balance for development
            return {
                'status': 'success',
                'balance': 500,  # Demo balance
                'message': 'Demo Mode (Configure MNOTIFY_API_KEY for real balance)',
                'demo_mode': True
            }
        
        # If we have a cached balance, return it
        if mNotifyService._cached_balance is not None:
            timestamp = mNotifyService._cached_balance_timestamp
            # Show how fresh the cache is
            if timestamp:
                from datetime import datetime as dt
                age = (dt.now() - timestamp).total_seconds()
                if age < 60:
                    age_str = f"{int(age)}s ago"
                elif age < 3600:
                    age_str = f"{int(age/60)}m ago"
                else:
                    age_str = f"{int(age/3600)}h ago"
            else:
                age_str = "recently"
            
            try:
                from flask import current_app
                current_app.logger.info(f"✅ SMS Balance (cached {age_str}): {mNotifyService._cached_balance} credits")
            except:
                pass
            
            return {
                'status': 'success',
                'balance': mNotifyService._cached_balance,
                'message': f'Balance from last SMS ({age_str})',
                'cached': True,
                'cached_at': timestamp.isoformat() if timestamp else None
            }
        
        # No cached balance yet
        return {
            'status': 'error',
            'message': 'Balance not yet available - send an SMS to populate the cache',
            'code': 'NO_CACHED_BALANCE',
            'hint': 'The first SMS sent will load the balance from the API response'
        }
    
    @staticmethod
    def _validate_phone_number(phone_number):
        """Validate Ghana phone number format"""
        # Ghana format: +233XXXXXXXXX or 233XXXXXXXXX or 0XXXXXXXXX
        pattern = r'^(\+233|233|0)[0-9]{9}$'
        return re.match(pattern, phone_number) is not None
    
    @staticmethod
    def calculate_sms_parts(message_text):
        """Calculate how many SMS parts a message will use"""
        try:
            message_text.encode('ascii')
            # Pure ASCII: 160 chars per SMS
            return (len(message_text) + 159) // 160
        except UnicodeEncodeError:
            # Contains unicode: 70 chars per SMS
            return (len(message_text) + 69) // 70

# Global mNotify service instance
sms_service = mNotifyService()


class SMSManager:
    """Manager class for SMS operations with database tracking"""
    
    def __init__(self):
        self.api = mNotifyService()
    
    def send_single_sms(self, user_id, message, admin_id):
        """Send a single SMS to a specific user"""
        user = User.query.get(user_id)
        if not user or not user.phone_number:
            return {
                'success': False,
                'message': 'User not found or has no phone number'
            }
        
        response = self.api.send_sms(user.phone_number, message)
        
        if response.get('status') == 'success':
            # Create SMS message record
            sms_msg = SMSMessage(
                user_id=user_id,
                phone_number=user.phone_number,
                recipient_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
                content=message,
                character_count=len(message),
                sms_parts=self.api.calculate_sms_parts(message),
                mnotify_message_id=response.get('message_id', ''),
                status='sent',
                sent_at=datetime.utcnow()
            )
            db.session.add(sms_msg)
            
            # Log the action
            log = SMSLog(
                action='message_sent',
                action_type='message',
                admin_id=admin_id,
                message=f'Single SMS sent to {user.phone_number}',
                status='success',
                details=json.dumps({'message_id': response.get('message_id', '')})
            )
            db.session.add(log)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'SMS sent to {user.phone_number}',
                'message_id': sms_msg.id
            }
        else:
            return {
                'success': False,
                'message': response.get('message', 'Failed to send SMS'),
                'error_code': response.get('code', '')
            }
    
    def create_bulk_campaign(self, name, message, recipient_filter, filter_data, admin_id, 
                            template_id=None, require_confirmation=True, schedule_time=None):
        """Create a bulk SMS campaign"""
        
        # Get recipient list based on filter
        recipients = self._get_recipients_by_filter(recipient_filter, filter_data)
        
        campaign = SMSCampaign(
            name=name,
            custom_message=message if not template_id else None,
            template_id=template_id,
            recipient_filter=recipient_filter,
            filter_data=json.dumps(filter_data),
            recipient_count=len(recipients),
            created_by_id=admin_id,
            status='scheduled' if schedule_time else 'draft',
            scheduled_at=schedule_time,
            require_confirmation=require_confirmation
        )
        
        db.session.add(campaign)
        db.session.flush()
        
        # Create SMS message records for each recipient
        for user in recipients:
            if user.phone_number and not SMSBlacklist.is_blacklisted(user.phone_number):
                # Render message with template variables if using template
                if template_id:
                    template = SMSTemplate.query.get(template_id)
                    rendered_msg = template.render(
                        first_name=user.first_name or user.username,
                        last_name=user.last_name or '',
                        username=user.username,
                        user_id=user.id
                    )
                else:
                    rendered_msg = message
                
                sms_msg = SMSMessage(
                    campaign_id=campaign.id,
                    user_id=user.id,
                    phone_number=user.phone_number,
                    recipient_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
                    content=rendered_msg,
                    character_count=len(rendered_msg),
                    sms_parts=self.api.calculate_sms_parts(rendered_msg),
                    status='pending'
                )
                db.session.add(sms_msg)
        
        # Log campaign creation
        log = SMSLog(
            action='campaign_created',
            action_type='campaign',
            campaign_id=campaign.id,
            admin_id=admin_id,
            message=f'Campaign "{name}" created with {len(recipients)} recipients',
            status='success',
            details=json.dumps({
                'recipient_count': len(recipients),
                'filter': recipient_filter
            })
        )
        db.session.add(log)
        db.session.commit()
        
        return {
            'success': True,
            'campaign_id': campaign.id,
            'message': f'Campaign created with {len(recipients)} recipients',
            'recipient_count': len(recipients)
        }
    
    def send_campaign(self, campaign_id, admin_id):
        """Send a bulk SMS campaign"""
        campaign = SMSCampaign.query.get(campaign_id)
        
        if not campaign:
            return {'success': False, 'message': 'Campaign not found'}
        
        # Prevent re-sending: only draft campaigns can be sent
        if campaign.status != 'draft':
            return {'success': False, 'message': f'Campaign cannot be sent (status: {campaign.status}). Only draft campaigns can be sent.'}
        
        # Get pending messages
        messages = SMSMessage.query.filter_by(
            campaign_id=campaign_id,
            status='pending'
        ).all()
        
        if not messages:
            return {'success': False, 'message': 'No pending messages in campaign'}
        
        campaign.status = 'in_progress'
        campaign.started_at = datetime.utcnow()
        db.session.add(campaign)
        
        sent_count = 0
        failed_count = 0
        
        # Send messages in batches
        batch_size = campaign.batch_size or 100
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            
            for sms_msg in batch:
                response = self.api.send_sms(sms_msg.phone_number, sms_msg.content)
                
                if response.get('status') == 'success':
                    sms_msg.status = 'sent'
                    sms_msg.sent_at = datetime.utcnow()
                    sms_msg.mnotify_message_id = response.get('message_id', '')
                    sent_count += 1
                else:
                    sms_msg.status = 'failed'
                    sms_msg.failed_at = datetime.utcnow()
                    sms_msg.delivery_error = response.get('message', 'Unknown error')
                    failed_count += 1
                
                db.session.add(sms_msg)
        
        # Update campaign status
        campaign.status = 'completed'
        campaign.completed_at = datetime.utcnow()
        campaign.messages_sent = sent_count
        campaign.messages_failed = failed_count
        db.session.add(campaign)
        
        # Log campaign send
        log = SMSLog(
            action='campaign_sent',
            action_type='campaign',
            campaign_id=campaign.id,
            admin_id=admin_id,
            message=f'Campaign "{campaign.name}" sent: {sent_count} sent, {failed_count} failed',
            status='success' if failed_count == 0 else 'warning',
            details=json.dumps({
                'sent': sent_count,
                'failed': failed_count,
                'total': len(messages)
            })
        )
        db.session.add(log)
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Campaign sent: {sent_count} sent, {failed_count} failed',
            'sent': sent_count,
            'failed': failed_count
        }
    
    def retry_failed_messages(self, campaign_id, admin_id):
        """Retry failed messages in a campaign"""
        campaign = SMSCampaign.query.get(campaign_id)
        
        if not campaign:
            return {'success': False, 'message': 'Campaign not found'}
        
        # Get failed messages that can be retried
        failed_messages = SMSMessage.query.filter(
            SMSMessage.campaign_id == campaign_id,
            SMSMessage.status == 'failed',
            SMSMessage.retry_count < SMSMessage.max_retries
        ).all()
        
        if not failed_messages:
            return {'success': False, 'message': 'No failed messages to retry'}
        
        retry_count = 0
        success_count = 0
        
        for sms_msg in failed_messages:
            response = self.api.send_sms(sms_msg.phone_number, sms_msg.content)
            
            if response.get('status') == 'success':
                sms_msg.status = 'sent'
                sms_msg.sent_at = datetime.utcnow()
                sms_msg.mnotify_message_id = response.get('message_id', '')
                sms_msg.delivery_error = None
                success_count += 1
            else:
                sms_msg.delivery_error = response.get('message', 'Unknown error')
            
            sms_msg.retry_count += 1
            sms_msg.last_retry_at = datetime.utcnow()
            retry_count += 1
            db.session.add(sms_msg)
        
        campaign.messages_sent = SMSMessage.query.filter_by(
            campaign_id=campaign_id,
            status='sent'
        ).count()
        campaign.messages_failed = SMSMessage.query.filter_by(
            campaign_id=campaign_id,
            status='failed'
        ).count()
        db.session.add(campaign)
        
        # Log retry action
        log = SMSLog(
            action='bulk_retry',
            action_type='campaign',
            campaign_id=campaign.id,
            admin_id=admin_id,
            message=f'Retried {retry_count} failed messages, {success_count} recovered',
            status='success',
            details=json.dumps({
                'retried': retry_count,
                'recovered': success_count
            })
        )
        db.session.add(log)
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Retried {retry_count} messages, {success_count} recovered',
            'recovered': success_count
        }
    
    def create_template(self, name, category, content, variables, admin_id, description=None):
        """Create a new SMS template"""
        if SMSTemplate.query.filter_by(name=name).first():
            return {'success': False, 'message': 'Template name already exists'}
        
        template = SMSTemplate(
            name=name,
            category=category,
            content=content,
            description=description,
            variables=json.dumps(variables),
            character_count=len(content),
            is_active=True,
            created_by_id=admin_id
        )
        db.session.add(template)
        
        # Log template creation
        log = SMSLog(
            action='template_created',
            action_type='template',
            template_id=template.id,
            admin_id=admin_id,
            message=f'Template "{name}" created',
            status='success'
        )
        db.session.add(log)
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Template "{name}" created',
            'template_id': template.id
        }
    
    def add_to_blacklist(self, phone_number, reason, admin_id):
        """Add phone number to SMS blacklist"""
        if SMSBlacklist.query.filter_by(phone_number=phone_number).first():
            return {'success': False, 'message': 'Phone number already blacklisted'}
        
        blacklist_entry = SMSBlacklist(
            phone_number=phone_number,
            reason=reason,
            added_by_id=admin_id
        )
        db.session.add(blacklist_entry)
        
        # Log blacklist action
        log = SMSLog(
            action='blacklist_added',
            action_type='system',
            admin_id=admin_id,
            message=f'Phone {phone_number} added to blacklist',
            status='success',
            details=json.dumps({'reason': reason})
        )
        db.session.add(log)
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Phone {phone_number} added to blacklist'
        }
    
    @staticmethod
    def _get_recipients_by_filter(recipient_filter, filter_data):
        """Get user recipients based on filter criteria"""
        query = User.query.filter_by(is_active=True)
        
        if recipient_filter == 'verified_only':
            query = query.filter_by(is_verified=True)
        
        elif recipient_filter == 'by_city':
            city = filter_data.get('city')
            if city:
                query = query.filter_by(city=city)
        
        elif recipient_filter == 'by_date_range':
            start_date = filter_data.get('start_date')
            end_date = filter_data.get('end_date')
            if start_date and end_date:
                query = query.filter(
                    User.created_at >= start_date,
                    User.created_at <= end_date
                )
        
        elif recipient_filter == 'custom_list':
            user_ids = filter_data.get('user_ids', [])
            if user_ids:
                query = query.filter(User.id.in_(user_ids))
        
        # Filter out users without phone numbers
        return [u for u in query.all() if u.phone_number]

    def delete_campaign(self, campaign_id, admin_id):
        """Delete a campaign with all its associated messages and logs"""
        campaign = SMSCampaign.query.get(campaign_id)
        
        if not campaign:
            return {'success': False, 'message': 'Campaign not found'}
        
        # Check if campaign can be deleted (only draft and cancelled campaigns can be deleted)
        if campaign.status not in ['draft', 'cancelled']:
            return {
                'success': False,
                'message': f'Cannot delete campaign with status: {campaign.status}. Only draft and cancelled campaigns can be deleted.'
            }
        
        campaign_name = campaign.name
        recipient_count = campaign.recipient_count
        
        try:
            # Get count of messages for logging
            message_count = SMSMessage.query.filter_by(campaign_id=campaign_id).count()
            
            # Delete all messages associated with campaign
            SMSMessage.query.filter_by(campaign_id=campaign_id).delete()
            
            # Create deletion log entry BEFORE deleting campaign
            log = SMSLog(
                action='campaign_deleted',
                action_type='campaign',
                admin_id=admin_id,
                message=f'Campaign "{campaign_name}" deleted (sent to {recipient_count} recipients, {message_count} messages)',
                status='success',
                details=json.dumps({
                    'campaign_name': campaign_name,
                    'recipient_count': recipient_count,
                    'message_count': message_count,
                    'status': campaign.status,
                    'deleted_at': datetime.utcnow().isoformat()
                })
            )
            db.session.add(log)
            
            # Delete campaign
            db.session.delete(campaign)
            
            # Commit all deletions
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Campaign "{campaign_name}" deleted successfully ({message_count} messages removed)'
            }
        
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting campaign: {str(e)}'
            }


# Convenience functions for common SMS scenarios
def send_account_status_sms(user, action, performed_by, reason=None):
    """Send account status change notification via SMS"""
    if not user.phone_number:
        print(f"⚠️ Skipping SMS for {user.email}: No phone number on file")
        return False
    
    try:
        if action == 'activated':
            message = f"Hello {user.username}, your {current_app.config['APP_NAME']} account has been activated. Login now at {current_app.config['APP_URL']}"
        elif action == 'deactivated':
            message = f"Hello {user.username}, your {current_app.config['APP_NAME']} account has been deactivated."
            if reason:
                message += f" Reason: {reason}"
        elif action == 'admin_granted':
            message = f"Hello {user.username}, you have been granted admin privileges on {current_app.config['APP_NAME']}."
        elif action == 'admin_revoked':
            message = f"Hello {user.username}, your admin privileges on {current_app.config['APP_NAME']} have been revoked."
        else:
            return False
        
        message = message[:160]
        print(f"📱 Attempting to send {action} SMS to {user.phone_number}")
        return sms_service.send_sms(user.phone_number, message).get('status') == 'success'
        
    except Exception as e:
        print(f"❌ Error preparing {action} SMS: {str(e)}")
        return False

def send_welcome_sms(user):
    """Send welcome SMS to new users"""
    if not user.phone_number:
        print(f"⚠️ Skipping welcome SMS for {user.email}: No phone number on file")
        return False
    
    try:
        message = f"Welcome to {current_app.config['APP_NAME']}, {user.username}! Shop now at {current_app.config['APP_URL']}"
        message = message[:160]
        
        print(f"📱 Sending welcome SMS to {user.phone_number}")
        return sms_service.send_sms(user.phone_number, message).get('status') == 'success'
        
    except Exception as e:
        print(f"❌ Error sending welcome SMS: {str(e)}")
        return False

def send_verification_sms(user, verification_code):
    """Send email verification code via SMS"""
    if not user.phone_number:
        print(f"⚠️ Skipping verification SMS for {user.email}: No phone number on file")
        return False
    
    try:
        message = f"Your {current_app.config['APP_NAME']} verification code is: {verification_code}"
        message = message[:160]
        
        print(f"📱 Sending verification SMS to {user.phone_number}")
        return sms_service.send_sms(user.phone_number, message).get('status') == 'success'
        
    except Exception as e:
        print(f"❌ Error sending verification SMS: {str(e)}")
        return False


def send_password_reset_sms(user, reset_code):
    """Send password reset code via SMS"""
    if not user.phone_number:
        print(f"⚠️ Skipping password reset SMS for {user.email}: No phone number on file")
        return False
    
    try:
        message = f"Your {current_app.config['APP_NAME']} password reset code is: {reset_code}. Link expires in 1 hour."
        message = message[:160]
        
        print(f"📱 Sending password reset SMS to {user.phone_number}")
        return sms_service.send_sms(user.phone_number, message).get('status') == 'success'
        
    except Exception as e:
        print(f"❌ Error sending password reset SMS: {str(e)}")
        return False


def send_order_status_sms(order, status_message=None):
    """Send order status update via SMS to customer"""
    from models import Order
    
    # Get phone number from order shipping info or user profile
    phone_number = order.shipping_phone or (order.user.phone_number if order.user else None)
    
    if not phone_number:
        print(f"⚠️ Skipping order status SMS for order #{order.order_number}: No phone number on file")
        return False
    
    try:
        # Create status message
        if status_message:
            message = status_message
        else:
            status_labels = {
                'pending': 'Your order is pending. Call 0544765278 for more Info',
                'confirmed': 'Your order has been confirmed. Call 0544765278 for any enquiry',
                'processing': 'Your order is being processed. Call 0544765278 for any enquiry',
                'shipped': f'Your order has been shipped. Tracking: {order.tracking_number or "Coming soon"}. Call 0544765278 for any enquiry',
                'delivered': 'Your order has been delivered. Call 0544765278 for any enquiry',
                'cancelled': 'Your order has been cancelled. Call 0544765278 for any enquiry'
            }
            message = status_labels.get(order.status, f'Your order status is: {order.status}')
        
        # Add order number
        full_message = f"[{current_app.config['APP_NAME']}] {message} (Order #{order.order_number})"
        
        # Truncate to SMS limit
        full_message = full_message[:160]
        
        print(f"📱 Sending order status SMS to {phone_number} for order #{order.order_number}")
        result = sms_service.send_sms(phone_number, full_message)
        
        if result.get('status') == 'success':
            # Log the SMS
            sms_log = SMSLog(
                phone_number=phone_number,
                message=full_message,
                status='sent',
                message_type='order_status',
                reference_id=order.id
            )
            db.session.add(sms_log)
            db.session.commit()
            return True
        else:
            print(f"❌ Failed to send order status SMS: {result.get('message')}")
            return False
        
    except Exception as e:
        print(f"❌ Error sending order status SMS: {str(e)}")
        return False