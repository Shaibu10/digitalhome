from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db
#db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)  # SMS support (e.g., 0241234567)
    password_hash = db.Column(db.String(255))  # Increased from 128 to 255 for scrypt hashes (151+ chars)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Shipping Information (saved from last order for auto-fill)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    email_tokens = db.relationship('EmailToken', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_order_count(self):
        return len(self.orders)
    
    def get_total_spent(self):
        return sum(order.total_amount for order in self.orders)
    
    def log_activity(self, activity_type, description=None, ip_address=None, user_agent=None):
        """Log user activity"""
        activity = UserActivity(
            user_id=self.id,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(activity)
        
        # Update last login if it's a login activity
        if activity_type == 'login':
            self.last_login = datetime.utcnow()
        
        db.session.commit()
        return activity
    
    def get_recent_activities(self, limit=10):
        """Get recent user activities"""
        return UserActivity.query.filter_by(user_id=self.id)\
            .order_by(UserActivity.created_at.desc())\
            .limit(limit).all()
    
    def get_activity_count(self, activity_type=None):
        """Get count of user activities, optionally filtered by type"""
        query = UserActivity.query.filter_by(user_id=self.id)
        if activity_type:
            query = query.filter_by(activity_type=activity_type)
        return query.count()

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)  # login, logout, view_product, add_to_cart, etc.
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('activities', lazy=True))

    def __repr__(self):
        return f'<UserActivity {self.user_id} - {self.activity_type}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='category', lazy=True)

    def product_count(self):
        return len(self.products)

    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float)
    stock_quantity = db.Column(db.Integer, default=0)
    image = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    reviews = db.relationship('ProductReview', backref='product', lazy=True, cascade='all, delete-orphan')

    def final_price(self):
        """Calculate final price customer pays"""
        if self.discount_price:
            return self.price - self.discount_price
        return self.price

    def discount_percentage(self):
        if self.discount_price and self.price > 0:
            return int((self.discount_price / self.price) * 100)
        return 0

    def is_in_stock(self):
        return self.stock_quantity > 0
    
    def get_avg_rating(self):
        """Calculate average rating from approved reviews"""
        approved_reviews = ProductReview.query.filter_by(
            product_id=self.id,
            is_approved=True
        ).all()
        if not approved_reviews:
            return 0
        total = sum(review.rating for review in approved_reviews)
        return round(total / len(approved_reviews), 1)
    
    def get_review_count(self):
        """Get count of approved reviews"""
        return ProductReview.query.filter_by(
            product_id=self.id,
            is_approved=True
        ).count()
    
    def get_rating_distribution(self):
        """Get distribution of ratings (5-star, 4-star, etc.)"""
        distribution = {}
        for i in range(1, 6):
            count = ProductReview.query.filter_by(
                product_id=self.id,
                rating=i,
                is_approved=True
            ).count()
            distribution[i] = count
        return distribution

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)  # e.g., ORD-2025-001234
    total_amount = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False, default=0)
    shipping_cost = db.Column(db.Float, nullable=False, default=0)
    discount_amount = db.Column(db.Float, nullable=False, default=0)
    discount_percentage = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, processing, shipped, delivered, cancelled
    payment_status = db.Column(db.String(50), default='unpaid')  # unpaid, paid, failed, refunded
    payment_method = db.Column(db.String(100))  # cash, card, mobile_money, etc.
    
    # Shipping information
    shipping_first_name = db.Column(db.String(100))
    shipping_last_name = db.Column(db.String(100))
    shipping_address = db.Column(db.Text)
    shipping_city = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(20))
    shipping_phone = db.Column(db.String(20))
    
    # Additional info
    notes = db.Column(db.Text)
    tracking_number = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def get_status_badge(self):
        """Get Bootstrap badge class for status"""
        status_map = {
            'pending': 'warning',
            'confirmed': 'info',
            'processing': 'primary',
            'shipped': 'secondary',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        return status_map.get(self.status, 'secondary')
    
    def get_payment_badge(self):
        """Get Bootstrap badge class for payment status"""
        payment_map = {
            'unpaid': 'warning',
            'paid': 'success',
            'failed': 'danger',
            'refunded': 'secondary'
        }
        return payment_map.get(self.payment_status, 'secondary')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)  # Store product name at purchase time
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # Price at time of purchase
    total_price = db.Column(db.Float, nullable=False)  # unit_price * quantity
    
    def __repr__(self):
        return f'<OrderItem Order#{self.order_id} Product#{self.product_id}>'

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_subtotal(self):
        """Get subtotal for this cart item"""
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if session:
            product = session.query(Product).get(self.product_id)
            if product:
                return product.final_price() * self.quantity
        return 0
    
    def __repr__(self):
        return f'<CartItem User#{self.user_id} Product#{self.product_id}>'

class HeroSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.Text)
    button_text = db.Column(db.String(50), default='Shop Now')
    button_url = db.Column(db.String(200), default='/products')
    image = db.Column(db.String(200))
    background_color = db.Column(db.String(50), default='bg-primary')
    text_color = db.Column(db.String(50), default='text-white')
    is_active = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<HeroSection {self.title}>'


class EmailToken(db.Model):
    """Model for storing email verification tokens"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    verification_code = db.Column(db.String(10), nullable=False)  # Short 6-char code for SMS/email display
    token_type = db.Column(db.String(50), default='email_verification')  # email_verification or password_reset
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)  # When token was used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_valid(self):
        """Check if token is still valid (not expired and not used)"""
        return datetime.utcnow() < self.expires_at and self.used_at is None
    
    def mark_as_used(self):
        """Mark token as used"""
        self.used_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<EmailToken {self.token_type} for user {self.user_id}>'


class TokenRateLimit(db.Model):
    """Model for tracking token generation requests for rate limiting"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    attempt_count = db.Column(db.Integer, default=1)
    last_attempt_at = db.Column(db.DateTime, default=datetime.utcnow)
    locked_until = db.Column(db.DateTime)  # Temporary lock for abuse prevention
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.Index('idx_email_rate_limit', 'email'),)
    
    def is_locked(self):
        """Check if this email is currently rate limited"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def increment_attempt(self):
        """Increment attempt count and update timestamp"""
        self.attempt_count += 1
        self.last_attempt_at = datetime.utcnow()
        
        # Calculate exponential backoff: 60s * 2^(attempts-3) for attempts >= 3
        if self.attempt_count >= 3:
            seconds_to_lock = 60 * (2 ** (self.attempt_count - 3))
            self.locked_until = datetime.utcnow() + __import__('datetime').timedelta(seconds=seconds_to_lock)
        
        db.session.commit()
    
    def reset(self):
        """Reset attempt count after successful verification"""
        self.attempt_count = 0
        self.locked_until = None
        db.session.commit()
    
    @staticmethod
    def get_or_create(email):
        """Get existing rate limit record or create new one"""
        record = TokenRateLimit.query.filter_by(email=email).first()
        if not record:
            record = TokenRateLimit(email=email)
            db.session.add(record)
            db.session.commit()
        return record
    
    def __repr__(self):
        return f'<TokenRateLimit {self.email} - attempts: {self.attempt_count}>'


class SystemSettings(db.Model):
    """Model for managing system-wide settings like shipping costs and tax rates"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Shipping Costs
    standard_shipping_cost = db.Column(db.Float, default=10.00)
    express_shipping_cost = db.Column(db.Float, default=15.00)
    free_shipping_threshold = db.Column(db.Float, default=100.00)
    
    # Shipping Days (Delivery Time)
    standard_shipping_days_min = db.Column(db.Integer, default=3)  # 3-5 days
    standard_shipping_days_max = db.Column(db.Integer, default=5)
    express_shipping_days_min = db.Column(db.Integer, default=1)   # 1-2 days
    express_shipping_days_max = db.Column(db.Integer, default=2)
    free_shipping_days_min = db.Column(db.Integer, default=5)      # 5-7 days
    free_shipping_days_max = db.Column(db.Integer, default=7)
    
    # Shipping Hours & Minutes (Additional Time Precision)
    standard_shipping_hours_min = db.Column(db.Integer, default=0)  # Hours (0-23)
    standard_shipping_hours_max = db.Column(db.Integer, default=0)
    standard_shipping_minutes_min = db.Column(db.Integer, default=0)  # Minutes (0-59)
    standard_shipping_minutes_max = db.Column(db.Integer, default=0)
    
    express_shipping_hours_min = db.Column(db.Integer, default=0)
    express_shipping_hours_max = db.Column(db.Integer, default=0)
    express_shipping_minutes_min = db.Column(db.Integer, default=0)
    express_shipping_minutes_max = db.Column(db.Integer, default=0)
    
    free_shipping_hours_min = db.Column(db.Integer, default=0)
    free_shipping_hours_max = db.Column(db.Integer, default=0)
    free_shipping_minutes_min = db.Column(db.Integer, default=0)
    free_shipping_minutes_max = db.Column(db.Integer, default=0)
    
    # Tax Settings
    tax_rate = db.Column(db.Float, default=0.05)  # 5% as decimal (0.05 = 5%)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])
    
    @staticmethod
    def get_settings():
        """Get or create default settings"""
        settings = SystemSettings.query.first()
        if not settings:
            settings = SystemSettings()
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def update_shipping_settings(self, standard_cost, express_cost, free_threshold, 
                                standard_min_days, standard_max_days, express_min_days, 
                                express_max_days, free_min_days, free_max_days, user_id,
                                standard_min_hours=0, standard_max_hours=0, standard_min_minutes=0, standard_max_minutes=0,
                                express_min_hours=0, express_max_hours=0, express_min_minutes=0, express_max_minutes=0,
                                free_min_hours=0, free_max_hours=0, free_min_minutes=0, free_max_minutes=0):
        """Update shipping settings including costs, delivery days, and delivery times (hours/minutes)"""
        self.standard_shipping_cost = standard_cost
        self.express_shipping_cost = express_cost
        self.free_shipping_threshold = free_threshold
        self.standard_shipping_days_min = standard_min_days
        self.standard_shipping_days_max = standard_max_days
        self.express_shipping_days_min = express_min_days
        self.express_shipping_days_max = express_max_days
        self.free_shipping_days_min = free_min_days
        self.free_shipping_days_max = free_max_days
        
        # Update hours and minutes
        self.standard_shipping_hours_min = standard_min_hours
        self.standard_shipping_hours_max = standard_max_hours
        self.standard_shipping_minutes_min = standard_min_minutes
        self.standard_shipping_minutes_max = standard_max_minutes
        
        self.express_shipping_hours_min = express_min_hours
        self.express_shipping_hours_max = express_max_hours
        self.express_shipping_minutes_min = express_min_minutes
        self.express_shipping_minutes_max = express_max_minutes
        
        self.free_shipping_hours_min = free_min_hours
        self.free_shipping_hours_max = free_max_hours
        self.free_shipping_minutes_min = free_min_minutes
        self.free_shipping_minutes_max = free_max_minutes
        
        self.updated_by_id = user_id
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_tax_settings(self, tax_rate, user_id):
        """Update tax settings"""
        self.tax_rate = tax_rate
        self.updated_by_id = user_id
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<SystemSettings tax_rate={self.tax_rate*100}% standard_shipping={self.standard_shipping_cost}>'


