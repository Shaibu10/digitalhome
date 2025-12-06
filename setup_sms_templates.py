#!/usr/bin/env python
"""
SMS System - Setup Default Templates and Sample Data
Populates database with commonly used SMS templates
"""

from app import app, db
from models import SMSTemplate, User
from datetime import datetime

def setup_sms_templates():
    """Create system SMS templates"""
    
    with app.app_context():
        print("=" * 70)
        print("SMS SYSTEM - SETUP DEFAULT TEMPLATES")
        print("=" * 70)
        
        # Check if templates already exist
        existing = SMSTemplate.query.filter_by(is_system_template=True).count()
        if existing > 0:
            print(f"\n⚠️  Found {existing} existing system templates")
            print("Skipping template creation (already setup)")
            return
        
        # Get admin user for creator
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("\n❌ ERROR: No admin user found!")
            print("Please create admin user first")
            return
        
        templates = [
            {
                'name': 'Order Confirmation',
                'category': 'orders',
                'description': 'Sent when customer places an order',
                'content': 'Hi {user_name}! Your order #{order_id} has been confirmed. Expected delivery: {delivery_date}. Thank you!',
                'is_system_template': True,
            },
            {
                'name': 'Order Shipped',
                'category': 'shipping',
                'description': 'Sent when order is dispatched',
                'content': 'Good news {user_name}! Your order #{order_id} has shipped! Track your package: {tracking_url}',
                'is_system_template': True,
            },
            {
                'name': 'Delivery Reminder',
                'category': 'shipping',
                'description': 'Reminder that delivery is arriving soon',
                'content': '{user_name}, your delivery from order #{order_id} is arriving today! Be ready to receive it.',
                'is_system_template': True,
            },
            {
                'name': 'Verification Code',
                'category': 'verification',
                'description': 'SMS verification code for account confirmation',
                'content': 'Your DigitalHome verification code is: {code}. Do not share this with anyone. Valid for 10 minutes.',
                'is_system_template': True,
            },
            {
                'name': 'Password Reset',
                'category': 'verification',
                'description': 'Password reset OTP',
                'content': 'Your DigitalHome password reset code is: {code}. If you did not request this, ignore this message.',
                'is_system_template': True,
            },
            {
                'name': 'Flash Sale Alert',
                'category': 'marketing',
                'description': 'Announce flash sale or promotion',
                'content': '🎉 FLASH SALE! Get {discount}% OFF everything! Use code {promo_code}. Offer valid until {expiry_date}. Shop now!',
                'is_system_template': True,
            },
            {
                'name': 'New Arrival',
                'category': 'marketing',
                'description': 'Notify about new product arrival',
                'content': 'New arrivals just dropped! Check out {product_name} - {discount}% off for first-time buyers. {shop_link}',
                'is_system_template': True,
            },
            {
                'name': 'Payment Confirmation',
                'category': 'payments',
                'description': 'Confirm payment received',
                'content': 'Payment confirmed for order #{order_id}. Amount: {amount}. Your order will be processed shortly.',
                'is_system_template': True,
            },
            {
                'name': 'Wallet Credit',
                'category': 'wallet',
                'description': 'Notify wallet credit received',
                'content': '{user_name}, you received {amount} credit to your DigitalHome wallet. Current balance: {balance}',
                'is_system_template': True,
            },
            {
                'name': 'Refund Processed',
                'category': 'payments',
                'description': 'Notify customer about refund',
                'content': 'Refund of {amount} for order #{order_id} has been processed. Money will arrive in {days} business days.',
                'is_system_template': True,
            },
        ]
        
        print("\nCreating system templates:\n")
        
        created = 0
        for template_data in templates:
            # Extract variables from content
            import re
            pattern = r'\{(\w+)\}'
            variables = list(set(re.findall(pattern, template_data['content'])))
            
            # Create template
            template = SMSTemplate(
                name=template_data['name'],
                category=template_data['category'],
                description=template_data['description'],
                content=template_data['content'],
                variables=','.join(variables),
                character_count=len(template_data['content']),
                is_system_template=True,
                created_by_id=admin.id
            )
            
            db.session.add(template)
            print(f"  ✅ {template_data['name']}")
            print(f"     Variables: {', '.join(variables) if variables else 'None'}")
            print(f"     Length: {len(template_data['content'])} chars")
            created += 1
        
        # Save all templates
        try:
            db.session.commit()
            print(f"\n" + "=" * 70)
            print(f"✅ Successfully created {created} system templates")
            print("=" * 70)
            
            # Show summary
            print(f"\nTemplates available at: /admin/sms/templates")
            print(f"Use these templates to send bulk SMS campaigns")
            print(f"Customize with your own values for variables")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating templates: {e}")
            return False
        
        return True

def list_templates():
    """List all created templates"""
    with app.app_context():
        templates = SMSTemplate.query.all()
        print("\n" + "=" * 70)
        print("AVAILABLE SMS TEMPLATES")
        print("=" * 70)
        
        if not templates:
            print("\nNo templates found. Run setup first!")
            return
        
        for i, template in enumerate(templates, 1):
            print(f"\n{i}. {template.name}")
            print(f"   Category: {template.category}")
            print(f"   Description: {template.description}")
            print(f"   Content: {template.content[:60]}...")
            print(f"   Variables: {template.variables if template.variables else 'None'}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_templates()
    else:
        setup_sms_templates()
        print("\n💡 Tip: Run 'python setup_sms_templates.py list' to view templates")
