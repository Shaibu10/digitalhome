"""
DigitalHome E-Commerce Platform
Main Application File

This module initializes the Flask application and configures all extensions,
blueprints, routes, and utilities for the e-commerce platform.
"""

import os
import json
import sys
from datetime import datetime, timedelta
from sqlalchemy import and_

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from PIL import Image

from config import Config
from extensions import db, migrate, login_manager
from models import User, Product, Category, Order, OrderItem, CartItem, HeroSection, UserActivity, SystemSettings, DynamicMessage, ProductReview, ContactSettings

# =============================================================================
# APPLICATION FACTORY
# =============================================================================

def create_app():
    """
    Application factory function to create and configure the Flask app.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    register_blueprints(app)
    
    # Register context processors and template filters
    register_template_utilities(app)
    
    # Import and initialize email service
    initialize_email_service()
    
    # Initialize database tables on app creation
    # This ensures tables exist for deployment on Render
    with app.app_context():
        try:
            print("=" * 60, file=sys.stderr)
            print("Initializing database tables...", file=sys.stderr)
            
            # Create tables if they don't exist (preserves existing data)
            db.create_all()
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"✅ Database initialization successful!", file=sys.stderr)
            print(f"✅ Tables created: {len(tables)}", file=sys.stderr)
            for table in sorted(tables):
                print(f"   - {table}", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            
            # Create default admin user if doesn't exist
            print("Checking for default admin user...", file=sys.stderr)
            admin_user = User.query.filter_by(email='admin@example.com').first()
            if not admin_user:
                print("Creating default admin user...", file=sys.stderr)
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    first_name='Admin',
                    last_name='User',
                    is_admin=True,
                    is_verified=True
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created: admin@example.com / admin123", file=sys.stderr)
            else:
                print("✅ Admin user already exists", file=sys.stderr)
            
        except Exception as e:
            print(f"⚠️  Database initialization error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            # Continue app startup - tables might already exist
    
    return app


def register_blueprints(app):
    """
    Register all Flask blueprints with the application.
    
    Args:
        app (Flask): Flask application instance
    """
    # Import and register auth blueprint
    from auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Import and register payment blueprint (Paystack integration)
    from payments.routes import payment_bp
    app.register_blueprint(payment_bp, url_prefix='/payment')
    
    # Import and register SMS blueprint
    from sms import sms_bp
    app.register_blueprint(sms_bp)


def register_template_utilities(app):
    """
    Register template context processors and filters.
    
    Args:
        app (Flask): Flask application instance
    """
    @app.context_processor
    def inject_now():
        """Inject current datetime into all templates."""
        return {'now': datetime.now}
    
    @app.context_processor
    def inject_contact_settings():
        """Inject contact settings into all templates."""
        contact_settings = ContactSettings.get_settings()
        return {'contact_settings': contact_settings}
    
    @app.context_processor
    def utility_processor():
        """Inject utility functions into templates."""
        def remove_filter_url(param_to_remove):
            """Generate URL with specific parameter removed."""
            args = request.args.copy()
            args.pop(param_to_remove, None)
            return url_for('admin_users', **args)
        return dict(remove_filter_url=remove_filter_url)
    
    @app.template_filter('date_equal')
    def date_equal_filter(dt, date_string):
        """Check if datetime date equals target date string."""
        if dt is None:
            return False
        return dt.date() == date_string



def initialize_extensions(app):
    """
    Initialize all Flask extensions with the application.
    
    Args:
        app (Flask): Flask application instance
    """
    # This function is now redundant since we initialize in create_app
    pass


def initialize_email_service():
    """
    Initialize email service - this will run when app starts
    """
    try:
        from emails.service import gmail_service
        show_warnings = os.environ.get('SHOW_EMAIL_WARNINGS', 'true').lower() == 'true'
        
        if gmail_service.service:
            if show_warnings:
                print("✅ Gmail service initialized successfully")
        else:
            if show_warnings:
                print("⚠️ Gmail service not available - email sending disabled")
    except Exception as e:
        if os.environ.get('SHOW_EMAIL_WARNINGS', 'true').lower() == 'true':
            print(f"⚠️ Email service initialization failed: {e}")


# =============================================================================
# APPLICATION INSTANCE
# =============================================================================

app = create_app()


# =============================================================================
# AUTHENTICATION SETUP
# =============================================================================

@login_manager.user_loader
def load_user(user_id):
    """
    Load user by ID for Flask-Login.
    
    Args:
        user_id (str): User ID
        
    Returns:
        User: User instance or None
    """
    with app.app_context():
        return User.query.get(int(user_id))


# =============================================================================
# AUTHENTICATION SETUP
# =============================================================================

@login_manager.user_loader
def load_user(user_id):
    """
    Load user by ID for Flask-Login.
    
    Args:
        user_id (str): User ID
        
    Returns:
        User: User instance or None
    """
    return User.query.get(int(user_id))


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def allowed_file(filename):
    """
    Check if file extension is allowed for upload.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        bool: True if file extension is allowed
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def save_image(file, image_type='product'):
    """
    Save uploaded image with size-specific resizing and unique filename.
    
    Args:
        file (FileStorage): Uploaded file
        image_type (str): Type of image - 'product' (600x600), 'category' (400x200), 
                         'detail' (800x800), 'cart' (200x200), 'recommended' (300x300)
        
    Returns:
        str: Saved filename or None if failed
    """
    # Define optimal sizes for different image types
    image_sizes = {
        'product': (600, 600),
        'category': (400, 200),  # Landscape 2:1 ratio for category cards
        'detail': (800, 800),
        'cart': (200, 200),
        'recommended': (300, 300),
        'default': (800, 800)  # fallback size
    }
    
    if file and allowed_file(file.filename):
        # Create uploads directory if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = secure_filename(file.filename)
        filename = f"{timestamp}_{original_filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            print(f"Image saved to: {filepath}")
            
            # Resize image with size-specific dimensions
            try:
                img = Image.open(filepath)
                target_size = image_sizes.get(image_type, image_sizes['default'])
                
                # Convert RGBA to RGB for JPEG compatibility
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Resize image while maintaining aspect ratio
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
                
                # Create square canvas and center the image
                square_img = Image.new('RGB', target_size, (255, 255, 255))
                offset = ((target_size[0] - img.size[0]) // 2, 
                         (target_size[1] - img.size[1]) // 2)
                square_img.paste(img, offset)
                
                # Save with quality optimization
                quality = 85 if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg') else 90
                square_img.save(filepath, quality=quality, optimize=True)
                
                print(f"Image resized to {target_size} and saved: {filepath}")
            except Exception as e:
                print(f"Image resize failed: {e}")
                # If resize fails, still return the filename (unoptimized)
            
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    return None


def log_user_activity(user, activity_type, description=None, request_obj=None):
    """
    Log user activity to database.
    
    Args:
        user (User): User instance
        activity_type (str): Type of activity
        description (str, optional): Activity description
        request_obj (Request, optional): Flask request object
        
    Returns:
        UserActivity: Created activity record
    """
    ip_address = request_obj.remote_addr if request_obj else None
    user_agent = request_obj.headers.get('User-Agent') if request_obj else None
    
    return user.log_activity(
        activity_type=activity_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_client_ip(request_obj):
    """
    Get client IP address considering proxies.
    
    Args:
        request_obj (Request): Flask request object
        
    Returns:
        str: Client IP address
    """
    if request_obj.headers.get('X-Forwarded-For'):
        return request_obj.headers.get('X-Forwarded-For').split(',')[0]
    return request_obj.remote_addr


# =============================================================================
# IMPORT SERVICE FUNCTIONS
# =============================================================================

from auth.utils import GoogleOAuth, get_google_oauth_url
from emails.service import send_account_status_email, send_welcome_email


# =============================================================================
# PUBLIC ROUTES
# =============================================================================

@app.route('/')
def index():
    """
    Home page route.
    
    Returns:
        Response: Rendered home page
    """
    # Get active hero section
    hero_section = HeroSection.query.filter_by(is_active=True).first()
    
    # Get dynamic messages for homepage
    dynamic_messages = DynamicMessage.get_active_homepage_messages()
    
    # Get system settings for dynamic content
    settings = SystemSettings.get_settings()
    
    # Get categories and products for display
    categories = Category.query.filter_by(is_active=True).all()
    featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    new_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()
    
    return render_template('index.html', 
                         hero_section=hero_section,
                         dynamic_messages=dynamic_messages,
                         settings=settings,
                         categories=categories, 
                         featured_products=featured_products,
                         new_products=new_products)


@app.route('/products')
def products():
    """
    Products listing page with filtering and sorting.
    
    Returns:
        Response: Rendered products page
    """
    # Get dynamic messages for display
    dynamic_messages = DynamicMessage.get_active_homepage_messages()
    
    # Get query parameters
    category_id = request.args.get('category')
    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'newest')
    
    # Build query
    query = Product.query.filter_by(is_active=True)
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    # Apply sorting
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'name':
        query = query.order_by(Product.name.asc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())
    
    # Execute query
    products_list = query.all()
    categories = Category.query.filter_by(is_active=True).all()
    current_category = Category.query.get(category_id) if category_id else None
    
    return render_template('products.html', 
                         products=products_list, 
                         categories=categories,
                         dynamic_messages=dynamic_messages,
                         current_category=current_category,
                         sort_by=sort_by)


@app.route('/category/<int:category_id>')
def category_products(category_id):
    """
    Products by category page.
    
    Args:
        category_id (int): Category ID
        
    Returns:
        Response: Rendered category products page
    """
    # Get dynamic messages for display
    dynamic_messages = DynamicMessage.get_active_homepage_messages()
    
    category = Category.query.get_or_404(category_id)
    products_list = Product.query.filter_by(category_id=category_id, is_active=True).all()
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('category_products.html',
                         category=category,
                         products=products_list,
                         categories=categories,
                         dynamic_messages=dynamic_messages)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """
    Product detail page.
    
    Args:
        product_id (int): Product ID
        
    Returns:
        Response: Rendered product detail page
    """
    # Get dynamic messages for display
    dynamic_messages = DynamicMessage.get_active_homepage_messages()
    
    product = Product.query.get_or_404(product_id)
    if not product.is_active:
        flash('Product not available')
        return redirect(url_for('products'))
    
    # Log product view if user is logged in
    if current_user.is_authenticated:
        log_user_activity(
            current_user,
            'view_product',
            f'Viewed product: {product.name} (ID: {product.id})',
            request
        )
    
    # Get related products
    related_products = Product.query.filter_by(
        category_id=product.category_id, 
        is_active=True
    ).filter(Product.id != product.id).limit(4).all()
    
    return render_template('product_detail.html', 
                         product=product, 
                         related_products=related_products,
                         dynamic_messages=dynamic_messages)


# =============================================================================
# CART ROUTES
# =============================================================================

@app.route('/cart')
@login_required
def cart():
    """
    Shopping cart page with dynamic shipping and tax from settings.
    
    Returns:
        Response: Rendered cart page
    """
    # Get dynamic messages for display
    dynamic_messages = DynamicMessage.get_active_homepage_messages()
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    cart_total = sum(item.product.final_price() * item.quantity for item in cart_items)
    
    # Get system settings for dynamic shipping and tax
    settings = SystemSettings.get_settings()
    
    # Calculate totals with dynamic values
    shipping_cost = settings.standard_shipping_cost  # Default shipping on cart page
    tax_rate = settings.tax_rate * 100  # Convert to percentage for display
    tax_amount = (cart_total + shipping_cost) * settings.tax_rate
    total = cart_total + shipping_cost + tax_amount
    
    # Get shipping days for display
    standard_shipping_days_min = settings.standard_shipping_days_min
    standard_shipping_days_max = settings.standard_shipping_days_max
    
    return render_template('cart.html', 
                         cart_items=cart_items, 
                         cart_total=cart_total,
                         shipping_cost=shipping_cost,
                         shipping_days_min=standard_shipping_days_min,
                         shipping_days_max=standard_shipping_days_max,
                         tax_rate=tax_rate,
                         tax_amount=tax_amount,
                         total=total,
                         dynamic_messages=dynamic_messages)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """
    Add product to cart.
    
    Args:
        product_id (int): Product ID
        
    Returns:
        Response: Redirect to previous page or home
    """
    product = Product.query.get_or_404(product_id)
    if not product.is_active or not product.is_in_stock():
        flash('Product not available')
        return redirect(request.referrer or url_for('index'))
    
    # Find existing cart item or create new one
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        if cart_item.quantity < product.stock_quantity:
            cart_item.quantity += 1
            # Log cart update
            log_user_activity(
                current_user,
                'update_cart',
                f'Increased quantity for {product.name} to {cart_item.quantity}',
                request
            )
        else:
            flash('Not enough stock available')
            return redirect(request.referrer or url_for('index'))
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id)
        db.session.add(cart_item)
        # Log cart addition
        log_user_activity(
            current_user,
            'add_to_cart',
            f'Added {product.name} to cart',
            request
        )
    
    db.session.commit()
    flash('Product added to cart')
    return redirect(request.referrer or url_for('index'))