class DynamicMessage(db.Model):
    """Model for managing dynamic messages displayed on home page"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Message Content
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Can contain HTML
    
    # Message Type (for styling)
    message_type = db.Column(db.String(50), default='info')  # info, warning, promotion, alert, success
    
    # Status & Visibility
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime)  # When to start showing
    end_date = db.Column(db.DateTime)    # When to stop showing
    
    # Display Location
    display_location = db.Column(db.String(100), default='homepage')  # homepage, all_pages, specific_page
    
    # Styling
    background_color = db.Column(db.String(10), default='#007bff')  # Hex color
    text_color = db.Column(db.String(10), default='#ffffff')        # Hex color
    icon = db.Column(db.String(50), default='info-circle')  # Font awesome icon
    
    # CTA (Call To Action)
    cta_text = db.Column(db.String(100))  # Button text (optional)
    cta_url = db.Column(db.String(500))   # Button link (optional)
    
    # Analytics
    click_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    
    # Metadata
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])
    
    # Display order
    display_order = db.Column(db.Integer, default=0)
    
    @staticmethod
    def get_active_messages():
        """Get all active messages that should be displayed (respecting schedule)"""
        now = datetime.utcnow()
        return DynamicMessage.query.filter(
            DynamicMessage.is_active == True,
            (DynamicMessage.start_date == None) | (DynamicMessage.start_date <= now),
            (DynamicMessage.end_date == None) | (DynamicMessage.end_date >= now)
        ).order_by(DynamicMessage.display_order.asc()).all()
    
    @staticmethod
    def get_active_homepage_messages():
        """Get active messages for homepage"""
        return DynamicMessage.query.filter(
            DynamicMessage.is_active == True,
            (DynamicMessage.display_location.in_(['homepage', 'all_pages'])),
            (DynamicMessage.start_date == None) | (DynamicMessage.start_date <= datetime.utcnow()),
            (DynamicMessage.end_date == None) | (DynamicMessage.end_date >= datetime.utcnow())
        ).order_by(DynamicMessage.display_order.asc()).all()
    
    def increment_views(self):
        """Track message view"""
        self.view_count += 1
        db.session.commit()
    
    def increment_clicks(self):
        """Track CTA click"""
        self.click_count += 1
        db.session.commit()
    
    def is_scheduled(self):
        """Check if message is scheduled for future"""
        if self.start_date:
            return self.start_date > datetime.utcnow()
        return False
    
    def is_expired(self):
        """Check if message has expired"""
        if self.end_date:
            return self.end_date < datetime.utcnow()
        return False
    
    def is_currently_active(self):
        """Check if message is currently active and should display"""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True
    
    def __repr__(self):
        return f'<DynamicMessage title="{self.title}" type={self.message_type} active={self.is_active}>'


class ProductReview(db.Model):
    """Model for customer product reviews and ratings"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Review Content
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Moderation & Status
    is_approved = db.Column(db.Boolean, default=False)  # Admin must approve
    helpful_count = db.Column(db.Integer, default=0)  # Track if other users found it helpful
    
    # Metadata
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('product_reviews', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for query performance
    __table_args__ = (
        db.Index('idx_product_approved', 'product_id', 'is_approved'),
        db.Index('idx_user_product_review', 'user_id', 'product_id'),
        db.Index('idx_review_created_at', 'created_at'),
    )
    
    def approve(self, admin_user=None):
        """Approve review by admin"""
        self.is_approved = True
        db.session.commit()
    
    def reject(self):
        """Reject review (mark as not approved but keep record)"""
        self.is_approved = False
        db.session.commit()
    
    def mark_helpful(self):
        """Mark review as helpful"""
        self.helpful_count += 1
        db.session.commit()
    
    def is_by_verified_buyer(self):
        """Check if this is from a verified buyer"""
        # Check if user has an order containing this product
        from sqlalchemy import and_
        order = db.session.query(Order).join(OrderItem).filter(
            and_(
                Order.user_id == self.user_id,
                OrderItem.product_id == self.product_id,
                Order.status.in_(['delivered', 'shipped'])  # Only shipped/delivered orders count
            )
        ).first()
        return order is not None
    
    @staticmethod
    def get_product_reviews(product_id, approved_only=True, page=1, per_page=10, sort_by='recent'):
        """Get reviews for a product with pagination and sorting"""
        query = ProductReview.query.filter_by(product_id=product_id)
        
        if approved_only:
            query = query.filter_by(is_approved=True)
        
        # Sorting options
        if sort_by == 'helpful':
            query = query.order_by(ProductReview.helpful_count.desc())
        elif sort_by == 'rating_high':
            query = query.order_by(ProductReview.rating.desc())
        elif sort_by == 'rating_low':
            query = query.order_by(ProductReview.rating.asc())
        else:  # default 'recent'
            query = query.order_by(ProductReview.created_at.desc())
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_pending_reviews(page=1, per_page=20):
        """Get pending reviews for admin moderation"""
        return ProductReview.query.filter_by(is_approved=False).order_by(
            ProductReview.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_user_product_review(user_id, product_id):
        """Check if user already reviewed this product"""
        return ProductReview.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first()
    
    def get_rating_stars(self):
        """Get HTML star rating display"""
        full_stars = self.rating
        empty_stars = 5 - full_stars
        return '⭐' * full_stars + '☆' * empty_stars
    
    def __repr__(self):
        return f'<ProductReview Product#{self.product_id} by User#{self.user_id} rating={self.rating}/5>'


# ============================================================================
# PAYSTACK PAYMENT MODELS
# ============================================================================

class Payment(db.Model):
    """Paystack Payment Records"""
    __tablename__ = 'payment'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Order Reference
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    
    # Customer Information
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20))
    
    # Payment Details
    amount = db.Column(db.Float, nullable=False)  # In GHS
    currency = db.Column(db.String(3), default='GHS')
    
    # Paystack References
    paystack_reference = db.Column(db.String(100), unique=True, nullable=False)
    paystack_authorization_code = db.Column(db.String(100))
    paystack_customer_id = db.Column(db.Integer)
    
    # Payment Method (set after payment completes)
    payment_method = db.Column(db.String(50))  # card, mobile_money, bank_transfer, ussd
    
    # Status Tracking
    status = db.Column(
        db.String(50),
        default='pending'
    )  # pending, success, failed, abandoned
    
    status_reason = db.Column(db.String(255))  # Reason for failure
    
    # Timestamps
    initiated_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationship
    order = db.relationship('Order', backref='payment_record')
    logs = db.relationship('PaymentLog', backref='payment', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.paystack_reference}>'
    
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == 'success'
    
    def is_pending(self):
        """Check if payment is pending"""
        return self.status == 'pending'
    
    def is_failed(self):
        """Check if payment failed"""
        return self.status == 'failed'


