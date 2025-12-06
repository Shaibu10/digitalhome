import os
import secrets
import string
from flask import current_app, url_for
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import json
import secrets
from datetime import datetime, timedelta

class GoogleOAuth:
    """Google OAuth 2.0 utility class"""
    
    # Google OAuth 2.0 configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    
    @staticmethod
    def get_flow(redirect_uri=None):
        """Create OAuth flow instance"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GoogleOAuth.GOOGLE_CLIENT_ID,
                    "client_secret": GoogleOAuth.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=[
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
            ],
            redirect_uri=redirect_uri
        )
        return flow
    
    @staticmethod
    def validate_token(token):
        """Validate Google OAuth token"""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), GoogleOAuth.GOOGLE_CLIENT_ID
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return idinfo
        except Exception as e:
            print(f"Token validation failed: {e}")
            return None

def get_google_oauth_url(redirect_uri):
    """Generate Google OAuth URL"""
    flow = GoogleOAuth.get_flow(redirect_uri)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url, state


class TokenGenerator:
    """Utility class for generating and validating email tokens"""
    
    MAX_ATTEMPTS = 5  # Lock after 5 attempts
    
    @staticmethod
    def check_rate_limit(email):
        """
        Check if email is rate limited for token generation
        
        Args:
            email: Email address to check
            
        Returns:
            dict with keys: 'allowed' (bool), 'message' (str), 'wait_seconds' (int)
        """
        from models import TokenRateLimit
        from datetime import datetime
        
        rate_limit = TokenRateLimit.get_or_create(email)
        
        if rate_limit.is_locked():
            wait_time = int((rate_limit.locked_until - datetime.utcnow()).total_seconds())
            return {
                'allowed': False,
                'message': f'Too many requests. Please wait {wait_time} seconds before trying again.',
                'wait_seconds': wait_time
            }
        
        return {
            'allowed': True,
            'message': None,
            'wait_seconds': 0
        }
    
    @staticmethod
    def generate_email_token(user, token_type='email_verification', expires_in_hours=24):
        """
        Generate a unique email verification token with rate limiting
        
        Args:
            user: User instance
            token_type: Type of token (email_verification or password_reset)
            expires_in_hours: How long the token is valid
            
        Returns:
            dict with 'success' (bool), 'token' (EmailToken or None), 'message' (str)
        """
        from models import EmailToken, TokenRateLimit
        from extensions import db
        
        # Check rate limit
        rate_limit_check = TokenGenerator.check_rate_limit(user.email)
        if not rate_limit_check['allowed']:
            return {
                'success': False,
                'token': None,
                'message': rate_limit_check['message']
            }
        
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Generate short 6-character verification code (alphanumeric)
        verification_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        # Create token record
        email_token = EmailToken(
            user_id=user.id,
            token=token,
            verification_code=verification_code,
            token_type=token_type,
            expires_at=expires_at
        )
        
        db.session.add(email_token)
        
        # Update rate limit tracking
        rate_limit = TokenRateLimit.get_or_create(user.email)
        rate_limit.increment_attempt()
        
        db.session.commit()
        
        return {
            'success': True,
            'token': email_token,
            'message': 'Verification email sent successfully'
        }
    
    @staticmethod
    def verify_token(token, token_type='email_verification'):
        """
        Verify and retrieve a token, then reset rate limit on success
        
        Args:
            token: Token string to verify
            token_type: Expected token type
            
        Returns:
            EmailToken instance if valid, None otherwise
        """
        from models import EmailToken, TokenRateLimit
        
        email_token = EmailToken.query.filter_by(token=token, token_type=token_type).first()
        
        if not email_token:
            return None
        
        if not email_token.is_valid():
            return None
        
        # Reset rate limit on successful verification
        rate_limit = TokenRateLimit.get_or_create(email_token.user.email)
        rate_limit.reset()
        
        return email_token