@app.route('/remove_from_cart/<int:cart_item_id>')
@login_required
def remove_from_cart(cart_item_id):
    """
    Remove item from cart.
    
    Args:
        cart_item_id (int): Cart item ID
        
    Returns:
        Response: Redirect to cart page
    """
    cart_item = CartItem.query.get_or_404(cart_item_id)
    if cart_item.user_id == current_user.id:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Product removed from cart')
    
    return redirect(url_for('cart'))


@app.route('/update_cart_quantity/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart_quantity(cart_item_id):
    """
    Update cart item quantity via AJAX.
    
    Args:
        cart_item_id (int): Cart item ID
        
    Returns:
        JSON: Update result with totals
    """
    cart_item = CartItem.query.get_or_404(cart_item_id)
    if cart_item.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() or {}
    quantity = int(data.get('quantity', 1))
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        if quantity <= cart_item.product.stock_quantity:
            cart_item.quantity = quantity
        else:
            return jsonify({'error': 'Not enough stock'}), 400
    
    db.session.commit()
    
    # Recalculate totals
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.final_price() * item.quantity for item in cart_items)
    
    return jsonify({
        'success': True,
        'item_total': cart_item.product.final_price() * cart_item.quantity,
        'cart_total': total
    })


@app.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    """
    Clear entire shopping cart.
    
    Returns:
        Response: Redirect to cart page with confirmation message
    """
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    log_user_activity(
        current_user,
        'clear_cart',
        'Cleared shopping cart',
        request
    )
    
    flash('Shopping cart cleared')
    return redirect(url_for('cart'))


def calculate_shipping_cost(subtotal, cart_items):
    """
    Calculate shipping cost based on subtotal and cart items.
    Uses settings from database for dynamic shipping costs and delivery times.
    
    Shipping Rules:
    - Free shipping for orders over threshold
    - Standard shipping for mid-range orders
    - Express shipping for time-sensitive deliveries
    
    Args:
        subtotal (float): Order subtotal
        cart_items (list): Cart items
        
    Returns:
        dict: Shipping options with costs and delivery times
    """
    from models import SystemSettings
    settings = SystemSettings.get_settings()
    
    # Helper function to format delivery time
    def format_delivery_time(days_min, days_max, hours_min, hours_max, minutes_min, minutes_max):
        """Format delivery time display"""
        from_time = f"{days_min}d {hours_min:02d}h{minutes_min:02d}m"
        to_time = f"{days_max}d {hours_max:02d}h{minutes_max:02d}m"
        return f"{from_time} - {to_time}"
    
    shipping_options = {
        'free': {
            'label': f'Free Shipping ({format_delivery_time(settings.free_shipping_days_min, settings.free_shipping_days_max, settings.free_shipping_hours_min, settings.free_shipping_hours_max, settings.free_shipping_minutes_min, settings.free_shipping_minutes_max)})',
            'cost': 0.00,
            'min_subtotal': settings.free_shipping_threshold,
            'days_min': settings.free_shipping_days_min,
            'days_max': settings.free_shipping_days_max,
            'hours_min': settings.free_shipping_hours_min,
            'hours_max': settings.free_shipping_hours_max,
            'minutes_min': settings.free_shipping_minutes_min,
            'minutes_max': settings.free_shipping_minutes_max
        },
        'standard': {
            'label': f'Standard Shipping ({format_delivery_time(settings.standard_shipping_days_min, settings.standard_shipping_days_max, settings.standard_shipping_hours_min, settings.standard_shipping_hours_max, settings.standard_shipping_minutes_min, settings.standard_shipping_minutes_max)}) - GH₵ {settings.standard_shipping_cost:.2f}',
            'cost': settings.standard_shipping_cost,
            'min_subtotal': 0.00,
            'days_min': settings.standard_shipping_days_min,
            'days_max': settings.standard_shipping_days_max,
            'hours_min': settings.standard_shipping_hours_min,
            'hours_max': settings.standard_shipping_hours_max,
            'minutes_min': settings.standard_shipping_minutes_min,
            'minutes_max': settings.standard_shipping_minutes_max
        },
        'express': {
            'label': f'Express Shipping ({format_delivery_time(settings.express_shipping_days_min, settings.express_shipping_days_max, settings.express_shipping_hours_min, settings.express_shipping_hours_max, settings.express_shipping_minutes_min, settings.express_shipping_minutes_max)}) - GH₵ {settings.express_shipping_cost:.2f}',
            'cost': settings.express_shipping_cost,
            'min_subtotal': 0.00,
            'days_min': settings.express_shipping_days_min,
            'days_max': settings.express_shipping_days_max,
            'hours_min': settings.express_shipping_hours_min,
            'hours_max': settings.express_shipping_hours_max,
            'minutes_min': settings.express_shipping_minutes_min,
            'minutes_max': settings.express_shipping_minutes_max
        }
    }
    
    # Determine applicable shipping options based on subtotal
    applicable_options = {}
    for method, details in shipping_options.items():
        if subtotal >= details['min_subtotal']:
            applicable_options[method] = details
    
    return applicable_options


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """
    Checkout page for order placement with professional shipping calculation.
    
    GET: Display checkout form with shipping options
    POST: Process order placement
    
    Returns:
        Response: Rendered checkout page or redirect to confirmation
    """
    from models import SystemSettings
    
    # Get dynamic messages for display
    dynamic_messages = DynamicMessage.get_active_homepage_messages()
    
    # Verify user has verified email
    if not current_user.is_verified:
        flash('Please verify your email before checkout', 'danger')
        return redirect(url_for('cart'))
    
    # Get cart items
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('products'))
    
    if request.method == 'GET':
        # Get system settings
        settings = SystemSettings.get_settings()
        
        # Calculate totals
        subtotal = sum(item.product.final_price() * item.quantity for item in cart_items)
        
        # Get applicable shipping options
        shipping_options = calculate_shipping_cost(subtotal, cart_items)
        
        # Default to cheapest available option
        default_shipping = min(shipping_options.items(), key=lambda x: x[1]['cost'])
        default_method = default_shipping[0]
        shipping_cost = default_shipping[1]['cost']
        
        discount_amount = 0  # Add discount logic if needed
        tax = subtotal * settings.tax_rate  # Use tax rate from settings
        total = subtotal + shipping_cost + tax - discount_amount
        
        return render_template(
            'checkout.html',
            cart_items=cart_items,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            shipping_options=shipping_options,
            selected_shipping=default_method,
            discount_amount=discount_amount,
            tax=tax,
            tax_rate=settings.tax_rate * 100,
            total=total,
            dynamic_messages=dynamic_messages
        )
    
    # POST - Process order
    # Get JSON data - use cache=False to allow multiple reads
    app.logger.debug(f"Request Content-Type: {request.content_type}")
    app.logger.debug(f"Request method: {request.method}")
    app.logger.debug(f"Request data length: {len(request.data)}")
    
    try:
        data = request.get_json(force=True, cache=False)
    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"JSON parsing error: {e}, Content-Type: {request.content_type}")
        app.logger.debug(f"Raw request body: {request.data}")
        # If JSON parsing fails and we got form data instead, use form data
        if request.form:
            data = request.form.to_dict()
            app.logger.debug(f"Using form data instead: {data}")
        else:
            data = {}
    
    # Debug: log what we received
    app.logger.debug(f"Received data: {data}")
    
    # Get system settings
    settings = SystemSettings.get_settings()
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'postal_code', 'payment_method', 'shipping_method']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400
    
    # Calculate order totals with selected shipping method
    subtotal = sum(item.product.final_price() * item.quantity for item in cart_items)
    shipping_options = calculate_shipping_cost(subtotal, cart_items)
    
    # Validate shipping method
    selected_shipping = data.get('shipping_method')
    if selected_shipping not in shipping_options:
        return jsonify({'success': False, 'message': 'Invalid shipping method selected'}), 400
    
    shipping_cost = shipping_options[selected_shipping]['cost']
    discount_amount = 0
    tax = subtotal * settings.tax_rate  # Use tax rate from settings
    total = subtotal + shipping_cost + tax - discount_amount
    
    # Create order
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    payment_method = data.get('payment_method')
    
    # Determine payment status based on payment method
    if payment_method == 'cod':
        payment_status = 'pending'  # COD - pending until delivery
    else:
        payment_status = 'unpaid'  # Other methods - will be marked paid after successful payment
    
    order = Order(
        user_id=current_user.id,
        order_number=order_number,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        discount_amount=discount_amount,
        discount_percentage=0,
        total_amount=total,
        status='pending',
        payment_method=payment_method,
        payment_status=payment_status,
        shipping_first_name=data.get('first_name'),
        shipping_last_name=data.get('last_name'),
        shipping_address=data.get('address'),
        shipping_city=data.get('city'),
        shipping_postal_code=data.get('postal_code'),
        shipping_phone=data.get('phone'),
        notes=data.get('notes', '')
    )
    
    # Add order items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=None,  # Will be set after order is committed
            product_id=cart_item.product_id,
            product_name=cart_item.product.name,
            quantity=cart_item.quantity,
            unit_price=cart_item.product.final_price(),
            total_price=cart_item.product.final_price() * cart_item.quantity
        )
        order.order_items.append(order_item)
    
    db.session.add(order)
    db.session.commit()
    
    # Save user's shipping info for future orders
    current_user.first_name = data.get('first_name')
    current_user.last_name = data.get('last_name')
    current_user.address = data.get('address')
    current_user.city = data.get('city')
    current_user.postal_code = data.get('postal_code')
    db.session.commit()
    
    # Clear cart
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    # Log activity
    log_user_activity(
        current_user,
        'place_order',
        f'Placed order {order_number} for GH₵ {total:.2f}',
        request
    )
    
    # Handle different payment methods
    if payment_method == 'cod':
        # Cash on Delivery - no online payment needed
        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order_id': order.id,
            'order_number': order.order_number,
            'payment_method': 'cod',
            'redirect_url': url_for('order_confirmation', order_id=order.id)
        })
    
    elif payment_method == 'paystack':
        # Paystack online payment
        try:
            from payments.paystack_gateway import PaystackGateway
            from models import Payment, PaymentLog
            import uuid
            
            # Initialize Paystack gateway
            gateway = PaystackGateway()
            
            # Generate unique reference
            paystack_reference = f"ORDER-{order.id}-{uuid.uuid4().hex[:8]}"
            
            # Metadata to store with payment
            metadata = {
                'order_id': order.id,
                'user_id': current_user.id,
                'order_number': order_number
            }
            
            # Initialize payment with Paystack
            paystack_response = gateway.initialize_payment(
                email=current_user.email,
                amount=total,
                reference=paystack_reference,
                metadata=metadata
            )
            
            if not paystack_response['success']:
                error_msg = paystack_response.get('error', 'Payment initialization failed')
                current_app.logger.error(f'Paystack initialization failed: {error_msg}')
                return jsonify({
                    'success': False,
                    'message': 'Failed to initiate payment. Please try again.'
                }), 500
            
            # Create payment record
            payment = Payment(
                order_id=order.id,
                customer_email=current_user.email,
                customer_phone=getattr(current_user, 'phone_number', None),
                amount=total,
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
            
            current_app.logger.info(f'Paystack payment initiated: {paystack_reference} for order {order.id}')
            
            # Return Paystack authorization URL
            return jsonify({
                'success': True,
                'message': 'Payment initialization successful',
                'order_id': order.id,
                'order_number': order.order_number,
                'payment_method': 'paystack',
                'authorization_url': paystack_response['authorization_url'],
                'reference': paystack_reference,
                'access_code': paystack_response.get('access_code')
            })
        
        except Exception as e:
            current_app.logger.error(f'Paystack payment error: {str(e)}', exc_info=True)
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': 'Failed to initialize payment. Please try again.'
            }), 500
    
    else:  # bank_transfer, mobile_money (manual)
        # For now, treat these as manual payment methods
        order.payment_status = 'pending'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order_id': order.id,
            'order_number': order.order_number,
            'payment_method': payment_method,
            'redirect_url': url_for('order_confirmation', order_id=order.id)
        })


