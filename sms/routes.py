"""SMS Management Routes"""

from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json

from . import sms_bp
from .service import mNotifyService, SMSManager
from models import (
    SMSTemplate, SMSCampaign, SMSMessage, SMSLog, SMSBlacklist, User
)
from extensions import db


# Initialize services
sms_manager = SMSManager()
mnotify_api = mNotifyService()


# ============================================================================
# ADMIN REQUIRED DECORATOR
# ============================================================================
def admin_required(f):
    """Decorator to check if user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# SMS DASHBOARD
# ============================================================================
@sms_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    """Main SMS management dashboard"""
    
    # Get statistics
    total_sent = SMSMessage.query.filter_by(status='sent').count()
    total_failed = SMSMessage.query.filter_by(status='failed').count()
    total_pending = SMSMessage.query.filter_by(status='pending').count()
    
    # Delivery rate
    if total_sent > 0:
        delivered = SMSMessage.query.filter_by(status='delivered').count()
        delivery_rate = (delivered / (total_sent + total_failed)) * 100
    else:
        delivery_rate = 0
    
    # Get recent campaigns
    recent_campaigns = SMSCampaign.query.order_by(
        SMSCampaign.created_at.desc()
    ).limit(10).all()
    
    # Get account balance
    balance_info = mnotify_api.get_account_balance()
    
    # Get recent logs
    recent_logs = SMSLog.query.order_by(
        SMSLog.created_at.desc()
    ).limit(15).all()
    
    return render_template('sms/dashboard.html',
        total_sent=total_sent,
        total_failed=total_failed,
        total_pending=total_pending,
        delivery_rate=round(delivery_rate, 1),
        recent_campaigns=recent_campaigns,
        balance_info=balance_info,
        recent_logs=recent_logs
    )


# ============================================================================
# SINGLE SMS SENDING
# ============================================================================
@sms_bp.route('/single', methods=['GET', 'POST'])
@login_required
@admin_required
def single():
    """Send single SMS to a user"""
    
    if request.method == 'POST':
        user_id = request.form.get('user_id', type=int)
        message = request.form.get('message', '').strip()
        
        if not user_id or not message:
            flash('User and message are required', 'error')
            return redirect(url_for('sms.single'))
        
        if len(message) > 500:
            flash('Message cannot exceed 500 characters', 'error')
            return redirect(url_for('sms.single'))
        
        result = sms_manager.send_single_sms(user_id, message, current_user.id)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
        
        return redirect(url_for('sms.single'))
    
    # Get list of users with phone numbers
    users = User.query.filter(
        User.phone_number != None,
        User.is_active == True
    ).order_by(User.username).all()
    
    return render_template('sms/send_single.html', users=users)


# ============================================================================
# BULK SMS CAMPAIGNS
# ============================================================================
@sms_bp.route('/campaigns', methods=['GET'])
@login_required
@admin_required
def campaigns():
    """View all SMS campaigns"""
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = SMSCampaign.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    campaigns = query.order_by(
        SMSCampaign.created_at.desc()
    ).paginate(page=page, per_page=20)
    
    return render_template('sms/campaigns_list.html',
        campaigns=campaigns,
        status_filter=status_filter
    )


@sms_bp.route('/campaigns/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_campaign():
    """Create a new bulk SMS campaign"""
    
    if request.method == 'POST':
        campaign_name = request.form.get('campaign_name', '').strip()
        template_id = request.form.get('template_id', type=int)
        custom_message = request.form.get('custom_message', '').strip()
        recipient_filter = request.form.get('recipient_filter', 'all_users')
        schedule_time = request.form.get('schedule_time')
        
        if not campaign_name:
            flash('Campaign name is required', 'error')
            return redirect(url_for('sms.create_campaign'))
        
        if not template_id and not custom_message:
            flash('Either select a template or enter a custom message', 'error')
            return redirect(url_for('sms.create_campaign'))
        
        message_to_send = custom_message
        
        # Get filter data
        filter_data = {}
        if recipient_filter == 'by_city':
            filter_data['city'] = request.form.get('city', '').strip()
        elif recipient_filter == 'by_date_range':
            filter_data['start_date'] = request.form.get('start_date')
            filter_data['end_date'] = request.form.get('end_date')
        elif recipient_filter == 'custom_list':
            user_ids = request.form.getlist('user_ids')
            filter_data['user_ids'] = [int(uid) for uid in user_ids if uid.isdigit()]
        
        schedule_dt = None
        if schedule_time:
            try:
                schedule_dt = datetime.fromisoformat(schedule_time)
            except:
                flash('Invalid schedule time', 'error')
                return redirect(url_for('sms.create_campaign'))
        
        result = sms_manager.create_bulk_campaign(
            name=campaign_name,
            message=message_to_send,
            recipient_filter=recipient_filter,
            filter_data=filter_data,
            admin_id=current_user.id,
            template_id=template_id if template_id else None,
            require_confirmation=True,
            schedule_time=schedule_dt
        )
        
        if result['success']:
            flash(f"{result['message']}", 'success')
            return redirect(url_for('sms.view_campaign', campaign_id=result['campaign_id']))
        else:
            flash(result['message'], 'error')
            return redirect(url_for('sms.create_campaign'))
    
    # Get available templates
    templates = SMSTemplate.query.filter_by(is_active=True).all()
    
    # Get unique cities for filter
    cities = db.session.query(User.city).filter(
        User.city != None
    ).distinct().all()
    cities = [city[0] for city in cities if city[0]]
    
    return render_template('sms/create_campaign.html',
        templates=templates,
        cities=cities
    )


@sms_bp.route('/campaigns/<int:campaign_id>', methods=['GET'])
@login_required
@admin_required
def view_campaign(campaign_id):
    """View campaign details"""
    
    campaign = SMSCampaign.query.get_or_404(campaign_id)
    
    # Get messages for this campaign
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = SMSMessage.query.filter_by(campaign_id=campaign_id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    messages = query.paginate(page=page, per_page=50)
    
    return render_template('sms/campaign_details.html',
        campaign=campaign,
        messages=messages,
        status_filter=status_filter
    )


@sms_bp.route('/campaigns/<int:campaign_id>/send', methods=['POST'])
@login_required
@admin_required
def send_campaign(campaign_id):
    """Send a bulk SMS campaign"""
    
    campaign = SMSCampaign.query.get_or_404(campaign_id)
    
    # Check confirmation
    confirmed = request.form.get('confirmed') == 'yes'
    if not confirmed:
        flash('Campaign send must be confirmed', 'error')
        return redirect(url_for('sms.view_campaign', campaign_id=campaign_id))
    
    result = sms_manager.send_campaign(campaign_id, current_user.id)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('sms.view_campaign', campaign_id=campaign_id))


@sms_bp.route('/campaigns/<int:campaign_id>/retry', methods=['POST'])
@login_required
@admin_required
def retry_campaign_failed(campaign_id):
    """Retry failed messages in a campaign"""
    
    campaign = SMSCampaign.query.get_or_404(campaign_id)
    
    result = sms_manager.retry_failed_messages(campaign_id, current_user.id)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('sms.view_campaign', campaign_id=campaign_id))


@sms_bp.route('/campaigns/<int:campaign_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel_campaign(campaign_id):
    """Cancel a campaign"""
    
    campaign = SMSCampaign.query.get_or_404(campaign_id)
    
    if campaign.status in ['draft', 'scheduled']:
        campaign.status = 'cancelled'
        db.session.add(campaign)
        
        log = SMSLog(
            action='campaign_cancelled',
            action_type='campaign',
            campaign_id=campaign.id,
            admin_id=current_user.id,
            message=f'Campaign "{campaign.name}" cancelled',
            status='success'
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Campaign cancelled successfully', 'success')
    else:
        flash(f'Cannot cancel campaign with status: {campaign.status}', 'error')
    
    return redirect(url_for('sms.campaigns'))


@sms_bp.route('/campaigns/<int:campaign_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_campaign(campaign_id):
    """Delete a campaign permanently"""
    
    campaign = SMSCampaign.query.get_or_404(campaign_id)
    
    # Check confirmation
    confirmed = request.form.get('confirmed') == 'yes'
    if not confirmed:
        flash('Campaign deletion must be confirmed', 'error')
        return redirect(url_for('sms.view_campaign', campaign_id=campaign_id))
    
    result = sms_manager.delete_campaign(campaign_id, current_user.id)
    
    if result['success']:
        flash(result['message'], 'success')
        return redirect(url_for('sms.campaigns'))
    else:
        flash(result['message'], 'error')
        return redirect(url_for('sms.view_campaign', campaign_id=campaign_id))


# ============================================================================
# SMS TEMPLATES
# ============================================================================
@sms_bp.route('/templates', methods=['GET'])
@login_required
@admin_required
def templates():
    """View all SMS templates"""
    
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', '')
    
    query = SMSTemplate.query
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    templates = query.order_by(
        SMSTemplate.created_at.desc()
    ).paginate(page=page, per_page=20)
    
    categories = db.session.query(SMSTemplate.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('sms/templates_list.html',
        templates=templates,
        category_filter=category_filter,
        categories=categories
    )


@sms_bp.route('/templates/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_template():
    """Create a new SMS template"""
    
    if request.method == 'POST':
        template_name = request.form.get('template_name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        
        if not template_name or not content:
            flash('Template name and content are required', 'error')
            return redirect(url_for('sms.create_template'))
        
        if len(content) > 500:
            flash('Template content cannot exceed 500 characters', 'error')
            return redirect(url_for('sms.create_template'))
        
        # Extract variables from content (e.g., {first_name})
        import re
        variables = re.findall(r'\{(\w+)\}', content)
        variables = list(set(variables))  # Remove duplicates
        
        result = sms_manager.create_template(
            name=template_name,
            category=category or 'custom',
            content=content,
            variables=variables,
            admin_id=current_user.id,
            description=description
        )
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('sms.templates'))
        else:
            flash(result['message'], 'error')
            return redirect(url_for('sms.create_template'))
    
    categories = [
        'order_confirm',
        'shipping',
        'delivery',
        'verification',
        'promotion',
        'abandoned_cart',
        'custom'
    ]
    
    return render_template('sms/create_template.html', categories=categories)


@sms_bp.route('/templates/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_template(template_id):
    """Edit an SMS template"""
    
    template = SMSTemplate.query.get_or_404(template_id)
    
    if request.method == 'POST':
        template.name = request.form.get('template_name', '').strip()
        template.category = request.form.get('category', '').strip()
        template.description = request.form.get('description', '').strip()
        template.content = request.form.get('content', '').strip()
        
        # Extract variables
        import re
        variables = re.findall(r'\{(\w+)\}', template.content)
        variables = list(set(variables))
        
        template.variables = json.dumps(variables)
        template.character_count = len(template.content)
        template.updated_at = datetime.utcnow()
        
        db.session.add(template)
        db.session.commit()
        
        flash('Template updated successfully', 'success')
        return redirect(url_for('sms.templates'))
    
    categories = [
        'order_confirm',
        'shipping',
        'delivery',
        'verification',
        'promotion',
        'abandoned_cart',
        'custom'
    ]
    
    return render_template('sms/edit_template.html',
        template=template,
        categories=categories
    )


# ============================================================================
# SMS LOGS & HISTORY
# ============================================================================
@sms_bp.route('/messages', methods=['GET'])
@login_required
@admin_required
def messages_list():
    """View all SMS messages"""
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = SMSMessage.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    messages = query.order_by(
        SMSMessage.created_at.desc()
    ).paginate(page=page, per_page=50)
    
    return render_template('sms/messages_list.html',
        messages=messages,
        status_filter=status_filter
    )


@sms_bp.route('/logs', methods=['GET'])
@login_required
@admin_required
def activity_logs():
    """View SMS activity logs"""
    
    page = request.args.get('page', 1, type=int)
    action_filter = request.args.get('action', '')
    
    query = SMSLog.query
    
    if action_filter:
        query = query.filter_by(action=action_filter)
    
    logs = query.order_by(
        SMSLog.created_at.desc()
    ).paginate(page=page, per_page=50)
    
    return render_template('sms/activity_logs.html', logs=logs)


# ============================================================================
# BLACKLIST MANAGEMENT
# ============================================================================
@sms_bp.route('/blacklist', methods=['GET', 'POST'])
@login_required
@admin_required
def blacklist_management():
    """Manage SMS blacklist"""
    
    if request.method == 'POST':
        phone_number = request.form.get('phone_number', '').strip()
        reason = request.form.get('reason', '').strip()
        
        if not phone_number:
            flash('Phone number is required', 'error')
            return redirect(url_for('sms.blacklist_management'))
        
        result = sms_manager.add_to_blacklist(phone_number, reason, current_user.id)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
        
        return redirect(url_for('sms.blacklist_management'))
    
    page = request.args.get('page', 1, type=int)
    
    blacklist = SMSBlacklist.query.paginate(page=page, per_page=50)
    
    return render_template('sms/blacklist.html', blacklist=blacklist)


@sms_bp.route('/blacklist/<int:entry_id>/remove', methods=['POST'])
@login_required
@admin_required
def remove_blacklist(entry_id):
    """Remove a phone number from blacklist"""
    
    entry = SMSBlacklist.query.get_or_404(entry_id)
    
    db.session.delete(entry)
    
    log = SMSLog(
        action='blacklist_removed',
        action_type='system',
        admin_id=current_user.id,
        message=f'Phone {entry.phone_number} removed from blacklist',
        status='success'
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Phone number removed from blacklist', 'success')
    return redirect(url_for('sms.blacklist_management'))


# ============================================================================
# API ENDPOINTS
# ============================================================================
@sms_bp.route('/api/user-search', methods=['GET'])
@login_required
@admin_required
def api_user_search():
    """Search for users (API endpoint)"""
    
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    users = User.query.filter(
        User.is_active == True,
        User.phone_number != None,
        (User.username.ilike(f'%{query}%')) |
        (User.email.ilike(f'%{query}%')) |
        (User.first_name.ilike(f'%{query}%'))
    ).limit(10).all()
    
    return jsonify([
        {
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'phone': u.phone_number,
            'name': f"{u.first_name or ''} {u.last_name or ''}".strip()
        }
        for u in users
    ])


@sms_bp.route('/api/campaign-preview/<int:campaign_id>', methods=['GET'])
@login_required
@admin_required
def api_campaign_preview(campaign_id):
    """Get preview of campaign messages"""
    
    campaign = SMSCampaign.query.get_or_404(campaign_id)
    
    # Get sample messages
    sample_messages = SMSMessage.query.filter_by(
        campaign_id=campaign_id,
        status='pending'
    ).limit(5).all()
    
    return jsonify({
        'campaign_id': campaign.id,
        'campaign_name': campaign.name,
        'total_messages': campaign.recipient_count,
        'pending_messages': SMSMessage.query.filter_by(
            campaign_id=campaign_id,
            status='pending'
        ).count(),
        'samples': [
            {
                'phone': msg.phone_number,
                'recipient': msg.recipient_name,
                'message': msg.content,
                'sms_parts': msg.sms_parts
            }
            for msg in sample_messages
        ]
    })
