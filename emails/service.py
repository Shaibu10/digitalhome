import os
import base64
import sys
from flask import render_template, current_app
import json

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class GmailService:
    """Gmail API service for sending emails"""
    
    def __init__(self):
        self.service = None
        self.setup_service()
    
    def setup_service(self):
        """Setup Gmail API service"""
        try:
            # ===== TOGGLE THIS FLAG TO ENABLE/DISABLE GMAIL =====
            # Set to False to disable Gmail and use console logging
            # Set to True to enable Gmail (requires credentials.json)
            ENABLE_GMAIL = os.environ.get('ENABLE_GMAIL', 'false').lower() == 'true'
            # ===================================================
            
            if not ENABLE_GMAIL:
                if os.environ.get('SHOW_EMAIL_WARNINGS', 'true').lower() == 'true':
                    print("⚠️ Gmail API disabled - using console logging for emails")
                self.service = None
                return
            
            # Gmail API setup when ENABLE_GMAIL is True
            # Import here to avoid circular import issues
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE', 'credentials.json')
            
            if not os.path.exists(SERVICE_ACCOUNT_FILE):
                print(f"⚠️ Service account file '{SERVICE_ACCOUNT_FILE}' not found")
                self.service = None
                return
            
            # Validate JSON file
            try:
                with open(SERVICE_ACCOUNT_FILE, 'r') as f:
                    creds_data = json.load(f)
                    required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id', 'token_uri']
                    
                    if not all(field in creds_data for field in required_fields):
                        print("❌ Service account file missing required fields")
                        self.service = None
                        return
            except json.JSONDecodeError:
                print("❌ Service account file is not valid JSON")
                self.service = None
                return
            
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE,
                    scopes=['https://www.googleapis.com/auth/gmail.send']
                )
                
                # Send directly from service account (no domain delegation)
                # This avoids "unauthorized_client" errors
                self.service = build('gmail', 'v1', credentials=credentials)
                service_account_email = creds_data.get('client_email')
                print(f"✅ Gmail service initialized successfully (sending as: {service_account_email})")
                
            except Exception as e:
                print(f"❌ Failed to initialize Gmail service: {e}")
                self.service = None
                
        except Exception as e:
            print(f"❌ Unexpected error during Gmail setup: {e}")
            self.service = None
    
    
    def send_email(self, to, subject, html_content):
        """Send email using Gmail API or fallback to console"""
        if not self.service:
            # Fallback: log email to console
            print("=" * 50)
            print(f"📧 EMAIL WOULD BE SENT (Gmail API not configured)")
            print(f"To: {to}")
            print(f"Subject: {subject}")
            print(f"Content Preview: {html_content[:200]}...")
            print("=" * 50)
            return True  # Return True to indicate "success" for development
        
        try:
            # Gmail API sending code
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            message = MIMEMultipart('alternative')
            message['to'] = to
            message['subject'] = subject
            
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"✅ Email sent successfully to {to}. Message ID: {sent_message['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to}: {e}")
            return False

# Global Gmail service instance
gmail_service = GmailService()

def send_account_status_email(user, action, performed_by, reason=None):
    """Send account status change notification via email and SMS"""
    try:
        if action == 'activated':
            subject = f"Your {current_app.config['APP_NAME']} Account Has Been Activated"
            template = render_template('emails/account_activated.html',
                                     user=user,
                                     app_name=current_app.config['APP_NAME'],
                                     app_url=current_app.config['APP_URL'],
                                     support_email=current_app.config['SUPPORT_EMAIL'],
                                     performed_by=performed_by,
                                     reason=reason)
        elif action == 'deactivated':
            subject = f"Your {current_app.config['APP_NAME']} Account Has Been Deactivated"
            template = render_template('emails/account_deactivated.html',
                                     user=user,
                                     app_name=current_app.config['APP_NAME'],
                                     app_url=current_app.config['APP_URL'],
                                     support_email=current_app.config['SUPPORT_EMAIL'],
                                     performed_by=performed_by,
                                     reason=reason)
        elif action == 'admin_granted':
            subject = f"Admin Privileges Granted - {current_app.config['APP_NAME']}"
            template = render_template('emails/admin_granted.html',
                                     user=user,
                                     app_name=current_app.config['APP_NAME'],
                                     app_url=current_app.config['APP_URL'],
                                     support_email=current_app.config['SUPPORT_EMAIL'],
                                     performed_by=performed_by)
        elif action == 'admin_revoked':
            subject = f"Admin Privileges Revoked - {current_app.config['APP_NAME']}"
            template = render_template('emails/admin_revoked.html',
                                     user=user,
                                     app_name=current_app.config['APP_NAME'],
                                     app_url=current_app.config['APP_URL'],
                                     support_email=current_app.config['SUPPORT_EMAIL'],
                                     performed_by=performed_by)
        else:
            return False
        
        # Send email
        print(f"📧 Attempting to send {action} email to {user.email}")
        email_result = gmail_service.send_email(user.email, subject, template)
        
        # Send SMS in parallel (independently)
        from sms.service import send_account_status_sms
        print(f"📱 Attempting to send {action} SMS to {user.phone_number or 'N/A'}")
        sms_result = send_account_status_sms(user, action, performed_by, reason)
        
        # Return True if at least one succeeded
        return email_result or sms_result
        
    except Exception as e:
        print(f"❌ Error preparing {action} notification: {str(e)}")
        return False