@app.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    """
    Order confirmation page.
    
    Args:
        order_id (int): Order ID
        
    Returns:
        Response: Rendered order confirmation page
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify user owns this order
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get recommended products
    recommended_products = Product.query.filter(
        Product.is_active == True,
        Product.id.notin_([item.product_id for item in order.order_items])
    ).limit(4).all()
    
    return render_template('order_confirmation.html', order=order, recommended_products=recommended_products)


@app.route('/payment-confirmed/<reference>')
def payment_confirmed(reference):
    """
    Payment confirmation page after successful Paystack payment.
    
    Args:
        reference (str): Paystack payment reference
        
    Returns:
        Response: Rendered payment status page
    """
    from models import Payment
    
    try:
        # Get payment record
        payment = Payment.query.filter_by(paystack_reference=reference).first()
        
        if not payment:
            flash('Payment record not found', 'warning')
            return redirect(url_for('index'))
        
        # Verify user owns this payment
        if payment.order.user_id != current_user.id and not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('index'))
        
        # Get order
        order = payment.order
        
        return render_template(
            'payment_status.html',
            payment=payment,
            order=order,
            reference=reference,
            payment_status='success' if payment.status == 'success' else payment.status,
            config=current_app.config
        )
    
    except Exception as e:
        current_app.logger.error(f'Payment confirmation error: {str(e)}')
        flash('Error retrieving payment information', 'danger')
        return redirect(url_for('index'))


# =============================================================================
# PRODUCT REVIEW ROUTES
# =============================================================================

@app.route('/product/<int:product_id>/reviews', methods=['GET'])
def get_product_reviews(product_id):
    """
    Get paginated list of approved reviews for a product (AJAX endpoint).
    
    Args:
        product_id (int): Product ID
        
    Returns:
        JSON: Reviews list with pagination info
    """
    product = Product.query.get_or_404(product_id)
    
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'recent')  # recent, helpful, rating_high, rating_low
    rating_filter = request.args.get('rating', 'all')  # all, 5, 4, 3, 2, 1
    
    query = ProductReview.query.filter_by(product_id=product_id, is_approved=True)
    
    # Filter by rating
    if rating_filter != 'all':
        query = query.filter_by(rating=int(rating_filter))
    
    # Sort by
    if sort_by == 'helpful':
        query = query.order_by(ProductReview.helpful_count.desc(), ProductReview.created_at.desc())
    elif sort_by == 'rating_high':
        query = query.order_by(ProductReview.rating.desc(), ProductReview.created_at.desc())
    elif sort_by == 'rating_low':
        query = query.order_by(ProductReview.rating.asc(), ProductReview.created_at.desc())
    else:  # recent (default)
        query = query.order_by(ProductReview.created_at.desc())
    
    # Paginate
    reviews_pagination = query.paginate(page=page, per_page=5)
    reviews = reviews_pagination.items
    
    # Calculate review stats
    all_reviews = ProductReview.query.filter_by(product_id=product_id, is_approved=True).all()
    total_reviews = len(all_reviews)
    avg_rating = sum(r.rating for r in all_reviews) / total_reviews if total_reviews > 0 else 0
    rating_distribution = {
        5: len([r for r in all_reviews if r.rating == 5]),
        4: len([r for r in all_reviews if r.rating == 4]),
        3: len([r for r in all_reviews if r.rating == 3]),
        2: len([r for r in all_reviews if r.rating == 2]),
        1: len([r for r in all_reviews if r.rating == 1]),
    }
    
    reviews_data = [
        {
            'id': r.id,
            'user_name': r.user.username,
            'rating': r.rating,
            'title': r.title,
            'content': r.content,
            'helpful_count': r.helpful_count,
            'created_at': r.created_at.strftime('%B %d, %Y'),
            'is_verified_purchase': has_user_purchased_product(r.user_id, product_id)
        }
        for r in reviews
    ]
    
    return jsonify({
        'success': True,
        'reviews': reviews_data,
        'pagination': {
            'page': page,
            'total_pages': reviews_pagination.pages,
            'total_reviews': total_reviews,
            'per_page': 5
        },
        'stats': {
            'average_rating': round(avg_rating, 1),
            'total_reviews': total_reviews,
            'rating_distribution': rating_distribution
        }
    })


@app.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def submit_review(product_id):
    """
    Submit a new product review.
    
    Args:
        product_id (int): Product ID
        
    Returns:
        JSON: Success message or error
    """
    product = Product.query.get_or_404(product_id)
    
    # Check if user has purchased this product
    if not has_user_purchased_product(current_user.id, product_id):
        return jsonify({
            'success': False,
            'message': 'You can only review products you have purchased'
        }), 403
    
    # Check if user already reviewed this product
    existing_review = ProductReview.query.filter_by(
        product_id=product_id,
        user_id=current_user.id
    ).first()
    
    if existing_review:
        return jsonify({
            'success': False,
            'message': 'You have already reviewed this product. Edit your review or delete it first.'
        }), 400
    
    # Validate input
    try:
        data = request.get_json(force=True, cache=False)
    except Exception as e:
        app.logger.error(f"JSON parsing error: {e}")
        data = {}
    
    rating = data.get('rating')
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    
    # Validation
    if not rating or rating < 1 or rating > 5:
        return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400
    
    if not title or len(title) < 5:
        return jsonify({'success': False, 'message': 'Title must be at least 5 characters'}), 400
    
    if not content or len(content) < 20:
        return jsonify({'success': False, 'message': 'Review must be at least 20 characters'}), 400
    
    if len(title) > 200:
        return jsonify({'success': False, 'message': 'Title must not exceed 200 characters'}), 400
    
    if len(content) > 5000:
        return jsonify({'success': False, 'message': 'Review must not exceed 5000 characters'}), 400
    
    # Create review
    review = ProductReview(
        product_id=product_id,
        user_id=current_user.id,
        rating=int(rating),
        title=title,
        content=content,
        is_approved=False  # Requires admin approval by default
    )
    
    db.session.add(review)
    db.session.commit()
    
    # Log activity
    log_user_activity(
        current_user,
        'submit_review',
        f'Submitted review for product {product.name} (Rating: {rating}/5)',
        request
    )
    
    return jsonify({
        'success': True,
        'message': 'Review submitted successfully. It will be displayed after admin approval.',
        'review_id': review.id
    })


@app.route('/review/<int:review_id>/helpful', methods=['POST'])
def mark_review_helpful(review_id):
    """
    Mark a review as helpful (increment helpful count).
    
    Args:
        review_id (int): Review ID
        
    Returns:
        JSON: Updated helpful count
    """
    review = ProductReview.query.get_or_404(review_id)
    
    # Increment helpful count
    review.helpful_count += 1
    db.session.commit()
    
    return jsonify({
        'success': True,
        'helpful_count': review.helpful_count,
        'message': 'Thank you for your feedback!'
    })


@app.route('/review/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    """
    Delete a review (user can only delete their own, admins can delete any).
    
    Args:
        review_id (int): Review ID
        
    Returns:
        JSON: Success message
    """
    review = ProductReview.query.get_or_404(review_id)
    
    # Check permissions
    if review.user_id != current_user.id and not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'You can only delete your own reviews'
        }), 403
    
    product_name = review.product.name
    db.session.delete(review)
    db.session.commit()
    
    # Log activity
    log_user_activity(
        current_user,
        'delete_review',
        f'Deleted review for product {product_name}',
        request
    )
    
    return jsonify({
        'success': True,
        'message': 'Review deleted successfully'
    })


@app.route('/review/<int:review_id>', methods=['PUT'])
@login_required
def edit_review(review_id):
    """
    Edit a review (user can only edit their own).
    
    Args:
        review_id (int): Review ID
        
    Returns:
        JSON: Success message
    """
    review = ProductReview.query.get_or_404(review_id)
    
    # Check permissions
    if review.user_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'You can only edit your own reviews'
        }), 403
    
    # Get data
    try:
        data = request.get_json(force=True, cache=False)
    except Exception as e:
        app.logger.error(f"JSON parsing error: {e}")
        data = {}
    
    rating = data.get('rating')
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    
    # Validation
    if not rating or rating < 1 or rating > 5:
        return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400
    
    if not title or len(title) < 5:
        return jsonify({'success': False, 'message': 'Title must be at least 5 characters'}), 400
    
    if not content or len(content) < 20:
        return jsonify({'success': False, 'message': 'Review must be at least 20 characters'}), 400
    
    if len(title) > 200:
        return jsonify({'success': False, 'message': 'Title must not exceed 200 characters'}), 400
    
    if len(content) > 5000:
        return jsonify({'success': False, 'message': 'Review must not exceed 5000 characters'}), 400
    
    # Update review
    review.rating = int(rating)
    review.title = title
    review.content = content
    review.updated_at = datetime.now()
    review.is_approved = False  # Re-moderate after edit
    db.session.commit()
    
    # Log activity
    log_user_activity(
        current_user,
        'edit_review',
        f'Edited review for product {review.product.name}',
        request
    )
    
    return jsonify({
        'success': True,
        'message': 'Review updated successfully. It will be re-reviewed by admin.'
    })


# Helper function to check if user has purchased a product
def has_user_purchased_product(user_id, product_id):
    """
    Check if a user has purchased a specific product.
    
    Args:
        user_id (int): User ID
        product_id (int): Product ID
        
    Returns:
        bool: True if user has purchased, False otherwise
    """
    from sqlalchemy import and_
    
    order_item = db.session.query(OrderItem).join(
        Order, OrderItem.order.has(user_id=user_id)
    ).filter(
        OrderItem.product_id == product_id,
        Order.status.in_(['completed', 'shipped', 'processing', 'delivered', 'confirmed'])
    ).first()
    
    return order_item is not None


@app.route('/account/orders')
@login_required
def view_orders():
    """
    User's order history page.
    
    Returns:
        Response: Rendered orders list page
    """
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('order_history.html', orders=orders)


@app.route('/account/order/<int:order_id>')
@login_required
def order_detail(order_id):
    """
    Order detail page.
    
    Args:
        order_id (int): Order ID
        
    Returns:
        Response: Rendered order detail page
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify user owns this order
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    return render_template('order_detail.html', order=order)


