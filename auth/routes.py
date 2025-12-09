# auth/routes.py
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp  # Import from current package
from .utils import GoogleOAuth, get_google_oauth_url, TokenGenerator
from models import User, EmailToken
from extensions import db
from datetime import datetime, timedelta
import requests
import secrets

# Remove the user_loader from here since it's in app.py

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with email/password and Google OAuth option"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return redirect(url_for('auth.login'))
            
            # Check if email is verified
            if not user.is_verified:
                flash('Please verify your email address before logging in. Check your inbox for the verification link.', 'info')
                return render_template('auth/pending_verification.html', email=email)
            
            # Login user
            login_user(user)
            
            # Log login activity
            from app import log_user_activity
            log_user_activity(user, 'login', 'User logged in with email/password', request)
            
            flash(f'Welcome back, {user.username}!', 'success')
            next_url = request.args.get('next', url_for('index'))
            return redirect(next_url)
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

@auth_bp.route('/login/google')
def login_google():
    """Initiate Google OAuth flow"""
    redirect_uri = url_for('auth.google_callback', _external=True)
    authorization_url, state = get_google_oauth_url(redirect_uri)
    
    # Store state in session for validation
    session['oauth_state'] = state
    session['next_url'] = request.args.get('next', url_for('index'))
    
    return redirect(authorization_url)

