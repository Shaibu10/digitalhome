import os

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///digitalhome.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration - save to static/uploads so Flask can serve them
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # mNotify SMS Configuration
    MNOTIFY_API_KEY = os.environ.get('MNOTIFY_API_KEY')
    MNOTIFY_SENDER_ID = os.environ.get('MNOTIFY_SENDER_ID', 'DigitalHome')
    
    # Paystack Payment Configuration
    PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
    PAYSTACK_CALLBACK_URL = os.environ.get('PAYSTACK_CALLBACK_URL')
    PAYSTACK_WEBHOOK_SECRET = os.environ.get('PAYSTACK_WEBHOOK_SECRET')
    
    # Payment Settings
    PAYMENT_CURRENCY = 'GHS'
    PAYMENT_TIMEOUT = 3600  # 1 hour in seconds
    
    # App Information
    APP_NAME = 'DigitalHome'
    APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'support@digitalhome.com')