@app.route('/account/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """
    Cancel an order.
    
    Args:
        order_id (int): Order ID
        
    Returns:
        JSON: Cancellation result
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify user owns this order
    if order.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Check if order can be cancelled
    if order.status not in ['pending', 'confirmed']:
        return jsonify({
            'success': False,
            'message': f'Cannot cancel order in {order.status} status'
        }), 400
    
    # Cancel the order
    order.status = 'cancelled'
    db.session.commit()
    
    # Log activity
    log_user_activity(
        current_user,
        'cancel_order',
        f'Cancelled order {order.order_number}',
        request
    )
    
    return jsonify({
        'success': True,
        'message': 'Order cancelled successfully'
    })


@app.route('/account/order/<int:order_id>/review', methods=['POST'])
@login_required
def order_review(order_id):
    """
    Submit review for delivered order.
    
    Args:
        order_id (int): Order ID
        
    Returns:
        JSON: Review submission result
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify user owns this order
    if order.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Check if order is delivered
    if order.status != 'delivered':
        return jsonify({
            'success': False,
            'message': 'You can only review delivered orders'
        }), 400
    
    try:
        data = request.get_json(force=True, cache=False)
    except Exception as e:
        app.logger.error(f"JSON parsing error: {e}")
        data = {}
    
    rating = int(data.get('rating', 0))
    comment = data.get('comment', '')
    
    if not (1 <= rating <= 5) or not comment:
        return jsonify({
            'success': False,
            'message': 'Invalid rating or comment'
        }), 400
    
    # Create a review for each product in the order
    reviews_created = 0
    for item in order.order_items:
        # Check if user already reviewed this product
        existing_review = ProductReview.query.filter_by(
            product_id=item.product_id,
            user_id=current_user.id
        ).first()
        
        if not existing_review:
            review = ProductReview(
                product_id=item.product_id,
                user_id=current_user.id,
                rating=rating,
                title=f'Review from Order {order.order_number}',
                content=comment,
                is_approved=False
            )
            db.session.add(review)
            reviews_created += 1
    
    if reviews_created > 0:
        db.session.commit()
    
    # Log activity
    log_user_activity(
        current_user,
        'leave_review',
        f'Left {rating}★ review for order {order.order_number} ({reviews_created} product(s)): {comment[:50]}...',
        request
    )
    
    return jsonify({
        'success': True,
        'message': f'Review submitted successfully for {reviews_created} product(s)'
    })


# =============================================================================
# ADMIN DASHBOARD ROUTES
# =============================================================================

@app.route('/admin')
@login_required
def admin_dashboard():
    """
    Admin dashboard with statistics.
    
    Returns:
        Response: Rendered admin dashboard
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Gather statistics (only paid, non-cancelled orders count as revenue)
    stats = {
        'total_products': Product.query.count(),
        'total_orders': Order.query.filter(and_(Order.status != 'cancelled', Order.payment_status == 'paid')).count(),
        'total_users': User.query.count(),
        'total_categories': Category.query.count(),
        'revenue': db.session.query(db.func.sum(Order.total_amount)).filter(and_(Order.status != 'cancelled', Order.payment_status == 'paid')).scalar() or 0
    }
    
    # Get recent data
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    low_stock_products = Product.query.filter(Product.stock_quantity <= 5).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_orders=recent_orders,
                         low_stock_products=low_stock_products)


@app.route('/admin/analytics')
@login_required
def admin_analytics():
    """
    Advanced analytics dashboard with sales trends, top products,
    customer demographics, and conversion funnel analysis.
    
    Returns:
        Response: Rendered analytics page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Import analytics helpers
    from analytics_helpers import (
        get_sales_trends, get_top_products, get_customer_demographics,
        get_conversion_funnel, get_revenue_by_category, get_order_status_breakdown,
        get_monthly_trends
    )
    
    # Get time period filter (default: 30 days)
    time_period = request.args.get('time_period', '30')
    try:
        time_period = int(time_period)
    except:
        time_period = 30
    
    # Gather all analytics data
    analytics_data = {
        'sales_trends': get_sales_trends(time_period),
        'monthly_trends': get_monthly_trends(12),
        'top_products': get_top_products(10),
        'top_categories': get_revenue_by_category(10),
        'customer_demographics': get_customer_demographics(),
        'conversion_funnel': get_conversion_funnel(),
        'order_status_breakdown': get_order_status_breakdown(),
        'time_period': time_period
    }
    
    return render_template('admin/analytics.html', analytics=analytics_data)


# =============================================================================
# ADMIN USER MANAGEMENT ROUTES
# =============================================================================

@app.route('/admin/users')
@login_required
def admin_users():
    """
    User management page with advanced filtering.
    
    Returns:
        Response: Rendered users management page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get filter parameters
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    role_filter = request.args.get('role', 'all')
    sort_by = request.args.get('sort_by', 'newest')
    date_filter = request.args.get('date_filter', 'all')
    
    # Build query
    query = User.query
    
    # Apply search filter
    if search_query:
        if search_query.isdigit():
            query = query.filter(User.id == int(search_query))
        else:
            query = query.filter(
                db.or_(
                    User.username.ilike(f'%{search_query}%'),
                    User.email.ilike(f'%{search_query}%')
                )
            )
    
    # Apply status filter
    if status_filter == 'active':
        query = query.filter(User.is_active == True)
    elif status_filter == 'inactive':
        query = query.filter(User.is_active == False)
    
    # Apply role filter
    if role_filter == 'admin':
        query = query.filter(User.is_admin == True)
    elif role_filter == 'user':
        query = query.filter(User.is_admin == False)
    
    # Apply date filter
    today = datetime.now().date()
    if date_filter == 'today':
        query = query.filter(db.func.date(User.created_at) == today)
    elif date_filter == 'week':
        week_ago = today - timedelta(days=7)
        query = query.filter(User.created_at >= week_ago)
    elif date_filter == 'month':
        month_ago = today - timedelta(days=30)
        query = query.filter(User.created_at >= month_ago)
    
    # Apply sorting
    if sort_by == 'name':
        query = query.order_by(User.username.asc())
    elif sort_by == 'newest':
        query = query.order_by(User.created_at.desc())
    elif sort_by == 'oldest':
        query = query.order_by(User.created_at.asc())
    elif sort_by == 'last_login':
        query = query.order_by(User.last_login.desc())
    else:
        query = query.order_by(User.created_at.desc())
    
    users = query.all()
    
    # Get statistics for display
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(is_admin=True).count()
    today_users = User.query.filter(db.func.date(User.created_at) == today).count()
    
    return render_template('admin/users.html', 
                         users=users,
                         today=today,
                         search_query=search_query,
                         status_filter=status_filter,
                         role_filter=role_filter,
                         sort_by=sort_by,
                         date_filter=date_filter,
                         total_users=total_users,
                         active_users=active_users,
                         admin_users=admin_users,
                         today_users=today_users)


@app.route('/admin/users/<int:user_id>')
@login_required
def admin_view_user(user_id):
    """
    User detail page for administrators.
    
    Args:
        user_id (int): User ID
        
    Returns:
        Response: Rendered user detail page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    return render_template('admin/view_user.html', user=user)


@app.route('/admin/users/toggle_admin/<int:user_id>')
@login_required
def admin_toggle_admin(user_id):
    """
    Toggle admin privileges for a user.
    
    Args:
        user_id (int): User ID
        
    Returns:
        Response: Redirect to users management page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent self-demotion
    if user.id == current_user.id:
        flash('You cannot change your own admin status')
        return redirect(url_for('admin_users'))
    
    # Toggle admin status
    user.is_admin = not user.is_admin
    db.session.commit()
    
    # Log action and send email
    log_user_activity(
        current_user,
        'admin_action',
        f'{"Granted" if user.is_admin else "Revoked"} admin privileges for user {user.username} (ID: {user.id})',
        request
    )
    
    if user.is_admin:
        send_account_status_email(user, 'admin_granted', current_user)
    else:
        send_account_status_email(user, 'admin_revoked', current_user)
    
    status = "admin" if user.is_admin else "regular user"
    flash(f'{user.username} is now a {status}')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/toggle_active/<int:user_id>')
