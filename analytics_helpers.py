"""Analytics helpers for dashboard statistics and data processing"""
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app import db
from models import Order, OrderItem, Product, User, Category

def get_sales_trends(days=30):
    """
    Get daily sales data for the last N days.
    
    Args:
        days (int): Number of days to retrieve
        
    Returns:
        dict: Daily sales data with dates and amounts
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query daily sales (only paid, non-cancelled orders)
    daily_sales = db.session.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('orders'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        and_(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status != 'cancelled',
            Order.payment_status == 'paid'
        )
    ).group_by(
        func.date(Order.created_at)
    ).order_by(
        func.date(Order.created_at)
    ).all()
    
    # Format data
    data = {
        'dates': [],
        'orders': [],
        'revenue': []
    }
    
    for item in daily_sales:
        date_str = item.date if isinstance(item.date, str) else item.date.strftime('%b %d')
        data['dates'].append(date_str)
        data['orders'].append(item.orders or 0)
        data['revenue'].append(float(item.revenue or 0))
    
    return data


def get_top_products(limit=10):
    """
    Get top products by revenue and units sold.
    
    Args:
        limit (int): Number of products to retrieve
        
    Returns:
        list: Top products with revenue and unit data
    """
    top_by_revenue = db.session.query(
        Product,
        func.sum(OrderItem.quantity).label('units_sold'),
        func.sum(OrderItem.total_price).label('total_revenue')
    ).join(
        OrderItem
    ).join(
        Order
    ).filter(
        and_(
            Order.status != 'cancelled',
            Order.payment_status == 'paid'
        )
    ).group_by(
        Product.id
    ).order_by(
        func.sum(OrderItem.total_price).desc()
    ).limit(limit).all()
    
    return [
        {
            'product': item[0],
            'units_sold': int(item[1] or 0),
            'total_revenue': float(item[2] or 0)
        }
        for item in top_by_revenue
    ]


def get_customer_demographics():
    """
    Get customer demographic statistics.
    
    Returns:
        dict: Customer statistics and counts
    """
    total_users = User.query.count()
    active_users = User.query.filter(User.is_active == True).count()
    verified_users = User.query.filter(User.is_verified == True).count()
    
    # Users by activity (have they placed orders?)
    users_with_orders = db.session.query(
        func.count(func.distinct(Order.user_id))
    ).filter(Order.status != 'cancelled').scalar() or 0
    
    users_without_orders = total_users - users_with_orders
    
    # Average orders per customer (total orders / users with orders)
    total_orders = db.session.query(
        func.count(Order.id)
    ).filter(
        and_(
            Order.status != 'cancelled',
            Order.payment_status == 'paid'
        )
    ).scalar() or 0
    
    avg_orders_per_customer = total_orders / users_with_orders if users_with_orders > 0 else 0
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'verified_users': verified_users,
        'users_with_orders': int(users_with_orders),
        'users_without_orders': users_without_orders,
        'avg_orders_per_customer': round(float(avg_orders_per_customer), 2)
    }


def get_conversion_funnel():
    """
    Get conversion funnel data.
    
    Returns:
        dict: Funnel stages with conversion rates
    """
    total_users = User.query.count()
    
    users_viewed_products = db.session.query(
        func.count(func.distinct(User.id))
    ).filter(User.created_at.isnot(None)).scalar() or 0
    
    users_added_to_cart = db.session.query(
        func.count(func.distinct(OrderItem.id))
    ).scalar() or 0
    
    users_completed_order = db.session.query(
        func.count(func.distinct(Order.user_id))
    ).filter(
        and_(
            Order.status != 'cancelled',
            Order.payment_status == 'paid'
        )
    ).scalar() or 0
    
    # Calculate conversion rates
    view_to_cart = (users_added_to_cart / total_users * 100) if total_users > 0 else 0
    cart_to_order = (users_completed_order / users_added_to_cart * 100) if users_added_to_cart > 0 else 0
    overall_conversion = (users_completed_order / total_users * 100) if total_users > 0 else 0
    
    return {
        'stages': {
            'total_users': total_users,
            'viewed_products': int(users_viewed_products),
            'added_to_cart': int(users_added_to_cart),
            'completed_order': int(users_completed_order)
        },
        'conversion_rates': {
            'view_to_cart': round(view_to_cart, 2),
            'cart_to_order': round(cart_to_order, 2),
            'overall_conversion': round(overall_conversion, 2)
        }
    }


def get_revenue_by_category(limit=10):
    """
    Get revenue breakdown by product category.
    
    Args:
        limit (int): Number of categories to retrieve
        
    Returns:
        list: Categories sorted by revenue
    """
    revenue_by_cat = db.session.query(
        Category,
        func.sum(OrderItem.total_price).label('category_revenue'),
        func.sum(OrderItem.quantity).label('units_sold')
    ).join(
        Product, Product.category_id == Category.id
    ).join(
        OrderItem, OrderItem.product_id == Product.id
    ).join(
        Order, Order.id == OrderItem.order_id
    ).filter(
        and_(
            Order.status != 'cancelled',
            Order.payment_status == 'paid'
        )
    ).group_by(
        Category.id
    ).order_by(
        func.sum(OrderItem.total_price).desc()
    ).limit(limit).all()
    
    return [
        {
            'category': item[0],
            'revenue': float(item[1] or 0),
            'units_sold': int(item[2] or 0)
        }
        for item in revenue_by_cat
    ]


def get_order_status_breakdown():
    """
    Get breakdown of orders by status.
    
    Returns:
        dict: Order counts by status
    """
    status_counts = db.session.query(
        Order.status,
        func.count(Order.id).label('count')
    ).group_by(
        Order.status
    ).all()
    
    return {
        item[0]: item[1]
        for item in status_counts
    }


def get_monthly_trends(months=12):
    """
    Get monthly sales trends.
    
    Args:
        months (int): Number of months to retrieve
        
    Returns:
        dict: Monthly sales and revenue data
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months*30)
    
    monthly_sales = db.session.query(
        func.strftime('%Y-%m', Order.created_at).label('month'),
        func.count(Order.id).label('orders'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        and_(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status != 'cancelled',
            Order.payment_status == 'paid'
        )
    ).group_by(
        func.strftime('%Y-%m', Order.created_at)
    ).order_by(
        func.strftime('%Y-%m', Order.created_at)
    ).all()
    
    data = {
        'months': [],
        'orders': [],
        'revenue': []
    }
    
    for item in monthly_sales:
        if item.month:
            # Format month display (item.month is already a string from strftime)
            if isinstance(item.month, str):
                month_display = item.month  # Already formatted as 'Mar 2025' or similar
            else:
                month_obj = datetime.strptime(str(item.month), '%Y-%m')
                month_display = month_obj.strftime('%b %Y')
            
            data['months'].append(month_display)
            data['orders'].append(item.orders or 0)
            data['revenue'].append(float(item.revenue or 0))
    
    return data