@auth_bp.route('/google/callback')
def google_callback():
    """Google OAuth callback handler"""
    try:
        # Verify state parameter
        if session.get('oauth_state') != request.args.get('state'):
            flash('Invalid OAuth state parameter', 'error')
            return redirect(url_for('auth.login'))
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            flash('Authorization code not provided', 'error')
            return redirect(url_for('auth.login'))
        
        # Exchange code for tokens
        redirect_uri = url_for('auth.google_callback', _external=True)
        flow = GoogleOAuth.get_flow(redirect_uri)
        flow.fetch_token(code=code)
        
        # Get user info
        credentials = flow.credentials
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        user_info = user_info_response.json()
        
        # Find or create user
        user = User.query.filter_by(email=user_info['email']).first()
        
        if not user:
            # Create new user
            user = User(
                username=user_info.get('name', user_info['email'].split('@')[0]),
                email=user_info['email'],
                is_active=True,
                is_verified=True,  # Auto-verify for Google OAuth users
                verified_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
            
            # Log registration activity
            from app import log_user_activity
            log_user_activity(user, 'registration', 'User registered via Google OAuth', request)
            
            flash('Account created successfully!', 'success')
        else:
            # Log login activity
            from app import log_user_activity
            log_user_activity(user, 'login', 'User logged in via Google OAuth', request)
        
        # Login user
        login_user(user)
        
        # Clear session
        session.pop('oauth_state', None)
        next_url = session.pop('next_url', url_for('index'))
        
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_url)
        
    except Exception as e:
        print(f"Google OAuth error: {e}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page with email/password registration and email verification"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone_number = request.form.get('phone_number', '').strip() or None
        
        # Validate input
        if not username or not email or not password:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('auth.register'))
        
        # Validate phone number format if provided
        if phone_number and not (len(phone_number) == 10 and phone_number.isdigit()):
            flash('Invalid phone number format. Please use 10 digits (e.g., 0241234567)', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if phone number already registered (if provided)
        if phone_number and User.query.filter_by(phone_number=phone_number).first():
            flash('Phone number already registered', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user (not verified yet)
        user = User(username=username, email=email, phone_number=phone_number, is_active=True, is_verified=False)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate email verification token with rate limiting
        token_result = TokenGenerator.generate_email_token(user, token_type='email_verification')
        
        if not token_result['success']:
            flash(token_result['message'], 'error')
            return redirect(url_for('auth.register'))
        
        email_token = token_result['token']
        
        # Send verification email and SMS (Option 1: Sequential)
        try:
            from emails.service import send_verification_email
            # Pass the verification code and token URL
            verification_url = url_for('auth.verify_email', token=email_token.token, _external=True)
            send_verification_email(user, email_token.verification_code, verification_url)
            
            flash('Account created! Please check your email or phone for a verification code. You can verify using either method.', 'success')
            session['pending_verification_email'] = email  # Store email in session for resend functionality
            return redirect(url_for('auth.verify_code'))  # Redirect to code verification page
        except Exception as e:
            print(f"Error sending verification email: {e}")
            flash('Account created but verification email failed to send. Please contact support.', 'warning')
            session['pending_verification_email'] = email  # Store email in session even if email fails
            return redirect(url_for('auth.verify_code'))  # Still show verification page
    
    return render_template('auth/register.html')

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify email using token"""
    # Verify the token
    email_token = TokenGenerator.verify_token(token, token_type='email_verification')
    
    if not email_token:
        flash('Invalid or expired verification link. Please register again or request a new verification link.', 'error')
        return redirect(url_for('auth.login'))
    
    # Mark user as verified
    user = email_token.user
    user.is_verified = True
    user.verified_at = datetime.utcnow()
    
    # Mark token as used
    email_token.mark_as_used()
    
    db.session.commit()
    
    # Log email verification activity
    from app import log_user_activity
    log_user_activity(user, 'email_verified', 'User verified their email address', request)
    
    flash('Email verified successfully! You can now login.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    """Verify account using code sent via email or SMS (Option 1: Sequential Verification)"""
    if request.method == 'POST':
        verification_code = request.form.get('verification_code', '').strip().upper()
        
        if not verification_code:
            flash('Please enter a verification code', 'error')
            pending_email = session.get('pending_verification_email', '')
            return render_template('auth/verify_code.html', pending_email=pending_email)
        
        # Find the token by verification code
        matching_token = EmailToken.query.filter_by(
            verification_code=verification_code.upper(),
            token_type='email_verification'
        ).first()
        
        if matching_token and not matching_token.is_valid():
            matching_token = None
        
        if not matching_token:
            flash('Invalid or expired verification code. Please check your email or SMS.', 'error')
            pending_email = session.get('pending_verification_email', '')
            return render_template('auth/verify_code.html', pending_email=pending_email)
        
        # Mark user as verified
        user = matching_token.user
        user.is_verified = True
        user.verified_at = datetime.utcnow()
        
        # Mark token as used
        matching_token.mark_as_used()
        
        db.session.commit()
        
        # Log verification activity
        from app import log_user_activity
        log_user_activity(user, 'email_verified', 'User verified account via email/SMS code (Option 1)', request)
        
        print(f"✅ User {user.username} verified account using code")
        flash('Account verified successfully! You can now login.', 'success')
        
        # Clear the pending verification email from session
        session.pop('pending_verification_email', None)
        
        return redirect(url_for('auth.login'))
    
    # GET request - show verification form
    pending_email = session.get('pending_verification_email', '')
    return render_template('auth/verify_code.html', pending_email=pending_email)

@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    """Resend verification email/SMS code with rate limiting (Option 1: Sequential Verification)"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
    else:
        email = request.args.get('email', '').strip()
    
    if not email:
        flash('Email address is required', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('Email address not found.', 'error')
        return redirect(url_for('auth.login'))
    
    if user.is_verified:
        flash('Your email is already verified. You can login now.', 'info')
        return redirect(url_for('auth.login'))
    
    # Check rate limit
    rate_limit_check = TokenGenerator.check_rate_limit(email)
    if not rate_limit_check['allowed']:
        flash(rate_limit_check['message'], 'error')
        return render_template('auth/pending_verification.html', email=email)
    
    # Check if there's already a valid token
    valid_token = EmailToken.query.filter_by(
        user_id=user.id,
        token_type='email_verification'
    ).filter(EmailToken.expires_at > datetime.utcnow()).first()
    
    if not valid_token:
        # Generate new verification token
        token_result = TokenGenerator.generate_email_token(user, token_type='email_verification')
        if not token_result['success']:
            flash(token_result['message'], 'error')
            return render_template('auth/pending_verification.html', email=email)
        valid_token = token_result['token']
    
    # Send verification email and SMS (Option 1: Sequential)
    try:
        from emails.service import send_verification_email
        # Pass the verification code and token URL
        verification_url = url_for('auth.verify_email', token=valid_token.token, _external=True)
        send_verification_email(user, valid_token.verification_code, verification_url)
        
        flash('Verification code sent to your email and SMS! Check both for the code.', 'success')
    except Exception as e:
        print(f"Error sending verification notification: {e}")
        flash('Failed to send verification code. Please try again later.', 'error')
    
    return render_template('auth/verify_code.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    from app import log_user_activity
    log_user_activity(current_user, 'logout', 'User logged out', request)
    
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    from datetime import datetime as dt
    return render_template('auth/profile.html', user=current_user, now=dt.utcnow())

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    # Validate input
    if not current_password or not new_password or not confirm_password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    # Check if new password matches confirm password
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'New passwords do not match'}), 400
    
    # Check if new password is at least 6 characters
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400
    
    # Verify current password
    if not current_user.check_password(current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 401
    
    # Check if new password is different from old password
    if current_user.check_password(new_password):
        return jsonify({'success': False, 'message': 'New password must be different from current password'}), 400
    
    try:
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        # Log this action
        from app import log_user_activity
        log_user_activity(current_user, 'password_changed', 'User changed their password', request)
        
        return jsonify({'success': True, 'message': 'Password changed successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@auth_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Update user fields
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        address = data.get('address', '').strip()
        city = data.get('city', '').strip()
        postal_code = data.get('postal_code', '').strip()
        phone_number = data.get('phone_number', '').strip()
        
        # Validate length constraints
        if len(first_name) > 100:
            return jsonify({'success': False, 'message': 'First name must be 100 characters or less'}), 400
        if len(last_name) > 100:
            return jsonify({'success': False, 'message': 'Last name must be 100 characters or less'}), 400
        if len(address) > 255:
            return jsonify({'success': False, 'message': 'Address must be 255 characters or less'}), 400
        if len(city) > 100:
            return jsonify({'success': False, 'message': 'City must be 100 characters or less'}), 400
        if len(postal_code) > 20:
            return jsonify({'success': False, 'message': 'Postal code must be 20 characters or less'}), 400
        if len(phone_number) > 20:
            return jsonify({'success': False, 'message': 'Phone number must be 20 characters or less'}), 400
        
        # Update current user fields
        current_user.first_name = first_name if first_name else None
        current_user.last_name = last_name if last_name else None
        current_user.address = address if address else None
        current_user.city = city if city else None
        current_user.postal_code = postal_code if postal_code else None
        current_user.phone_number = phone_number if phone_number else None
        
        db.session.commit()
        
        # Log this action
        from app import log_user_activity
        log_user_activity(current_user, 'profile_updated', 'User updated their profile information', request)
        
        return jsonify({'success': True, 'message': 'Profile updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Admin verification management routes
@auth_bp.route('/admin/verification', methods=['GET'])
@login_required
def admin_verification_dashboard():
    """Admin dashboard for managing email verification"""
    from flask import abort
    
    # Check if user is admin
    if not current_user.is_admin:
        abort(403)
    
    # Get all unverified users with pagination
    page = request.args.get('page', 1, type=int)
    unverified_users = User.query.filter_by(is_verified=False).paginate(page=page, per_page=20)
    
    # Get verification statistics
    total_users = User.query.count()
    verified_users = User.query.filter_by(is_verified=True).count()
    unverified_count = User.query.filter_by(is_verified=False).count()
    
    stats = {
        'total_users': total_users,
        'verified_users': verified_users,
        'unverified_users': unverified_count,
        'verification_rate': round((verified_users / total_users * 100) if total_users > 0 else 0, 2)
    }
    
    return render_template(
        'admin/verification_dashboard.html',
        unverified_users=unverified_users,
        stats=stats
    )

@auth_bp.route('/admin/verification/manual-verify/<int:user_id>', methods=['POST'])
@login_required
def manual_verify_user(user_id):
    """Manually verify a user (admin only)"""
    from flask import abort
    
    # Check if user is admin
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Mark user as verified
    user.is_verified = True
    user.verified_at = datetime.utcnow()
    db.session.commit()
    
    # Log the activity
    from app import log_user_activity
    log_user_activity(
        current_user,
        'admin_manual_verify',
        f'Admin manually verified user {user.email} (ID: {user_id})',
        request
    )
    
    flash(f'User {user.email} has been manually verified.', 'success')
    return redirect(url_for('auth.admin_verification_dashboard'))

@auth_bp.route('/admin/verification/resend/<int:user_id>', methods=['POST'])
@login_required
def admin_resend_verification(user_id):
    """Admin resend verification email to unverified user"""
    from flask import abort
    
    # Check if user is admin
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    if user.is_verified:
        flash(f'User {user.email} is already verified.', 'info')
        return redirect(url_for('auth.admin_verification_dashboard'))
    
    # Check if there's already a valid token
    valid_token = EmailToken.query.filter_by(
        user_id=user.id,
        token_type='email_verification'
    ).filter(EmailToken.expires_at > datetime.utcnow()).first()
    
    if not valid_token:
        # Generate new token (bypass rate limiting for admin)
        from models import EmailToken
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        valid_token = EmailToken(
            user_id=user.id,
            token=token,
            token_type='email_verification',
            expires_at=expires_at
        )
        db.session.add(valid_token)
        db.session.commit()
    
    # Send verification email
    try:
        from emails.service import send_verification_email
        verification_url = url_for('auth.verify_email', token=valid_token.token, _external=True)
        send_verification_email(user, verification_url)
        
        # Log the activity
        from app import log_user_activity
        log_user_activity(
            current_user,
            'admin_resend_verification',
            f'Admin resent verification email to user {user.email} (ID: {user_id})',
            request
        )
        
        flash(f'Verification email sent to {user.email}.', 'success')
    except Exception as e:
        print(f"Error sending verification email: {e}")
        flash(f'Failed to send verification email to {user.email}.', 'error')
    
    return redirect(url_for('auth.admin_verification_dashboard'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page - user enters email to receive password reset link"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        user = User.query.filter_by(email=email).first()
        
        # Always show success message for security (don't reveal if email exists)
        if user:
            # Generate password reset token
            token_result = TokenGenerator.generate_email_token(user, token_type='password_reset', expires_in_hours=1)
            
            if token_result['success']:
                # Send password reset email and SMS
                try:
                    from emails.service import send_password_reset_email
                    from sms.service import send_password_reset_sms
                    
                    reset_url = url_for('auth.reset_password', token=token_result['token'].token, _external=True)
                    reset_code = token_result['token'].verification_code
                    
                    # Send email
                    email_sent = send_password_reset_email(user, reset_code, reset_url)
                    
                    # Send SMS if user has phone number
                    sms_sent = False
                    if user.phone_number:
                        sms_sent = send_password_reset_sms(user, reset_code)
                    
                    # Log activity
                    from app import log_user_activity
                    log_user_activity(
                        user,
                        'password_reset_requested',
                        f'User requested password reset (Email: {"sent" if email_sent else "failed"}, SMS: {"sent" if sms_sent else "not sent"})',
                        request
                    )
                except Exception as e:
                    print(f"Error sending password reset notifications: {e}")
        
        flash('If an account exists with that email, you will receive a password reset link via email and SMS. Check your inbox and spam folder.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password page - user enters new password"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Verify token
    email_token = TokenGenerator.verify_token(token, token_type='password_reset')
    
    if not email_token:
        flash('Invalid or expired password reset link. Please request a new one.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validate input
        if not password or not confirm_password:
            flash('Please fill in all fields', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        # Update password
        user = email_token.user
        user.set_password(password)
        
        # Mark token as used
        email_token.mark_as_used()
        
        db.session.commit()
        
        # Log activity
        from app import log_user_activity
        log_user_activity(user, 'password_reset', 'User successfully reset password', request)
        
        # Send confirmation email
        try:
            from emails.service import send_password_changed_email
            send_password_changed_email(user)
        except Exception as e:
            print(f"Error sending password changed email: {e}")
        
        flash('Your password has been reset successfully. Please login with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)