@login_required
def admin_toggle_active(user_id):
    """
    Toggle active status for a user.
    
    Args:
        user_id (int): User ID
        
    Returns:
        Response: Redirect to users management page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deactivation
    if user.id == current_user.id:
        flash('You cannot deactivate your own account')
        return redirect(url_for('admin_users'))
    
    # Toggle active status
    user.is_active = not user.is_active
    db.session.commit()
    
    # Log action and send email
    log_user_activity(
        current_user,
        'admin_action',
        f'{"Activated" if user.is_active else "Deactivated"} user {user.username} (ID: {user.id})',
        request
    )
    
    if user.is_active:
        send_account_status_email(user, 'activated', current_user)
    else:
        send_account_status_email(user, 'deactivated', current_user)
    
    status = "activated" if user.is_active else "deactivated"
    flash(f'{user.username} has been {status}')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/verify/<int:user_id>', methods=['POST'])
@login_required
def admin_verify_user(user_id):
    """
    Manually verify a user account.
    
    Args:
        user_id (int): User ID
        
    Returns:
        Response: Redirect to user detail page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Check if already verified
    if user.is_verified:
        flash(f'{user.username} is already verified')
        return redirect(url_for('admin_user_detail', user_id=user_id))
    
    # Mark user as verified
    user.is_verified = True
    user.verified_at = datetime.utcnow()
    
    # Mark any existing verification tokens as used
    from models import EmailToken
    EmailToken.query.filter_by(
        user_id=user.id,
        token_type='email_verification'
    ).update({'used_at': datetime.utcnow()})
    
    db.session.commit()
    
    # Log action and send email
    log_user_activity(
        current_user,
        'admin_action',
        f'Manually verified user {user.username} (ID: {user_id})',
        request
    )
    
    send_account_status_email(user, 'admin_verified', current_user)
    
    flash(f'{user.username} has been manually verified')
    return redirect(url_for('admin_view_user', user_id=user_id))


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """
    Delete a user account.
    
    Args:
        user_id (int): User ID
        
    Returns:
        Response: Redirect to users management page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account')
        return redirect(url_for('admin_users'))
    
    # Check if user has orders
    if user.orders:
        flash(f'Cannot delete {user.username} because they have order history')
        return redirect(url_for('admin_users'))
    
    # Delete user activity records first (to avoid foreign key constraint issues)
    UserActivity.query.filter_by(user_id=user.id).delete()
    
    # Delete user
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} has been deleted')
    return redirect(url_for('admin_users'))


# =============================================================================
# ADMIN BULK USER OPERATIONS
# =============================================================================

@app.route('/api/admin/users/bulk_activate', methods=['POST'])
@login_required
def api_bulk_activate_users():
    """
    Bulk activate users via API.
    
    Expected JSON: {'user_ids': [1, 2, 3, ...]}
    
    Returns:
        JSON response with success/failure details
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json(force=True, cache=False)
    except Exception as e:
        app.logger.error(f"JSON parsing error: {e}")
        data = {}
    
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return jsonify({'success': False, 'message': 'No users selected'}), 400
    
    try:
        # Prevent admin from activating themselves
        user_ids = [uid for uid in user_ids if uid != current_user.id]
        
        if not user_ids:
            return jsonify({'success': False, 'message': 'Cannot activate your own account'}), 400
        
        # Update users
        users = User.query.filter(User.id.in_(user_ids)).all()
        activated_count = 0
        
        for user in users:
            if not user.is_active:
                user.is_active = True
                activated_count += 1
                
                # Log action
                log_user_activity(
                    current_user,
                    'admin_action',
                    f'Bulk activated user {user.username} (ID: {user.id})',
                    request
                )
                
                # Send email notification
                try:
                    send_account_status_email(user, 'activated', current_user)
                except:
                    pass  # Continue even if email fails
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{activated_count} user(s) activated successfully',
            'activated_count': activated_count
        }), 200
        
    except Exception as e:
        print(f"Error in bulk activation: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/admin/users/bulk_deactivate', methods=['POST'])
@login_required
def api_bulk_deactivate_users():
    """
    Bulk deactivate users via API.
    
    Expected JSON: {'user_ids': [1, 2, 3, ...]}
    
    Returns:
        JSON response with success/failure details
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json(force=True, cache=False)
    except Exception as e:
        app.logger.error(f"JSON parsing error: {e}")
        data = {}
    
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return jsonify({'success': False, 'message': 'No users selected'}), 400
    
    try:
        # Prevent admin from deactivating themselves
        user_ids = [uid for uid in user_ids if uid != current_user.id]
        
        if not user_ids:
            return jsonify({'success': False, 'message': 'Cannot deactivate your own account'}), 400
        
        # Update users
        users = User.query.filter(User.id.in_(user_ids)).all()
        deactivated_count = 0
        
        for user in users:
            if user.is_active:
                user.is_active = False
                deactivated_count += 1
                
                # Log action
                log_user_activity(
                    current_user,
                    'admin_action',
                    f'Bulk deactivated user {user.username} (ID: {user.id})',
                    request
                )
                
                # Send email notification
                try:
                    send_account_status_email(user, 'deactivated', current_user)
                except:
                    pass  # Continue even if email fails
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{deactivated_count} user(s) deactivated successfully',
            'deactivated_count': deactivated_count
        }), 200
        
    except Exception as e:
        print(f"Error in bulk deactivation: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/admin/users/bulk_delete', methods=['POST'])
@login_required
def api_bulk_delete_users():
    """
    Bulk delete users via API (only those without orders).
    
    Expected JSON: {'user_ids': [1, 2, 3, ...]}
    
    Returns:
        JSON response with success/failure details
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json(force=True, cache=False)
    except Exception as e:
        app.logger.error(f"JSON parsing error: {e}")
        data = {}
    
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return jsonify({'success': False, 'message': 'No users selected'}), 400
    
    try:
        # Prevent admin from deleting themselves
        user_ids = [uid for uid in user_ids if uid != current_user.id]
        
        if not user_ids:
            return jsonify({'success': False, 'message': 'Cannot delete your own account'}), 400
        
        # Get users and check if any have orders
        users = User.query.filter(User.id.in_(user_ids)).all()
        deletable_users = []
        protected_users = []
        
        for user in users:
            if user.orders:
                protected_users.append(user.username)
            else:
                deletable_users.append(user)
        
        deleted_count = 0
        
        for user in deletable_users:
            # Delete user activity records first
            UserActivity.query.filter_by(user_id=user.id).delete()
            
            username = user.username
            db.session.delete(user)
            deleted_count += 1
            
            # Log action
            log_user_activity(
                current_user,
                'admin_action',
                f'Bulk deleted user {username} (ID: {user.id})',
                request
            )
        
        db.session.commit()
        
        message = f'{deleted_count} user(s) deleted successfully'
        if protected_users:
            message += f'. {len(protected_users)} user(s) protected (have order history): {", ".join(protected_users)}'
        
        return jsonify({
            'success': True,
            'message': message,
            'deleted_count': deleted_count,
            'protected_count': len(protected_users)
        }), 200
        
    except Exception as e:
        print(f"Error in bulk deletion: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# =============================================================================
# ADMIN PRODUCT MANAGEMENT ROUTES
# =============================================================================

@app.route('/admin/products')
@login_required
def admin_products():
    """
    Product management page.
    
    Returns:
        Response: Rendered products management page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    category_id = request.args.get('category')
    query = Product.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    products_list = query.all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products_list, categories=categories)


@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    """
    Add new product page.
    
    Returns:
        Response: Rendered add product form or redirect to products list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price'))
            discount_price = float(request.form.get('discount_price')) if request.form.get('discount_price') else None
            stock_quantity = int(request.form.get('stock_quantity'))
            category_id = int(request.form.get('category_id'))
            is_featured = 'is_featured' in request.form
            is_active = 'is_active' in request.form
            
            # Validate discount price
            if discount_price is not None and discount_price >= price:
                flash('Discount price must be less than regular price', 'danger')
                return redirect(request.url)
            
            # Validate image upload
            if 'image' not in request.files:
                flash('No image file selected')
                return redirect(request.url)
            
            image_file = request.files['image']
            
            if image_file.filename == '':
                flash('No image selected')
                return redirect(request.url)
            
            # Create product
            product = Product(
                name=name,
                description=description,
                price=price,
                discount_price=discount_price,
                stock_quantity=stock_quantity,
                category_id=category_id,
                is_featured=is_featured,
                is_active=is_active
            )
            
            # Save image
            filename = save_image(image_file, image_type='product')
            if filename:
                product.image = filename
                flash(f'Product added successfully with image: {filename}')
            else:
                flash('Product added but image upload failed', 'warning')
            
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully')
            return redirect(url_for('admin_products'))
            
        except Exception as e:
            flash(f'Error adding product: {str(e)}')
            db.session.rollback()
    
    categories = Category.query.all()
    return render_template('admin/add_product.html', categories=categories)


@app.route('/admin/products/view/<int:product_id>')
@login_required
def admin_view_product(product_id):
    """
    Product detail page for administrators.
    
    Args:
        product_id (int): Product ID
        
    Returns:
        Response: Rendered product detail page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    return render_template('admin/view_product.html', product=product)


@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    """
    Edit product page.
    
    Args:
        product_id (int): Product ID
        
    Returns:
        Response: Rendered edit product form or redirect to products list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        # Update product data
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        price = float(request.form.get('price'))
        discount_price = float(request.form.get('discount_price')) if request.form.get('discount_price') else None
        
        # Validate discount price
        if discount_price is not None and discount_price >= price:
            flash('Discount price must be less than regular price', 'danger')
            return redirect(request.url)
        
        product.price = price
        product.discount_price = discount_price
        product.stock_quantity = int(request.form.get('stock_quantity'))
        product.category_id = int(request.form.get('category_id'))
        product.is_featured = 'is_featured' in request.form
        product.is_active = 'is_active' in request.form
        
        # Handle image update
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                filename = save_image(image_file, image_type='product')
                if filename:
                    # Delete old image if exists
                    if product.image and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], product.image)):
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
                    product.image = filename
        
        db.session.commit()
        flash('Product updated successfully')
        return redirect(url_for('admin_products'))
    
    categories = Category.query.all()
    return render_template('admin/edit_product.html', product=product, categories=categories)


@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    """
    Delete a product.
    
    Args:
        product_id (int): Product ID
        
    Returns:
        Response: Redirect to products list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    
    # Delete associated image file
    if product.image and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], product.image)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
    
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully')
    return redirect(url_for('admin_products'))


# =============================================================================
# ADMIN CATEGORY MANAGEMENT ROUTES
# =============================================================================

@app.route('/admin/categories')
@login_required
def admin_categories():
    """
    Category management page.
    
    Returns:
        Response: Rendered categories management page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@app.route('/admin/categories/add', methods=['GET', 'POST'])
@login_required
def admin_add_category():
    """
    Add new category page.
    
    Returns:
        Response: Rendered add category form or redirect to categories list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        is_active = 'is_active' in request.form
        
        if Category.query.filter_by(name=name).first():
            flash('Category with this name already exists')
            return redirect(url_for('admin_categories'))
        
        category = Category(
            name=name,
            description=description,
            is_active=is_active
        )
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            filename = save_image(image_file, image_type='category')
            if filename:
                category.image = filename
        
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/add_category.html')


@app.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_category(category_id):
    """
    Edit category page.
    
    Args:
        category_id (int): Category ID
        
    Returns:
        Response: Rendered edit category form or redirect to categories list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        category.is_active = 'is_active' in request.form
        
        # Handle image update
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                filename = save_image(image_file, image_type='category')
                if filename:
                    # Delete old image if exists
                    if category.image and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], category.image)):
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], category.image))
                    category.image = filename
        
        db.session.commit()
        flash('Category updated successfully')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/edit_category.html', category=category)


@app.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@login_required
def admin_delete_category(category_id):
    """
    Delete a category.
    
    Args:
        category_id (int): Category ID
        
    Returns:
        Response: Redirect to categories list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(category_id)
    
    # Check if category has products
    if category.products:
        flash('Cannot delete category with existing products. Please reassign or delete the products first.')
        return redirect(url_for('admin_categories'))
    
    # Delete associated image file
    if category.image and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], category.image)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], category.image))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully')
    return redirect(url_for('admin_categories'))


# =============================================================================
# ADMIN ORDER MANAGEMENT ROUTES
# =============================================================================

@app.route('/admin/orders')
@login_required
def admin_orders():
    """
    Order management page with filtering and stats.
    
    Returns:
        Response: Rendered orders management page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get filter parameters
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    payment_filter = request.args.get('payment', '').strip()
    date_from = request.args.get('from', '').strip()
    date_to = request.args.get('to', '').strip()
    
    # Build query
    query = Order.query
    
    # Apply filters
    if search:
        query = query.filter(
            (Order.id.ilike(f'%{search}%')) |
            (Order.user.has(User.username.ilike(f'%{search}%'))) |
            (Order.user.has(User.email.ilike(f'%{search}%')))
        )
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if payment_filter:
        query = query.filter_by(payment_status=payment_filter)
    
    if date_from:
        from datetime import datetime
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        query = query.filter(Order.created_at >= date_from_obj)
    
    if date_to:
        from datetime import datetime
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        query = query.filter(Order.created_at <= date_to_obj)
    
    orders = query.order_by(Order.created_at.desc()).all()
    
    # Calculate stats
    all_orders = Order.query.all()
    total_orders = len(all_orders)
    pending_orders = len([o for o in all_orders if o.status == 'pending'])
    processing_orders = len([o for o in all_orders if o.status == 'processing'])
    delivered_orders = len([o for o in all_orders if o.status == 'delivered'])
    cancelled_orders = len([o for o in all_orders if o.status == 'cancelled'])
    
    return render_template(
        'admin/orders.html',
        orders=orders,
        total_orders=total_orders,
        pending_orders=pending_orders,
        processing_orders=processing_orders,
        delivered_orders=delivered_orders,
        cancelled_orders=cancelled_orders
    )