def send_welcome_email(user):
    """Send welcome email and SMS to new users"""
    try:
        subject = f"Welcome to {current_app.config['APP_NAME']}!"
        template = render_template('emails/welcome.html',
                                 user=user,
                                 app_name=current_app.config['APP_NAME'],
                                 app_url=current_app.config['APP_URL'],
                                 support_email=current_app.config['SUPPORT_EMAIL'])
        
        # Send email
        print(f"📧 Sending welcome email to {user.email}")
        email_result = gmail_service.send_email(user.email, subject, template)
        
        # Send SMS in parallel (independently)
        from sms.service import send_welcome_sms
        print(f"📱 Sending welcome SMS to {user.phone_number or 'N/A'}")
        sms_result = send_welcome_sms(user)
        
        # Return True if at least one succeeded
        return email_result or sms_result
        
    except Exception as e:
        print(f"❌ Error sending welcome notification: {str(e)}")
        return False

def send_verification_email(user, verification_code, verification_url):
    """Send email verification and SMS code to user (Option 1: Sequential Verification)
    
    Args:
        user: User object
        verification_code: Short 6-char code to display/send
        verification_url: Full token URL for email backup link
    """
    try:
        
        subject = f"Verify Your Email - {current_app.config['APP_NAME']}"
        template = render_template('emails/verify_email.html',
                                 user=user,
                                 verification_url=verification_url,
                                 verification_code=verification_code,
                                 app_name=current_app.config['APP_NAME'],
                                 app_url=current_app.config['APP_URL'],
                                 support_email=current_app.config['SUPPORT_EMAIL'])
        
        # Send email with verification link
        print(f"📧 Sending verification email to {user.email}")
        print(f"   Verification link: {verification_url}")
        email_result = gmail_service.send_email(user.email, subject, template)
        
        # Send SMS with verification code in parallel (independently)
        # Option 1: User can verify via either email link OR SMS code
        from sms.service import send_verification_sms
        if user.phone_number:
            print(f"📱 Sending verification SMS to {user.phone_number}")
            sms_result = send_verification_sms(user, verification_code)
        else:
            print(f"📱 No phone number on file - SMS verification skipped")
            sms_result = True
        
        # Return True if at least one succeeded (Option 1: Sequential - either email or SMS is enough)
        return email_result or sms_result
        
    except Exception as e:
        print(f"❌ Error sending verification notification: {str(e)}")
        return False


def send_password_reset_email(user, reset_code, reset_url):
    """Send password reset email to user"""
    try:
        subject = f"Reset Your Password - {current_app.config['APP_NAME']}"
        template = render_template('emails/password_reset.html',
                                 user=user,
                                 reset_url=reset_url,
                                 reset_code=reset_code,
                                 app_name=current_app.config['APP_NAME'],
                                 app_url=current_app.config['APP_URL'],
                                 support_email=current_app.config['SUPPORT_EMAIL'])
        
        print(f"📧 Sending password reset email to {user.email}")
        print(f"   Reset link: {reset_url}")
        
        email_result = gmail_service.send_email(user.email, subject, template)
        
        if email_result:
            print(f"✅ Password reset email sent successfully to {user.email}")
        else:
            print(f"❌ Failed to send password reset email to {user.email}")
        
        return email_result
        
    except Exception as e:
        print(f"❌ Error sending password reset email: {str(e)}")
        return False


def send_password_changed_email(user):
    """Send password changed confirmation email to user"""
    try:
        subject = f"Password Changed - {current_app.config['APP_NAME']}"
        template = render_template('emails/password_changed.html',
                                 user=user,
                                 app_name=current_app.config['APP_NAME'],
                                 app_url=current_app.config['APP_URL'],
                                 support_email=current_app.config['SUPPORT_EMAIL'])
        
        print(f"📧 Sending password changed email to {user.email}")
        
        email_result = gmail_service.send_email(user.email, subject, template)
        
        if email_result:
            print(f"✅ Password changed email sent successfully to {user.email}")
        else:
            print(f"❌ Failed to send password changed email to {user.email}")
        
        return email_result
        
    except Exception as e:
        print(f"❌ Error sending password changed email: {str(e)}")
        return False