class PaymentLog(db.Model):
    """Payment Transaction Audit Log"""
    __tablename__ = 'payment_log'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    
    # Action Details
    action = db.Column(db.String(100), nullable=False)  # initiated, verified, confirmed, failed, webhook_confirmed, webhook_failed
    details = db.Column(db.Text)  # Detailed information (can store JSON)
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PaymentLog {self.id} - {self.action}>'


# ============================================================================
# SMS MANAGEMENT MODELS (mNotify Integration)
# ============================================================================

class SMSTemplate(db.Model):
    """SMS message templates for common scenarios"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Template Info
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)  # order_confirm, shipping, delivery, verification, promotion, abandoned_cart, custom
    description = db.Column(db.Text)
    
    # Template Content
    content = db.Column(db.Text, nullable=False)  # Template with variables like {first_name}, {order_id}, etc.
    variables = db.Column(db.Text)  # JSON list of available variables: ["first_name", "order_id", "tracking_number"]
    
    # Status & Settings
    is_active = db.Column(db.Boolean, default=True)
    character_count = db.Column(db.Integer)  # Cached character count
    is_system_template = db.Column(db.Boolean, default=False)  # True for default templates
    
    # Metadata
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_variable_list(self):
        """Parse variables JSON"""
        import json
        try:
            return json.loads(self.variables) if self.variables else []
        except:
            return []
    
    def render(self, **variables):
        """Render template with provided variables"""
        content = self.content
        for key, value in variables.items():
            content = content.replace(f'{{{key}}}', str(value))
        return content
    
    def __repr__(self):
        return f'<SMSTemplate {self.name}>'


class SMSCampaign(db.Model):
    """Bulk SMS campaigns"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Campaign Info
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Content
    template_id = db.Column(db.Integer, db.ForeignKey('sms_template.id'))
    template = db.relationship('SMSTemplate', backref=db.backref('campaigns', lazy=True))
    custom_message = db.Column(db.Text)  # If not using template
    
    # Targeting
    recipient_filter = db.Column(db.String(50))  # all_users, verified_only, by_city, by_date_range, custom_list
    filter_data = db.Column(db.Text)  # JSON with filter parameters
    recipient_count = db.Column(db.Integer, default=0)  # Count of recipients
    
    # Status
    status = db.Column(db.String(50), default='draft')  # draft, scheduled, in_progress, completed, failed, cancelled
    
    # Scheduling
    scheduled_at = db.Column(db.DateTime)  # When to send (None = immediate)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Batch Configuration
    batch_size = db.Column(db.Integer, default=100)  # Messages per batch
    messages_sent = db.Column(db.Integer, default=0)
    messages_failed = db.Column(db.Integer, default=0)
    messages_delivered = db.Column(db.Integer, default=0)
    
    # Settings
    require_confirmation = db.Column(db.Boolean, default=True)  # Admin must confirm before bulk send
    retry_failed = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref=db.backref('sms_campaigns', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('SMSMessage', backref='campaign', lazy=True, cascade='all, delete-orphan')
    
    def get_filter_data(self):
        """Parse filter data JSON"""
        import json
        try:
            return json.loads(self.filter_data) if self.filter_data else {}
        except:
            return {}
    
    def get_status_badge(self):
        """Get Bootstrap badge class"""
        status_map = {
            'draft': 'secondary',
            'scheduled': 'info',
            'in_progress': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'dark'
        }
        return status_map.get(self.status, 'secondary')
    
    def get_delivery_rate(self):
        """Calculate delivery rate percentage"""
        if self.messages_sent == 0:
            return 0
        return round((self.messages_delivered / self.messages_sent) * 100, 1)
    
    @staticmethod
    def get_pending_sends():
        """Get campaigns pending to be sent"""
        from datetime import datetime as dt
        return SMSCampaign.query.filter(
            SMSCampaign.status.in_(['draft', 'scheduled']),
            (SMSCampaign.scheduled_at == None) | (SMSCampaign.scheduled_at <= dt.utcnow())
        ).all()
    
    def __repr__(self):
        return f'<SMSCampaign {self.name} - {self.status}>'


class SMSMessage(db.Model):
    """Individual SMS messages"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Campaign Reference
    campaign_id = db.Column(db.Integer, db.ForeignKey('sms_campaign.id'))
    
    # Recipient Info
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for non-user recipients
    user = db.relationship('User', backref=db.backref('sms_messages', lazy=True))
    phone_number = db.Column(db.String(20), nullable=False)
    recipient_name = db.Column(db.String(100))  # Cached name for logs
    
    # Message Content
    content = db.Column(db.Text, nullable=False)
    character_count = db.Column(db.Integer)  # SMS length (for cost calculation)
    sms_parts = db.Column(db.Integer, default=1)  # How many SMS needed (160 chars = 1 part)
    
    # mNotify Integration
    mnotify_message_id = db.Column(db.String(100), unique=True)  # mNotify API response ID
    mnotify_status_code = db.Column(db.String(50))  # mNotify response code
    
    # Delivery Status
    status = db.Column(db.String(50), default='pending')  # pending, sent, delivered, failed, bounced, read
    delivery_status_code = db.Column(db.String(50))  # mNotify delivery code
    delivery_error = db.Column(db.String(255))  # Error message if failed
    
    # Retry Tracking
    retry_count = db.Column(db.Integer, default=0)
    max_retries = db.Column(db.Integer, default=3)
    last_retry_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    failed_at = db.Column(db.DateTime)
    
    # Cost Tracking (from mNotify)
    cost = db.Column(db.Float, default=0)  # Cost in GHS
    
    def is_delivered(self):
        return self.status == 'delivered'
    
    def is_failed(self):
        return self.status == 'failed'
    
    def is_pending(self):
        return self.status == 'pending'
    
    def can_retry(self):
        """Check if message can be retried"""
        return self.is_failed() and self.retry_count < self.max_retries
    
    def get_status_badge(self):
        """Get Bootstrap badge for status"""
        status_map = {
            'pending': 'secondary',
            'sent': 'info',
            'delivered': 'success',
            'failed': 'danger',
            'bounced': 'warning',
            'read': 'success'
        }
        return status_map.get(self.status, 'secondary')
    
    def __repr__(self):
        return f'<SMSMessage to {self.phone_number} - {self.status}>'


class SMSLog(db.Model):
    """Audit log for SMS operations"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Operation Details
    action = db.Column(db.String(100), nullable=False)  # campaign_created, campaign_sent, message_sent, message_failed, campaign_cancelled, template_created, bulk_retry
    action_type = db.Column(db.String(50))  # campaign, message, template, system
    
    # Related Objects
    campaign_id = db.Column(db.Integer, db.ForeignKey('sms_campaign.id'), nullable=True)
    message_id = db.Column(db.Integer, db.ForeignKey('sms_message.id'), nullable=True)
    template_id = db.Column(db.Integer, db.ForeignKey('sms_template.id'), nullable=True)
    
    # User & Details
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin = db.relationship('User', foreign_keys=[admin_id], backref=db.backref('sms_logs', lazy=True))
    
    details = db.Column(db.Text)  # JSON details about the action
    message = db.Column(db.String(255))  # Human-readable message
    status = db.Column(db.String(50))  # success, warning, error
    
    # Metadata
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_status_icon(self):
        """Get icon for status"""
        icons = {
            'success': 'check-circle',
            'warning': 'alert-circle',
            'error': 'x-circle'
        }
        return icons.get(self.status, 'info')
    
    def __repr__(self):
        return f'<SMSLog {self.action} by admin#{self.admin_id}>'


class SMSBlacklist(db.Model):
    """Phone numbers to exclude from SMS"""
    id = db.Column(db.Integer, primary_key=True)
    
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    reason = db.Column(db.String(255))  # user_request, invalid_number, carrier_block, spam_complaint
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    added_by = db.relationship('User', foreign_keys=[added_by_id])
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def is_blacklisted(phone_number):
        """Check if phone number is blacklisted"""
        return SMSBlacklist.query.filter_by(phone_number=phone_number).first() is not None
    
    def __repr__(self):
        return f'<SMSBlacklist {self.phone_number}>'


class ContactSettings(db.Model):
    """Model for managing contact information and social media links"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Business Information
    business_name = db.Column(db.String(200), default='Digital Home Store')
    business_description = db.Column(db.Text, default='Your one-stop shop for all your needs.')
    
    # Contact Information
    email = db.Column(db.String(120), default='support@estore.com')
    phone = db.Column(db.String(20), default='+233 544765278')
    phone_whatsapp = db.Column(db.String(20))  # WhatsApp number
    address = db.Column(db.Text)  # Full address
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # Social Media Links
    facebook_url = db.Column(db.String(255))
    twitter_url = db.Column(db.String(255))
    instagram_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    youtube_url = db.Column(db.String(255))
    tiktok_url = db.Column(db.String(255))
    telegram_url = db.Column(db.String(255))
    
    # Operating Hours
    opening_time = db.Column(db.String(10), default='08:00')  # HH:MM format
    closing_time = db.Column(db.String(10), default='18:00')  # HH:MM format
    timezone = db.Column(db.String(50), default='Africa/Accra')
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])
    
    @staticmethod
    def get_settings():
        """Get or create default contact settings"""
        settings = ContactSettings.query.first()
        if not settings:
            settings = ContactSettings()
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def update_contact_info(self, business_name, business_description, email, phone, 
                           phone_whatsapp, address, city, country, postal_code, user_id):
        """Update contact information"""
        self.business_name = business_name
        self.business_description = business_description
        self.email = email
        self.phone = phone
        self.phone_whatsapp = phone_whatsapp
        self.address = address
        self.city = city
        self.country = country
        self.postal_code = postal_code
        self.updated_by_id = user_id
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_social_media(self, facebook, twitter, instagram, linkedin, youtube, tiktok, telegram, user_id):
        """Update social media links"""
        self.facebook_url = facebook
        self.twitter_url = twitter
        self.instagram_url = instagram
        self.linkedin_url = linkedin
        self.youtube_url = youtube
        self.tiktok_url = tiktok
        self.telegram_url = telegram
        self.updated_by_id = user_id
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_operating_hours(self, opening_time, closing_time, timezone, user_id):
        """Update operating hours"""
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.timezone = timezone
        self.updated_by_id = user_id
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_active_social_links(self):
        """Get only the social media links that are configured"""
        links = {}
        if self.facebook_url:
            links['facebook'] = self.facebook_url
        if self.twitter_url:
            links['twitter'] = self.twitter_url
        if self.instagram_url:
            links['instagram'] = self.instagram_url
        if self.linkedin_url:
            links['linkedin'] = self.linkedin_url
        if self.youtube_url:
            links['youtube'] = self.youtube_url
        if self.tiktok_url:
            links['tiktok'] = self.tiktok_url
        if self.telegram_url:
            links['telegram'] = self.telegram_url
        return links
    
    def __repr__(self):
        return f'<ContactSettings {self.business_name}>'