@app.route('/admin/order/<int:order_id>')
@login_required
def admin_order_detail(order_id):
    """
    Order detail view page.
    
    Args:
        order_id (int): Order ID to view
        
    Returns:
        Response: Rendered order detail page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


# =============================================================================
# ADMIN ACTIVITY LOGS ROUTES
# =============================================================================

@app.route('/admin/activity-logs')
@login_required
def admin_activity_logs():
    """
    User activity logs page.
    
    Returns:
        Response: Rendered activity logs page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get filter parameters
    selected_user_id = request.args.get('user_id', type=int)
    selected_activity_type = request.args.get('activity_type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    show_all = request.args.get('show_all', type=int)
    
    # Build query
    query = UserActivity.query.join(User).order_by(UserActivity.created_at.desc())
    
    # Apply filters
    if selected_user_id:
        query = query.filter(UserActivity.user_id == selected_user_id)
    
    if selected_activity_type:
        query = query.filter(UserActivity.activity_type == selected_activity_type)
    
    if date_from:
        query = query.filter(UserActivity.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    
    if date_to:
        query = query.filter(UserActivity.created_at <= datetime.strptime(date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    
    # Limit results unless show_all is specified
    if not show_all:
        activities = query.limit(100).all()
    else:
        activities = query.all()
    
    # Get unique activity types for filter dropdown
    activity_types = db.session.query(UserActivity.activity_type).distinct().all()
    activity_types = [at[0] for at in activity_types]
    
    # Statistics
    total_activities = UserActivity.query.count()
    today = datetime.now().date()
    today_activities = UserActivity.query.filter(
        db.func.date(UserActivity.created_at) == today
    ).count()
    
    # Unique users with activities
    unique_users = db.session.query(UserActivity.user_id).distinct().count()
    
    # Most active user
    from sqlalchemy import func
    most_active = db.session.query(
        UserActivity.user_id,
        func.count(UserActivity.id).label('activity_count')
    ).group_by(UserActivity.user_id).order_by(func.count(UserActivity.id).desc()).first()
    
    most_active_user = User.query.get(most_active[0]) if most_active else None
    all_users = User.query.all()
    
    return render_template('admin/activity_logs.html',
                         activities=activities,
                         all_users=all_users,
                         activity_types=activity_types,
                         selected_user_id=selected_user_id,
                         selected_activity_type=selected_activity_type,
                         date_from=date_from,
                         date_to=date_to,
                         total_activities=total_activities,
                         today_activities=today_activities,
                         unique_users=unique_users,
                         most_active_user=most_active_user)


@app.route('/admin/clear-old-logs', methods=['POST'])
@login_required
def admin_clear_old_logs():
    """
    Clear old activity logs (older than 30 days).
    
    Returns:
        JSON: Operation result
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Delete logs older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        deleted_count = UserActivity.query.filter(
            UserActivity.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        # Log this admin action
        log_user_activity(
            current_user,
            'admin_action',
            f'Cleared {deleted_count} old activity logs (older than 30 days)',
            request
        )
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} old activity logs'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# =============================================================================
# ADMIN HERO SECTION ROUTES
# =============================================================================

@app.route('/admin/hero-sections')
@login_required
def admin_hero_sections():
    """
    Hero section management page.
    
    Returns:
        Response: Rendered hero sections management page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    hero_sections = HeroSection.query.order_by(HeroSection.display_order).all()
    return render_template('admin/hero_sections.html', hero_sections=hero_sections)


@app.route('/admin/hero-sections/add', methods=['GET', 'POST'])
@login_required
def admin_add_hero_section():
    """
    Add new hero section page.
    
    Returns:
        Response: Rendered add hero section form or redirect to hero sections list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        button_text = request.form.get('button_text', 'Shop Now')
        button_url = request.form.get('button_url', '/products')
        background_color = request.form.get('background_color', 'bg-primary')
        text_color = request.form.get('text_color', 'text-white')
        is_active = 'is_active' in request.form
        display_order = int(request.form.get('display_order', 0))
        
        # If setting this as active, deactivate others
        if is_active:
            HeroSection.query.update({HeroSection.is_active: False})
        
        hero_section = HeroSection(
            title=title,
            subtitle=subtitle,
            button_text=button_text,
            button_url=button_url,
            background_color=background_color,
            text_color=text_color,
            is_active=is_active,
            display_order=display_order
        )
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            filename = save_image(image_file, image_type='product')
            if filename:
                hero_section.image = filename
        
        db.session.add(hero_section)
        db.session.commit()
        flash('Hero section added successfully')
        return redirect(url_for('admin_hero_sections'))
    
    return render_template('admin/add_hero_section.html')


@app.route('/admin/hero-sections/edit/<int:hero_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_hero_section(hero_id):
    """
    Edit hero section page.
    
    Args:
        hero_id (int): Hero section ID
        
    Returns:
        Response: Rendered edit hero section form or redirect to hero sections list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    hero_section = HeroSection.query.get_or_404(hero_id)
    
    if request.method == 'POST':
        hero_section.title = request.form.get('title')
        hero_section.subtitle = request.form.get('subtitle')
        hero_section.button_text = request.form.get('button_text', 'Shop Now')
        hero_section.button_url = request.form.get('button_url', '/products')
        hero_section.background_color = request.form.get('background_color', 'bg-primary')
        hero_section.text_color = request.form.get('text_color', 'text-white')
        hero_section.display_order = int(request.form.get('display_order', 0))
        
        new_is_active = 'is_active' in request.form
        
        # If activating this section, deactivate others
        if new_is_active and not hero_section.is_active:
            HeroSection.query.update({HeroSection.is_active: False})
        
        hero_section.is_active = new_is_active
        
        # Handle image update
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                filename = save_image(image_file, image_type='product')
                if filename:
                    # Delete old image if exists
                    if hero_section.image and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], hero_section.image)):
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], hero_section.image))
                    hero_section.image = filename
        
        db.session.commit()
        flash('Hero section updated successfully')
        return redirect(url_for('admin_hero_sections'))
    
    return render_template('admin/edit_hero_section.html', hero_section=hero_section)


@app.route('/admin/hero-sections/delete/<int:hero_id>', methods=['POST'])
@login_required
def admin_delete_hero_section(hero_id):
    """
    Delete a hero section.
    
    Args:
        hero_id (int): Hero section ID
        
    Returns:
        Response: Redirect to hero sections list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    hero_section = HeroSection.query.get_or_404(hero_id)
    
    # Delete associated image
    if hero_section.image and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], hero_section.image)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], hero_section.image))
    
    db.session.delete(hero_section)
    db.session.commit()
    flash('Hero section deleted successfully')
    return redirect(url_for('admin_hero_sections'))


@app.route('/admin/hero-sections/activate/<int:hero_id>')
@login_required
def admin_activate_hero_section(hero_id):
    """
    Activate a specific hero section.
    
    Args:
        hero_id (int): Hero section ID
        
    Returns:
        Response: Redirect to hero sections list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Deactivate all hero sections first
    HeroSection.query.update({HeroSection.is_active: False})
    
    # Activate the selected one
    hero_section = HeroSection.query.get_or_404(hero_id)
    hero_section.is_active = True
    db.session.commit()
    
    flash(f'"{hero_section.title}" is now the active hero section')
    return redirect(url_for('admin_hero_sections'))


@app.route('/admin/hero-sections/preview/<int:hero_id>')
@login_required
def admin_preview_hero_section(hero_id):
    """
    Preview a hero section.
    
    Args:
        hero_id (int): Hero section ID
        
    Returns:
        Response: Rendered hero section preview
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    hero_section = HeroSection.query.get_or_404(hero_id)
    return render_template('preview_hero.html', hero_section=hero_section)


@app.route('/admin/hero-sections/bulk-delete', methods=['POST'])
@login_required
def admin_bulk_delete_hero_sections():
    """
    Bulk delete hero sections.
    
    Returns:
        Response: Redirect to hero sections list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    hero_ids = request.form.getlist('hero_ids')
    if hero_ids:
        # Prevent deleting active section
        active_hero = HeroSection.query.filter_by(is_active=True).first()
        if active_hero and str(active_hero.id) in hero_ids:
            flash('Cannot delete active hero section. Deactivate it first.', 'error')
            return redirect(url_for('admin_hero_sections'))
        
        for hero_id in hero_ids:
            hero_section = HeroSection.query.get(hero_id)
            if hero_section:
                # Delete image file
                if hero_section.image and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], hero_section.image)):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], hero_section.image))
                db.session.delete(hero_section)
        
        db.session.commit()
        flash(f'{len(hero_ids)} hero sections deleted successfully')
    
    return redirect(url_for('admin_hero_sections'))


# =============================================================================
# ADMIN SYSTEM SETTINGS ROUTES
# =============================================================================

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    """
    Admin page to manage system settings (shipping costs, tax rates).
    
    GET: Display current settings
    POST: Update settings
    
    Returns:
        Response: Rendered settings page or JSON response for POST
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    settings = SystemSettings.get_settings()
    
    if request.method == 'POST':
        try:
            settings_type = request.form.get('settings_type')
            
            if settings_type == 'shipping':
                # Update shipping settings (costs and delivery days)
                standard = float(request.form.get('standard_shipping_cost', 0))
                express = float(request.form.get('express_shipping_cost', 0))
                threshold = float(request.form.get('free_shipping_threshold', 0))
                
                # Get delivery days
                standard_min_days = int(request.form.get('standard_shipping_days_min', 3))
                standard_max_days = int(request.form.get('standard_shipping_days_max', 5))
                express_min_days = int(request.form.get('express_shipping_days_min', 1))
                express_max_days = int(request.form.get('express_shipping_days_max', 2))
                free_min_days = int(request.form.get('free_shipping_days_min', 5))
                free_max_days = int(request.form.get('free_shipping_days_max', 7))
                
                # Get delivery hours and minutes
                standard_min_hours = int(request.form.get('standard_shipping_hours_min', 0))
                standard_max_hours = int(request.form.get('standard_shipping_hours_max', 0))
                standard_min_minutes = int(request.form.get('standard_shipping_minutes_min', 0))
                standard_max_minutes = int(request.form.get('standard_shipping_minutes_max', 0))
                
                express_min_hours = int(request.form.get('express_shipping_hours_min', 0))
                express_max_hours = int(request.form.get('express_shipping_hours_max', 0))
                express_min_minutes = int(request.form.get('express_shipping_minutes_min', 0))
                express_max_minutes = int(request.form.get('express_shipping_minutes_max', 0))
                
                free_min_hours = int(request.form.get('free_shipping_hours_min', 0))
                free_max_hours = int(request.form.get('free_shipping_hours_max', 0))
                free_min_minutes = int(request.form.get('free_shipping_minutes_min', 0))
                free_max_minutes = int(request.form.get('free_shipping_minutes_max', 0))
                
                # Validate costs
                if standard < 0 or express < 0 or threshold < 0:
                    flash('Costs must be non-negative', 'danger')
                    return redirect(url_for('admin_settings'))
                
                # Validate delivery days (allow 0 for hour/minute only delivery)
                if (standard_min_days < 0 or standard_max_days < 0 or 
                    express_min_days < 0 or express_max_days < 0 or 
                    free_min_days < 0 or free_max_days < 0):
                    flash('Delivery days must be non-negative', 'danger')
                    return redirect(url_for('admin_settings'))
                
                if (standard_min_days > standard_max_days or 
                    express_min_days > express_max_days or 
                    free_min_days > free_max_days):
                    flash('From days cannot be greater than To days', 'danger')
                    return redirect(url_for('admin_settings'))
                
                # Validate hours and minutes
                if not (0 <= standard_min_hours <= 23 and 0 <= standard_max_hours <= 23 and
                        0 <= express_min_hours <= 23 and 0 <= express_max_hours <= 23 and
                        0 <= free_min_hours <= 23 and 0 <= free_max_hours <= 23):
                    flash('Hours must be between 0 and 23', 'danger')
                    return redirect(url_for('admin_settings'))
                
                if not (0 <= standard_min_minutes <= 59 and 0 <= standard_max_minutes <= 59 and
                        0 <= express_min_minutes <= 59 and 0 <= express_max_minutes <= 59 and
                        0 <= free_min_minutes <= 59 and 0 <= free_max_minutes <= 59):
                    flash('Minutes must be between 0 and 59', 'danger')
                    return redirect(url_for('admin_settings'))
                
                settings.update_shipping_settings(
                    standard, express, threshold,
                    standard_min_days, standard_max_days,
                    express_min_days, express_max_days,
                    free_min_days, free_max_days,
                    current_user.id,
                    standard_min_hours, standard_max_hours, standard_min_minutes, standard_max_minutes,
                    express_min_hours, express_max_hours, express_min_minutes, express_max_minutes,
                    free_min_hours, free_max_hours, free_min_minutes, free_max_minutes
                )
                
                # Log action
                log_user_activity(
                    current_user,
                    'admin_action',
                    f'Updated shipping: Standard=GH₵{standard} ({standard_min_days}-{standard_max_days}d {standard_min_hours}h{standard_min_minutes}m-{standard_max_hours}h{standard_max_minutes}m), '
                    f'Express=GH₵{express} ({express_min_days}-{express_max_days}d {express_min_hours}h{express_min_minutes}m-{express_max_hours}h{express_max_minutes}m), '
                    f'Free@GH₵{threshold} ({free_min_days}-{free_max_days}d {free_min_hours}h{free_min_minutes}m-{free_max_hours}h{free_max_minutes}m)',
                    request
                )
                
                flash('Shipping settings updated successfully', 'success')
            
            elif settings_type == 'tax':
                # Update tax settings
                tax_rate = float(request.form.get('tax_rate', 0)) / 100  # Convert from percentage
                
                # Validate
                if tax_rate < 0 or tax_rate > 1:
                    flash('Tax rate must be between 0% and 100%', 'danger')
                    return redirect(url_for('admin_settings'))
                
                settings.update_tax_settings(tax_rate, current_user.id)
                
                # Log action
                log_user_activity(
                    current_user,
                    'admin_action',
                    f'Updated tax rate to {tax_rate * 100:.2f}%',
                    request
                )
                
                flash('Tax settings updated successfully', 'success')
            
            return redirect(url_for('admin_settings'))
        
        except ValueError:
            flash('Invalid input values', 'danger')
            return redirect(url_for('admin_settings'))
        except Exception as e:
            flash(f'Error updating settings: {str(e)}', 'danger')
            return redirect(url_for('admin_settings'))
    
    return render_template('admin/settings.html', settings=settings)


@app.route('/admin/contact-settings', methods=['GET', 'POST'])
@login_required
def admin_contact_settings():
    """
    Admin page to manage contact information and social media links.
    
    GET: Display current contact settings
    POST: Update contact settings
    
    Returns:
        Response: Rendered contact settings page or redirect
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    contact_settings = ContactSettings.get_settings()
    
    if request.method == 'POST':
        try:
            settings_type = request.form.get('settings_type')
            
            if settings_type == 'contact_info':
                # Update contact information
                business_name = request.form.get('business_name')
                business_description = request.form.get('business_description')
                email = request.form.get('email')
                phone = request.form.get('phone')
                phone_whatsapp = request.form.get('phone_whatsapp')
                address = request.form.get('address')
                city = request.form.get('city')
                country = request.form.get('country')
                postal_code = request.form.get('postal_code')
                
                contact_settings.update_contact_info(
                    business_name, business_description, email, phone,
                    phone_whatsapp, address, city, country, postal_code,
                    current_user.id
                )
                
                log_user_activity(
                    current_user,
                    'admin_action',
                    f'Updated contact information: {business_name}, {email}, {phone}',
                    request
                )
                
                flash('Contact information updated successfully', 'success')
            
            elif settings_type == 'social_media':
                # Update social media links
                facebook = request.form.get('facebook_url')
                twitter = request.form.get('twitter_url')
                instagram = request.form.get('instagram_url')
                linkedin = request.form.get('linkedin_url')
                youtube = request.form.get('youtube_url')
                tiktok = request.form.get('tiktok_url')
                telegram = request.form.get('telegram_url')
                
                contact_settings.update_social_media(
                    facebook, twitter, instagram, linkedin, youtube, tiktok, telegram,
                    current_user.id
                )
                
                log_user_activity(
                    current_user,
                    'admin_action',
                    f'Updated social media links',
                    request
                )
                
                flash('Social media links updated successfully', 'success')
            
            elif settings_type == 'operating_hours':
                # Update operating hours
                opening_time = request.form.get('opening_time')
                closing_time = request.form.get('closing_time')
                timezone = request.form.get('timezone')
                
                contact_settings.update_operating_hours(
                    opening_time, closing_time, timezone,
                    current_user.id
                )
                
                log_user_activity(
                    current_user,
                    'admin_action',
                    f'Updated operating hours: {opening_time} - {closing_time}',
                    request
                )
                
                flash('Operating hours updated successfully', 'success')
            
            return redirect(url_for('admin_contact_settings'))
        
        except Exception as e:
            flash(f'Error updating settings: {str(e)}', 'danger')
            return redirect(url_for('admin_contact_settings'))
    
    return render_template('admin/contact_settings.html', contact_settings=contact_settings)


# =============================================================================
# ADMIN DYNAMIC MESSAGE ROUTES
# =============================================================================

@app.route('/admin/messages')
@login_required
def admin_messages():
    """
    Dynamic messages management page.
    
    Returns:
        Response: Rendered messages list page
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    
    # Build query
    query = DynamicMessage.query
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    elif status_filter == 'scheduled':
        now = datetime.utcnow()
        query = query.filter(DynamicMessage.start_date > now)
    elif status_filter == 'expired':
        now = datetime.utcnow()
        query = query.filter(DynamicMessage.end_date < now)
    
    messages = query.order_by(DynamicMessage.display_order.asc(), 
                             DynamicMessage.created_at.desc()).all()
    
    return render_template('admin/messages.html', 
                         messages=messages,
                         status_filter=status_filter)


@app.route('/admin/messages/add', methods=['GET', 'POST'])
@login_required
def admin_add_message():
    """
    Add new dynamic message.
    
    Returns:
        Response: Rendered form or redirect to messages list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            message_type = request.form.get('message_type', 'info')
            is_active = 'is_active' in request.form
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            display_location = request.form.get('display_location', 'homepage')
            background_color = request.form.get('background_color', '#007bff')
            text_color = request.form.get('text_color', '#ffffff')
            icon = request.form.get('icon', 'info-circle')
            cta_text = request.form.get('cta_text', '').strip()
            cta_url = request.form.get('cta_url', '').strip()
            display_order = int(request.form.get('display_order', 0))
            
            # Validate
            if not title or not content:
                flash('Title and content are required', 'danger')
                return redirect(url_for('admin_add_message'))
            
            # Parse dates if provided
            start_dt = None
            end_dt = None
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
            
            # Validate CTA
            if (cta_text and not cta_url) or (cta_url and not cta_text):
                flash('Both button text and URL must be provided together', 'danger')
                return redirect(url_for('admin_add_message'))
            
            message = DynamicMessage(
                title=title,
                content=content,
                message_type=message_type,
                is_active=is_active,
                start_date=start_dt,
                end_date=end_dt,
                display_location=display_location,
                background_color=background_color,
                text_color=text_color,
                icon=icon,
                cta_text=cta_text if cta_text else None,
                cta_url=cta_url if cta_url else None,
                display_order=display_order,
                created_by_id=current_user.id,
                updated_by_id=current_user.id
            )
            
            db.session.add(message)
            db.session.commit()
            
            log_user_activity(
                current_user,
                'admin_action',
                f'Created dynamic message: "{title}"',
                request
            )
            
            flash('Message created successfully', 'success')
            return redirect(url_for('admin_messages'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating message: {str(e)}', 'danger')
            return redirect(url_for('admin_add_message'))
    
    return render_template('admin/add_message.html')


@app.route('/admin/messages/edit/<int:message_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_message(message_id):
    """
    Edit dynamic message.
    
    Args:
        message_id (int): Message ID
        
    Returns:
        Response: Rendered form or redirect to messages list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    message = DynamicMessage.query.get_or_404(message_id)
    
    if request.method == 'POST':
        try:
            message.title = request.form.get('title', '').strip()
            message.content = request.form.get('content', '').strip()
            message.message_type = request.form.get('message_type', 'info')
            message.is_active = 'is_active' in request.form
            message.display_location = request.form.get('display_location', 'homepage')
            message.background_color = request.form.get('background_color', '#007bff')
            message.text_color = request.form.get('text_color', '#ffffff')
            message.icon = request.form.get('icon', 'info-circle')
            message.cta_text = request.form.get('cta_text', '').strip() or None
            message.cta_url = request.form.get('cta_url', '').strip() or None
            message.display_order = int(request.form.get('display_order', 0))
            message.updated_by_id = current_user.id
            message.updated_at = datetime.utcnow()
            
            # Parse dates
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            message.start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M') if start_date else None
            message.end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M') if end_date else None
            
            # Validate
            if not message.title or not message.content:
                flash('Title and content are required', 'danger')
                return redirect(request.url)
            
            # Validate CTA
            if (message.cta_text and not message.cta_url) or (message.cta_url and not message.cta_text):
                flash('Both button text and URL must be provided together', 'danger')
                return redirect(request.url)
            
            db.session.commit()
            
            log_user_activity(
                current_user,
                'admin_action',
                f'Updated dynamic message: "{message.title}"',
                request
            )
            
            flash('Message updated successfully', 'success')
            return redirect(url_for('admin_messages'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating message: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('admin/edit_message.html', message=message)


@app.route('/admin/messages/delete/<int:message_id>', methods=['POST'])
@login_required
def admin_delete_message(message_id):
    """
    Delete a dynamic message.
    
    Args:
        message_id (int): Message ID
        
    Returns:
        Response: Redirect to messages list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    message = DynamicMessage.query.get_or_404(message_id)
    title = message.title
    
    db.session.delete(message)
    db.session.commit()
    
    log_user_activity(
        current_user,
        'admin_action',
        f'Deleted dynamic message: "{title}"',
        request
    )
    
    flash('Message deleted successfully', 'success')
    return redirect(url_for('admin_messages'))


@app.route('/admin/messages/toggle/<int:message_id>')
@login_required
def admin_toggle_message(message_id):
    """
    Toggle active status of a message.
    
    Args:
        message_id (int): Message ID
        
    Returns:
        Response: Redirect to messages list
    """
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    message = DynamicMessage.query.get_or_404(message_id)
    message.is_active = not message.is_active
    message.updated_by_id = current_user.id
    message.updated_at = datetime.utcnow()
    db.session.commit()
    
    status = 'activated' if message.is_active else 'deactivated'
    log_user_activity(
        current_user,
        'admin_action',
        f'{status.capitalize()} message: "{message.title}"',
        request
    )
    
    flash(f'Message {status} successfully', 'success')
    return redirect(url_for('admin_messages'))


@app.route('/api/messages/click/<int:message_id>')
def api_message_click(message_id):
    """
    Track CTA click on a message (AJAX).
    
    Args:
        message_id (int): Message ID
        
    Returns:
        JSON: Success status
    """
    try:
        message = DynamicMessage.query.get(message_id)
        if message:
            message.increment_clicks()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False}), 500

# Message view tracking
@app.route('/api/messages/view/<int:message_id>')
def track_message_view(message_id):
    """Track message view for analytics"""
    try:
        message = DynamicMessage.query.get(message_id)
        if message:
            message.increment_views()
            db.session.commit()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False}), 500

# =============================================================================
# ADMIN REVIEW MODERATION ROUTES
# =============================================================================

@app.route('/admin/reviews')
@login_required
def admin_reviews():
    """
    Admin review moderation dashboard.
    
    Returns:
        Response: Rendered admin reviews page
    """
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get filters from query params
    status_filter = request.args.get('status', 'pending')  # pending, approved, all
    sort_by = request.args.get('sort', 'newest')  # newest, oldest, rating
    page = request.args.get('page', 1, type=int)
    
    query = ProductReview.query
    
    # Filter by status
    if status_filter == 'pending':
        query = query.filter_by(is_approved=False)
    elif status_filter == 'approved':
        query = query.filter_by(is_approved=True)
    
    # Sort
    if sort_by == 'oldest':
        query = query.order_by(ProductReview.created_at.asc())
    elif sort_by == 'rating':
        query = query.order_by(ProductReview.rating.desc())
    else:  # newest (default)
        query = query.order_by(ProductReview.created_at.desc())
    
    # Paginate
    reviews = query.paginate(page=page, per_page=10)
    
    # Get statistics
    total_reviews = ProductReview.query.count()
    pending_reviews = ProductReview.query.filter_by(is_approved=False).count()
    approved_reviews = ProductReview.query.filter_by(is_approved=True).count()
    
    # Calculate average rating
    all_reviews = ProductReview.query.all()
    avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews) if all_reviews else 0
    
    stats = {
        'total': total_reviews,
        'pending': pending_reviews,
        'approved': approved_reviews,
        'avg_rating': round(avg_rating, 1)
    }
    
    return render_template('admin/reviews.html', 
                         reviews=reviews,
                         status_filter=status_filter,
                         sort_by=sort_by,
                         stats=stats)


@app.route('/admin/review/<int:review_id>/approve', methods=['POST'])
@login_required
def approve_review(review_id):
    """
    Approve a pending review.
    
    Args:
        review_id (int): Review ID
        
    Returns:
        JSON: Success status
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    review = ProductReview.query.get_or_404(review_id)
    review.is_approved = True
    db.session.commit()
    
    # Log activity
    log_user_activity(
        current_user,
        'admin_action',
        f'Approved review for product {review.product.name}',
        request
    )
    
    return jsonify({'success': True, 'message': 'Review approved'})


@app.route('/admin/review/<int:review_id>/reject', methods=['POST'])
@login_required
def reject_review(review_id):
    """
    Reject and delete a pending review.
    
    Args:
        review_id (int): Review ID
        
    Returns:
        JSON: Success status
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    review = ProductReview.query.get_or_404(review_id)
    product_name = review.product.name
    db.session.delete(review)
    db.session.commit()
    
    # Log activity
    log_user_activity(
        current_user,
        'admin_action',
        f'Rejected review for product {product_name}',
        request
    )
    
    return jsonify({'success': True, 'message': 'Review rejected'})


# =============================================================================
# API ROUTES
# =============================================================================

@app.route('/api/update_order_status', methods=['POST'])
@login_required
def update_order_status():
    """
    Update order status with comprehensive fields: status, payment, tracking, delivery date, notes.
    
    Returns:
        JSON: Operation result
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json(force=True, cache=False)
    except Exception as e:
        app.logger.error(f"JSON parsing error: {e}")
        data = {}
    
    order_id = data.get('order_id')
    status = data.get('status')
    payment_status = data.get('payment_status', '').strip()
    tracking_number = data.get('tracking_number', '').strip()
    estimated_delivery = data.get('estimated_delivery', '').strip()
    internal_notes = data.get('internal_notes', '').strip()
    notify_customer = data.get('notify_customer', False)
    notify_team = data.get('notify_team', False)
    
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Track changes for logging
        changes = []
        status_changed = False
        old_status = order.status
        
        # Update status
        if status and status != order.status:
            old_status = order.status
            order.status = status
            status_changed = True
            changes.append(f"Status: {old_status} → {status}")
        
        # Update payment status
        if payment_status and payment_status != order.payment_status:
            old_payment = order.payment_status
            order.payment_status = payment_status
            changes.append(f"Payment: {old_payment} → {payment_status}")
        
        # Update tracking number
        if tracking_number:
            order.tracking_number = tracking_number
            changes.append(f"Tracking: {tracking_number}")
        
        # Update estimated delivery
        if estimated_delivery:
            from datetime import datetime
            try:
                delivery_date = datetime.strptime(estimated_delivery, '%Y-%m-%d')
                order.shipped_at = delivery_date  # Use shipped_at as estimated delivery proxy
                changes.append(f"Est. Delivery: {estimated_delivery}")
            except ValueError:
                pass
        
        # Update internal notes (append to existing)
        if internal_notes:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_note = f"[{timestamp}] {current_user.username}: {internal_notes}"
            if order.notes:
                order.notes = order.notes + '\n' + new_note
            else:
                order.notes = new_note
            changes.append("Notes added")
        
        db.session.commit()
        
        # Build activity log message
        log_message = f'Updated order #{order.id}: ' + ', '.join(changes)
        
        # Log admin action
        log_user_activity(
            current_user,
            'admin_action',
            log_message,
            request
        )
        
        # Send SMS notification if status changed
        if status_changed:
            try:
                from sms.service import send_order_status_sms
                send_order_status_sms(order)
            except Exception as e:
                print(f"Warning: Could not send order status SMS: {e}")
        
        # Send notifications if requested
        if notify_customer:
            # Queue email to customer with status update
            # TODO: Implement customer email notification
            pass
        
        if notify_team:
            # Queue notification to team
            # TODO: Implement team notification (Slack, email, etc)
            pass
        
        return jsonify({
            'success': True,
            'message': 'Order updated successfully',
            'changes': changes
        })
    
    except Exception as e:
        print(f"Error updating order: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export_orders')
@login_required
def export_orders():
    """
    Export filtered orders to CSV.
    
    Returns:
        Response: CSV file download
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        import csv
        from io import StringIO
        
        # Get filter parameters
        search = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '').strip()
        payment_filter = request.args.get('payment', '').strip()
        
        # Build query
        query = Order.query
        
        # Apply filters
        if search:
            query = query.filter(
                (Order.id.ilike(f'%{search}%')) |
                (Order.user.has(User.username.ilike(f'%{search}%'))) |
                (Order.user.has(User.email.ilike(f'%{search}%')))
            )
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if payment_filter:
            query = query.filter_by(payment_status=payment_filter)
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Order ID', 'Order Number', 'Customer', 'Email', 'Total Amount',
            'Status', 'Payment Status', 'Created Date', 'Items Count', 'Tracking Number'
        ])
        
        # Write data
        for order in orders:
            writer.writerow([
                order.id,
                order.order_number,
                order.user.username,
                order.user.email,
                f"{order.total_amount:.2f}",
                order.status,
                order.payment_status,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                len(order.order_items),
                order.tracking_number or 'N/A'
            ])
        
        # Prepare response
        output.seek(0)
        response = app.make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=orders_export.csv"
        response.headers["Content-Type"] = "text/csv"
        
        # Log action
        log_user_activity(
            current_user,
            'admin_action',
            f'Exported {len(orders)} orders to CSV',
            request
        )
        
        return response
    
    except Exception as e:
        print(f"Error exporting orders: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/categories')
def api_categories():
    """
    Get categories list for API.
    
    Returns:
        JSON: List of categories
    """
    categories = Category.query.filter_by(is_active=True).all()
    categories_data = [{
        'id': category.id,
        'name': category.name,
        'product_count': len(category.products)
    } for category in categories]
    
    return jsonify(categories_data)


@app.route('/api/user/shipping-info')
@login_required
def api_user_shipping_info():
    """
    Get logged-in user's saved shipping information for checkout pre-fill.
    
    Returns:
        JSON: User's saved shipping address info
    """
    return jsonify({
        'first_name': current_user.first_name or '',
        'last_name': current_user.last_name or '',
        'address': current_user.address or '',
        'city': current_user.city or '',
        'postal_code': current_user.postal_code or '',
        'phone': current_user.phone_number or '',
        'email': current_user.email or ''
    })


@app.route('/api/calculate-checkout', methods=['POST'])
@login_required
def api_calculate_checkout():
    """
    Recalculate checkout totals when shipping method changes.
    
    JSON Parameters:
        shipping_method (str): Selected shipping method (free, standard, express)
    
    Returns:
        JSON: Updated shipping cost, tax, and total
    """
    try:
        data = request.get_json()
        shipping_method = data.get('shipping_method')
        
        if not shipping_method:
            return jsonify({'success': False, 'message': 'Shipping method not provided'}), 400
        
        # Get current cart
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400
        
        # Calculate subtotal
        subtotal = sum(item.get_subtotal() for item in cart_items)
        
        # Get shipping options and validate method
        shipping_options = calculate_shipping_cost(subtotal, cart_items)
        if shipping_method not in shipping_options:
            return jsonify({'success': False, 'message': 'Invalid shipping method'}), 400
        
        # Get selected shipping cost
        shipping_cost = shipping_options[shipping_method]['cost']
        
        # Get system settings for tax
        settings = SystemSettings.get_settings()
        tax_rate = settings.tax_rate
        
        # Calculate tax on subtotal + shipping
        taxable_amount = subtotal + shipping_cost
        tax = taxable_amount * tax_rate
        
        # Calculate total
        total = subtotal + shipping_cost + tax
        
        return jsonify({
            'success': True,
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'tax': tax,
            'total': total
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# =============================================================================
# DEBUG AND UTILITY ROUTES
# =============================================================================

@app.route('/debug-images')
@login_required
def debug_images():
    """
    Debug route to check image uploads.
    
    Returns:
        Response: Debug information about images
    """
    if not current_user.is_admin:
        return "Access denied"
    
    import os
    uploads_dir = app.config['UPLOAD_FOLDER']
    files = os.listdir(uploads_dir) if os.path.exists(uploads_dir) else []
    
    products = Product.query.all()
    result = "<h1>Image Debug Info</h1>"
    result += f"<p>Uploads directory: {uploads_dir}</p>"
    result += f"<p>Files in uploads: {files}</p>"
    result += "<h2>Products and their images:</h2>"
    
    for product in products:
        result += f"<p>Product: {product.name} | Image: {product.image} | Has image: {bool(product.image)}</p>"
    
    return result


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_db():
    """
    Initialize database with default data.
    """
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create sample categories 
            categories = [
                Category(name='Electronics', description='Electronic devices and accessories', is_active=True),
                Category(name='Fashion', description='Clothing and fashion items', is_active=True),
                Category(name='Home & Garden', description='Home and garden products', is_active=True),
                Category(name='Sports', description='Sports equipment and accessories', is_active=True),
                Category(name='Books', description='Books and educational materials', is_active=True),
                Category(name='Beauty', description='Beauty and personal care products', is_active=True)
            ]
            
            for category in categories:
                db.session.add(category)
            
            db.session.commit()
            print("✅ Database initialized with admin user and sample categories")


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================
# ==================== BACKUP & RESTORE ROUTES ====================

@app.route('/admin/backups', methods=['GET'])
@login_required
def admin_backups():
    """List all backups"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    from backup_utils import BackupManager
    
    backup_manager = BackupManager(
        db_path='instance/digitalhome.db',
        backup_dir='backups'
    )
    
    backups = backup_manager.list_backups()
    return render_template('admin/backups.html', backups=backups)


@app.route('/api/backup/create', methods=['POST'])
@login_required
def api_create_backup():
    """Create a new backup"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    from backup_utils import BackupManager
    
    try:
        description = request.get_json().get('description', '')
        
        backup_manager = BackupManager(
            db_path='instance/digitalhome.db',
            backup_dir='backups'
        )
        
        result = backup_manager.create_backup(description)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/backup/list', methods=['GET'])
@login_required
def api_list_backups():
    """Get list of backups"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    from backup_utils import BackupManager
    
    try:
        backup_manager = BackupManager(
            db_path='instance/digitalhome.db',
            backup_dir='backups'
        )
        
        backups = backup_manager.list_backups()
        return jsonify({'success': True, 'backups': backups})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/backup/restore', methods=['POST'])
@login_required
def api_restore_backup():
    """Restore database from backup"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    from backup_utils import BackupManager
    
    try:
        data = request.get_json()
        backup_filename = data.get('filename')
        
        if not backup_filename:
            return jsonify({'success': False, 'message': 'Backup filename required'}), 400
        
        # Validate filename to prevent path traversal
        if '..' in backup_filename or '/' in backup_filename or '\\' in backup_filename:
            return jsonify({'success': False, 'message': 'Invalid backup filename'}), 400
        
        backup_manager = BackupManager(
            db_path='instance/digitalhome.db',
            backup_dir='backups'
        )
        
        result = backup_manager.restore_backup(backup_filename)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/backup/delete', methods=['POST'])
@login_required
def api_delete_backup():
    """Delete a backup file"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    from backup_utils import BackupManager
    
    try:
        data = request.get_json()
        backup_filename = data.get('filename')
        
        if not backup_filename:
            return jsonify({'success': False, 'message': 'Backup filename required'}), 400
        
        # Validate filename to prevent path traversal
        if '..' in backup_filename or '/' in backup_filename or '\\' in backup_filename:
            return jsonify({'success': False, 'message': 'Invalid backup filename'}), 400
        
        backup_manager = BackupManager(
            db_path='instance/digitalhome.db',
            backup_dir='backups'
        )
        
        result = backup_manager.delete_backup(backup_filename)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/backup/download/<filename>', methods=['GET'])
@login_required
def api_download_backup(filename):
    """Download a backup file"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        # Validate filename to prevent path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({'success': False, 'message': 'Invalid backup filename'}), 400
        
        backup_path = os.path.join('backups', filename)
        
        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'message': 'Backup file not found'}), 404
        
        return send_file(backup_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    # Create uploads directory
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    # Initialize database
    init_db()  # Temporarily disabled - use flask db upgrade instead
    
    # Start development server
    print("🚀 Starting DigitalHome E-Commerce Platform...")
    print("📍 Server running at: http://localhost:5000")
    print("🔑 Admin login: admin@example.com / admin123")
    app.run(debug=True)